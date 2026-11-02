"""Time only public RM02 frame sampling; does not upload or invoke a model."""
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from Build.reconstruction import live_room

video, output = map(Path, sys.argv[1:])
duration = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(video)], capture_output=True, text=True, check=True).stdout)
start = time.perf_counter()
frames = live_room.sample_frames(video, duration)
summary = {"label": "MEASURED local public RM02 frame sampling only; no upload or model call",
           "sampling_s": time.perf_counter() - start, "frames": len(frames),
           "png_sha256": [hashlib.sha256(frame).hexdigest() for frame in frames]}
output.write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps({k: v for k, v in summary.items() if k != "png_sha256"}))
