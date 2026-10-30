"""Offline audit of committed tracking PTS. Never rewrites accepted evidence.

Run from any directory: python audit.py <canonical-media-root> [--self-check]
Full-stream ffprobe deliberately avoids the packet-limited method under audit.
"""
import csv
import hashlib
import json
import math
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent


def pairs(value, at=""):
    """Keep JSON pointers so duplicate map/record timestamps are both audited."""
    if isinstance(value, dict):
        if "frame_index" in value and "pts_s" in value:
            yield at + "/pts_s", value["frame_index"], float(value["pts_s"])
        if "source_frame_index" in value and "pts_time" in value:
            yield at + "/pts_time", value["source_frame_index"], float(value["pts_time"])
        for key, child in value.items():
            if key == "differences":  # intentionally preserves recorded wrong values
                continue
            if key in ("frame_map", "trace") and isinstance(child, list):
                for i, row in enumerate(child):
                    if isinstance(row, list) and len(row) >= 2:
                        yield f"{at}/{key}/{i}/1", row[0], float(row[1])
            else:
                yield from pairs(child, at + "/" + key)
    elif isinstance(value, list):
        for i, child in enumerate(value):
            yield from pairs(child, at + f"/{i}")


def differences(rows, pts):
    result = []
    for pointer, index, recorded in rows:
        if type(index) is not int or not 0 <= index < len(pts) or not math.isfinite(recorded):
            raise ValueError(f"invalid frame/PTS at {pointer}: {index}, {recorded}")
        if abs(recorded - pts[index]) > 0.000001:
            result.append({"pointer": pointer, "frame_index": index,
                           "recorded_pts_s": recorded, "corrected_pts_s": pts[index]})
    return result


def self_check():
    doc = {"frame_map": [[0, 0], [1, .08]],
           "record": {"frames": [{"frame_index": 1, "pts_s": .08}]},
           "differences": [{"frame_index": 1, "pts_s": .99}]}
    bad = differences(list(pairs(doc)), [0, .04])
    assert len(bad) == 2 and {b["frame_index"] for b in bad} == {1}
    assert differences(list(pairs({"trace": [[1, .04, 7, 8]]})), [0, .04]) == []
    for index, pts in [(2, .04), (1, float("nan")), (-1, .04)]:
        try:
            differences([("/bad", index, pts)], [0, .04])
        except ValueError:
            pass
        else:
            raise AssertionError("invalid timestamp accepted")
    print("audit self-check PASS")


