"""N49 live run: RM02.mp4 (Pexels classroom, public) -> live_room.run_job (16 frames, MapAnything on Modal L4, A10G
fallback) -> automatic lab shell (hosted SAM 3.1, 16 keyframes, no SF3D) -> evidence/N49/live/rm02.json (numbers only).
Paid calls are reserved/settled in the daily_cap ledger under R2S_DATA_DIR.

uv run --python 3.12 --with modal==1.6.3 --with numpy --with fastapi --with httpx --with python-multipart \
  --with jsonschema --with pillow --env-file <root>/.env python evidence/N49/live_rm02.py <video> <data_dir>
"""
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from Build.api.room.objects import build_shell_files  # noqa: E402
from Build.reconstruction import live_room, object_lift  # noqa: E402

video, data = Path(sys.argv[1]), Path(sys.argv[2])
d = data / "rooms" / "user_n49live" / "rm02"
d.mkdir(parents=True, exist_ok=True)
cap, gpu_db = data / "spend.sqlite3", data / "gpu.sqlite3"
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
                           capture_output=True, text=True, check=True).stdout)
t = {}


def after(job):
    t0 = time.time()
    build_shell_files(job, lambda png, noun, w, h: object_lift.sam_text(png, noun, w, h, cap_path=cap), generate=None)
    t["shell_s"] = round(time.time() - t0, 1)


t0 = time.time()
live_room.run_job(d, video, dur, "user_n49live", gpu_db=gpu_db, cap_db=cap, after=after)
st = json.loads((d / "status.json").read_text())
room = json.loads((d / "room.json").read_text())
sh = room.get("shell", {})
scene = json.loads((d / "scene.json").read_text())
res = {"label": "RM02.mp4 Pexels classroom; geometry MODEL-ESTIMATED; " + room["scale"]["status"], "total_s": round(time.time() - t0, 1),
       "status": {k: st.get(k) for k in ("state", "gpu", "gpu_name", "peak_allocated_bytes", "timing_s", "estimated_usd", "frames",
                                          "gpu_attempts", "shell", "shell_error", "error")}, "shell_s": t.get("shell_s"),
       "views": room["views"], "floor": room["floor"], "sam_calls": sh.get("sam_calls"), "sam_cost_usd": sh.get("sam_cost_usd"),
       "walls": [{k: w.get(k) for k in ("axis", "side", "plane", "status", "reason")} for w in sh.get("walls", [])],
       "openings": [{k: o.get(k) for k in ("noun", "wall", "along", "y", "views")} for o in sh.get("openings", [])],
       "kept": [{k: x.get(k) for k in ("id", "category", "views", "size_m")} for x in sh.get("kept", [])],
       "dropped": sh.get("dropped"), "dropped_reasons": sh.get("dropped_reasons"), "detections": sh.get("detections"),
       "objects": len(scene["objects"])}
(HERE / "live").mkdir(exist_ok=True)
(HERE / "live" / "rm02.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
print(json.dumps(res)[:3000])

