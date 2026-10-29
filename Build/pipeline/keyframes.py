"""S13c keyframes stage: ffprobe metadata + ffmpeg keyframe extraction with original timestamps.

Times come from ffprobe per-frame pts (best_effort_timestamp fallback) in the stream timebase,
never frame_index/fps, so VFR clips and nonzero start offsets keep their original times.
Provenance is copied from the clip's clips.csv licence row. Local only; no network or spend.
Usage: python -m Build.pipeline.keyframes CLIP_ID CLIP_PATH OUT_DIR [CLIPS_CSV]
"""
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from Build.pipeline.contracts import POLICY, ROOT
from Build.pipeline.uploads import UploadError

PROVENANCE = ("clip_id", "title", "source_url", "creator", "licence", "licence_url",
              "attribution", "adaptation_notes", "status", "owner_approved")
_BANNED = ("NC", "ND", "NONCOMMERCIAL", "NODERIVATIVES")


def _run(args):
    p = subprocess.run(args, capture_output=True, text=True)
    if p.returncode:
        # shortcut: every ffmpeg/ffprobe failure is INVALID_INPUT (never_retry); split out IO/transient codes in S13d.
        raise UploadError("INVALID_INPUT", f"{args[0]} failed: {p.stderr.strip()[-300:]}")
    return p.stdout


def _probe(path, *extra):
    return json.loads(_run(["ffprobe", "-v", "error", "-select_streams", "v:0", *extra, "-of", "json", str(path)]))


def _num(v):
    return None if v in (None, "N/A") else float(v)


def provenance(clip_id, path, clips_csv=ROOT / "clips.csv"):
    """Licence row for clip_id; rejects missing/unlicensed/NC/ND rows and a path that is not the row's file."""
    clips_csv = Path(clips_csv)
    with open(clips_csv, encoding="utf-8", newline="") as f:
        row = next((r for r in csv.DictReader(f) if r["clip_id"] == clip_id), None)
    if row is None:
        raise UploadError("INVALID_INPUT", f"{clip_id} not in {clips_csv.name}")
    lic = (row["licence"] or "").strip()
    if not lic or any(t in lic.upper().replace("-", " ").split() for t in _BANNED):
        raise UploadError("INVALID_INPUT", f"{clip_id} licence not usable: {lic!r}")
    if row["local_path"] and (clips_csv.parent / row["local_path"]).resolve() != Path(path).resolve():
        raise UploadError("INVALID_INPUT", f"{path} is not {clip_id} local_path {row['local_path']}")
    return {k: row.get(k, "") for k in PROVENANCE}


def metadata(path):
    """Container/stream facts from ffprobe; enforces the policy duration limit."""
    info = _probe(path, "-show_entries",
                  "format=format_name,duration,start_time:stream=codec_name,width,height,"
                  "time_base,r_frame_rate,avg_frame_rate,start_time,duration,nb_frames")
    if not info.get("streams"):
        raise UploadError("INVALID_INPUT", "no video stream")
    s, fmt = info["streams"][0], info["format"]
    duration = _num(fmt.get("duration")) or _num(s.get("duration"))
    if duration is None or duration > POLICY["upload"]["max_duration_s"]:
        raise UploadError("INVALID_INPUT", f"duration {duration} s outside policy")
    return {"format_name": fmt.get("format_name"), "duration_s": duration,
            "start_time_s": _num(s.get("start_time")), "codec": s.get("codec_name"),
            "width": s.get("width"), "height": s.get("height"), "time_base": s.get("time_base"),
            "r_frame_rate": s.get("r_frame_rate"), "avg_frame_rate": s.get("avg_frame_rate"),
            "nb_frames": s.get("nb_frames"),
            # r != avg is only a VFR hint; timestamps never rely on either rate.
            "vfr_hint": s.get("r_frame_rate") != s.get("avg_frame_rate")}


def keyframe_times(path):
    """Original presentation times of decoded keyframes, in decode output order."""
    frames = _probe(path, "-skip_frame", "nokey", "-show_entries",
                    "frame=pts,pts_time,best_effort_timestamp,best_effort_timestamp_time,pict_type")["frames"]
    out = []
    for fr in frames:
        src = "pts" if _num(fr.get("pts_time")) is not None else "best_effort_timestamp"
        t = _num(fr.get(src + "_time"))
        if t is None:
            raise UploadError("INVALID_INPUT", "keyframe without pts or best_effort_timestamp")
        out.append({"pts": int(fr[src]), "time_s": t, "time_source": src, "pict_type": fr.get("pict_type")})
    return out


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def extract(clip_id, path, out_dir, clips_csv=ROOT / "clips.csv"):
    """Write kf_NNNNNN.jpg + manifest.json to out_dir; returns the manifest dict."""
    prov = provenance(clip_id, path, clips_csv)
    meta = metadata(path)
    times = keyframe_times(path)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    if any(out.glob("kf_*.jpg")):
        raise UploadError("INVALID_INPUT", "out_dir already has keyframes")  # no stale-frame mixing
    # Same -skip_frame nokey decode as keyframe_times; passthrough = no dup/drop, so order matches.
    _run(["ffmpeg", "-v", "error", "-nostdin", "-skip_frame", "nokey", "-i", str(path), "-map", "0:v:0",
          "-fps_mode", "passthrough", "-q:v", "2", str(out / "kf_%06d.jpg")])
    files = sorted(out.glob("kf_*.jpg"))
    if len(files) != len(times):
        raise UploadError("INVALID_INPUT", f"ffmpeg wrote {len(files)} frames, ffprobe saw {len(times)}")
    manifest = {"contract_version": "1.0.0", "kind": "keyframe_manifest", "stage": "keyframes",
                "provenance": prov,
                "source": {"file": Path(path).name, "sha256": _sha256(path), **meta},
                "keyframes": [{"index": i, "file": f.name, **t} for i, (f, t) in enumerate(zip(files, times))]}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    m = extract(*sys.argv[1:5])
    print(json.dumps({"clip_id": m["provenance"]["clip_id"], "licence": m["provenance"]["licence"],
                      "keyframes": len(m["keyframes"]), "times_s": [k["time_s"] for k in m["keyframes"]][:10],
                      **{k: m["source"][k] for k in ("duration_s", "start_time_s", "avg_frame_rate", "vfr_hint")}}))
