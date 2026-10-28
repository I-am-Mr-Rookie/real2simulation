"""Verify local research custody, not physical calibration. Standard library only."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent
entries = json.loads((root / "candidates.json").read_text(encoding="utf-8"))["candidates"]
json_files = list(root.rglob("*.json"))
for path in json_files:
    json.loads(path.read_text(encoding="utf-8-sig"))

inventory = []
for candidate in entries:
    assert not candidate["metric_qualified"]
    assert candidate["physical_capture_fps"] is None
    assert candidate["scale_m_per_pixel"] is None
    assert not candidate["owner_final_use_approved"]
    for name in candidate["renditions"]:
        path = root / "media" / name
        data = path.read_bytes()
        assert data
        receipt = {"file": "media/" + name, "bytes": len(data),
                   "sha256": hashlib.sha256(data).hexdigest(),
                   "sha1": hashlib.sha1(data).hexdigest()}
        check = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(path),
                                "-map", "0:v:0", "-f", "null", "-"], capture_output=True, text=True)
        receipt["decode_exit"] = check.returncode
        receipt["decode_stderr"] = check.stderr
        assert check.returncode == 0 and not check.stderr, receipt
        inventory.append(receipt)

api = json.loads((root / "sources/orion-videoinfo.json").read_text(encoding="utf-8-sig"))
info = next(iter(api["query"]["pages"].values()))["videoinfo"][0]
orion = next(x for x in inventory if "orion" in x["file"])
assert (orion["bytes"], orion["sha1"]) == (info["size"], info["sha1"])

segments = []
for ident, ranges in [("N01", [(1000, 1047), (1150, 1209), (1200, 1247)]),
                      ("N01-medium", [(2398, 2445)]),
                      ("N02", [(560, 607), (660, 755), (660, 695)])]:
    frames = json.loads((root / f"{ident}-frame-pts.json").read_text(encoding="utf-8-sig"))["frames"]
    pts = [float(x["best_effort_timestamp_time"]) for x in frames]
    assert all(b > a for a, b in zip(pts, pts[1:])), ident
    for start, end in ranges:
        segments.append({"rendition": ident, "zero_based_first": start, "zero_based_last": end,
                         "frame_count": end - start + 1, "first_pts_s": pts[start],
                         "last_pts_s": pts[end], "physical_time_mapping": None})

hashes = [line.split(",")[-1].strip() for line in (root / "N02-framemd5.txt").read_text().splitlines()
          if line and not line.startswith("#")]
adjacent_duplicates = sum(a == b for a, b in zip(hashes, hashes[1:]))
qualified = sum(x["metric_qualified"] for x in entries)
result = {"verification_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
          "custody_checks": "PASS", "parsed_json_files": len(json_files),
          "inventory": inventory, "inspected_native_windows": segments,
          "orion_decoded_frames": len(hashes), "orion_exact_adjacent_duplicate_frames": adjacent_duplicates,
          "orion_original_api_sha1_and_size": "MATCH", "new_metric_qualified": qualified,
          "physical_acceptance": "FAIL: no qualified additions; no inference from delivered fps"}
(root / "verification.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
if "--require-qualified" in sys.argv:
    sys.exit(0 if qualified else 1)