def run(media_root):
    tracked = subprocess.check_output(["git", "ls-files", "evidence"], cwd=ROOT, text=True).splitlines()
    # Only historical inputs: exclude this audit when it is later committed/replayed.
    tracked = [p for p in tracked if not p.startswith(OUT.relative_to(ROOT).as_posix() + "/")]
    base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    with (ROOT / "clips.csv").open(encoding="utf-8", newline="") as stream:
        clips = {r["clip_id"]: r for r in csv.DictReader(stream)}
    acquisition = json.loads((ROOT / "evidence/clips/S02c-acquisition.json").read_text())
    expected = {r["clip_id"]: r for r in acquisition["files"]}
    sources, presentation, ticks = {}, {}, {}
    for clip in ("ST03", "RM04"):
        row, pinned = clips[clip], expected[clip]
        assert row["local_path"] == pinned["local_path"]
        assert row["source_url"] == pinned["source_url"]
        path = media_root / row["local_path"]
        with path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        assert digest == pinned["sha256"], f"source hash mismatch: {clip}"
        command = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                   "frame=pts,pts_time:stream=time_base,has_b_frames", "-of", "json", str(path)]
        probe = json.loads(subprocess.check_output(command, text=True))
        pts = [float(f["pts_time"]) for f in probe["frames"]]
        assert pts and all(math.isfinite(p) for p in pts)
        assert all(a < b for a, b in zip(pts, pts[1:]))
        presentation[clip] = pts
        ticks[clip] = [f["pts"] for f in probe["frames"]]
        sources[clip] = {"source": row["local_path"], "source_sha256": digest,
                         "hash_verified": True, "hash_reference": "evidence/clips/S02c-acquisition.json",
                         "clips_csv_note": "clips.csv has paths/rights but no SHA column; acquisition record pins SHA",
                         "source_url": row["source_url"], "licence": row["licence"],
                         "frame_count": len(pts), "stream": probe["streams"][0], "command": command}
        (OUT / f"{clip}-full-presentation.json").write_text(json.dumps(probe, indent=2) + "\n")
    entries, candidates, invalid_json = [], [], []
    for rel in tracked:
        path = ROOT / rel
        if path.suffix.lower() not in (".json", ".jsonl", ".csv"):
            continue
        raw = path.read_bytes()
        if path.suffix == ".csv":
            header = raw.decode("utf-8-sig").splitlines()[0].lower()
            if any(k in header for k in ("pts", "frame", "time")):
                candidates.append({"file": rel, "classification": "independent research/acquisition CSV, not modal_track output", "header": header})
            continue
        try:
            docs = [json.loads(raw)] if path.suffix == ".json" else [json.loads(line) for line in raw.splitlines() if line.strip()]
        except (ValueError, UnicodeError) as exc:
            invalid_json.append({"file": rel, "reason": str(exc)})
            continue
        for doc in docs:
            text = raw.decode("utf-8-sig")
            if not any(k in text for k in ('"frame_map"', '"pts_s"', '"pts_time"', '"time_s"', '"trace"', '"file_time_s"')):
                continue
            rows = list(pairs(doc))
            relevant = rel.startswith(("evidence/S07/", "evidence/S12/", "evidence/S13/"))
            if not relevant or not rows or "SYNTHETIC" in rel:
                candidates.append({"file": rel, "classification": "not modal_track PTS output (independent research, synthetic, scene index time, or reference-only)", "extracted_pairs": len(rows)})
                continue
            clip = doc.get("clip_id") or doc.get("record", {}).get("clip_id")
            if not clip:
                clip = "RM04" if "RM04" in rel else "ST03" if ("ST03" in rel or "/S07b/" in rel) else None
            assert clip in presentation, f"unclassified tracking output: {rel}"
            for meta in (doc, doc.get("record", {}), doc.get("adapter_metadata", {})):
                if meta.get("source_sha256"):
                    assert meta["source_sha256"] == sources[clip]["source_sha256"], rel
            # Recovery custody maps retain integer ticks as well as rendered seconds.
            for frame in doc.get("frames", []) + doc.get("prefix", []):
                if "source_frame_index" in frame and "pts" in frame:
                    assert frame["pts"] == ticks[clip][frame["source_frame_index"]], rel
            if "first_suffix_pts_time" in doc:
                assert abs(float(doc["first_suffix_pts_time"]) - presentation[clip][doc["suffix_first_frame"]]) <= 1e-6
            bad = differences(rows, presentation[clip])
            entry = {"file": rel, "sha256": hashlib.sha256(raw).hexdigest(), "clip_id": clip,
                     "status": "WRONG" if bad else "OK", "timestamp_occurrences": len(rows),
                     "unique_frames": len({r[1] for r in rows}), "differences": bad}
            if bad:
                fmap = [[i, presentation[clip][i]] for i in sorted({r[1] for r in rows})]
                name = rel.removeprefix("evidence/").removesuffix(".json").replace("/", "--") + "-frame_map.json"
                errata = {"errata_for": rel, "original_sha256": entry["sha256"], "clip_id": clip,
                          "source": sources[clip]["source"], "source_sha256": sources[clip]["source_sha256"],
                          "source_hash_verified": True, "run": "S07-pts-audit-orch58",
                          "method": "full-stream ffprobe presentation frames; no read_intervals packet limit",
                          "differences": bad, "frame_map": fmap,
                          "scope": "PTS-only correction; does not validate tracking, calibration, or physical gates"}
                (OUT / name).write_text(json.dumps(errata, indent=2) + "\n")
                entry["errata"] = (OUT / name).relative_to(ROOT).as_posix()
            entries.append(entry)
    result = {"run": "S07-pts-audit-orch58", "generated_utc": datetime.now(timezone.utc).isoformat(),
              "base_commit": base, "tracked_evidence_files_scanned": len(tracked),
              "ffprobe_version": subprocess.check_output(["ffprobe", "-version"], text=True).splitlines()[0],
              "sources": sources, "tolerance_s": 1e-6, "results": entries,
              "counts": dict(Counter(e["status"] for e in entries)),
              "excluded_timestamp_candidates": candidates, "non_json_named_json": invalid_json}
    (OUT / "audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"scanned": len(tracked), "counts": result["counts"],
                      "wrong": [{"file": e["file"], "frames": sorted({b["frame_index"] for b in e["differences"]})}
                                for e in entries if e["status"] == "WRONG"]}, indent=2))


if __name__ == "__main__":
    if "--self-check" in sys.argv:
        self_check()
    else:
        run(Path(sys.argv[1]).resolve())
