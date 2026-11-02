"""Extract only public RM02 timing/cost evidence from N47's existing receipts. No network or paid calls."""
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path


def stamp(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


src, output = map(Path, sys.argv[1:])
status = json.loads((src / "new-room-status.json").read_text())["job"]
shell = json.loads((src / "new-room-result.json").read_text())["room"]["shell"]
rows = json.loads((src / "runtime-ledger-window.json").read_text())
by_id = {row["id"]: row for row in rows}
gpu_done = stamp(by_id[status["gpu_attempts"][-1]["reservation_id"]]["settled_at"])
end = stamp(status["updated_at"]) + timedelta(seconds=1)
sam = [r for r in rows if "sam-3.1 image" in r["label"] and gpu_done <= stamp(r["reserved_at"]) < end]
shapes = [r for r in rows if r["label"] == "N31 sf3d" and gpu_done <= stamp(r["reserved_at"]) < end]
assert len(sam) == shell["sam_calls"] and len(shapes) == 3
sam_first, sam_last = min(stamp(r["reserved_at"]) for r in sam), max(stamp(r["settled_at"]) for r in sam)
summary = {
    "label": "RECORDED public N47 RM02-trim DEV job; estimates are not provider bills",
    "total_status_s": (stamp(status["updated_at"]) - stamp(status["created_at"])).total_seconds(),
    "status_timestamp_resolution_s": 1,
    "frames": status["frames"],
    "upload_s": None,
    "gpu_attempts": [{k: a[k] for k in ("gpu", "wall_s", "estimated_usd")} for a in status["gpu_attempts"]],
    "successful_gpu_timing_s": status["timing_s"],
    "sam_calls": len(sam),
    "sam_wall_s": (sam_last - sam_first).total_seconds(),
    "sam_call_duration_sum_s": sum((stamp(r["settled_at"]) - stamp(r["reserved_at"])).total_seconds() for r in sam),
    "post_sam_to_first_sf3d_s": (min(stamp(r["reserved_at"]) for r in shapes) - sam_last).total_seconds(),
    "sf3d_calls": [{"wall_s": (stamp(r["settled_at"]) - stamp(r["reserved_at"])).total_seconds(),
                    "estimated_usd": r["actual"] / 1e8} for r in shapes],
    "mask_decode_validation_s": None,
    "lift_s": None,
    "shell_save_s": None,
}
output.write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary))
