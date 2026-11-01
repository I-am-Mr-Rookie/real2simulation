"""N04 on-demand GPU service: one deployed Modal app wrapping the existing GPU functions.

reconstruct(frames): S06d MapAnything room reconstruction (Build/gpu/scene_job.py body, unchanged).
track(...): S07b SAM 3.1 backup tracker (Build/measurement/runtime/modal_track.py track_one, unchanged).
Each: min_containers=0, max_containers=1, scaledown_window=900 (sleep after 15 idle minutes). Modal pools are
per function, so callers MUST go through Build/api/gpu enqueue -> start (blocks until head of the one shared
queue) -> remote -> finish: at most one job of either kind runs at a time. Residual: the other function's
container may still be warm-idle (billed) up to 900 s after its job; callers reserve that idle window.
Empty frames to reconstruct = warm-up only (no model load, no output).

Deploy: uv run --python 3.12 --with modal==1.6.3 --env-file .env modal deploy Build/gpu/ondemand.py
Paid callers reserve/settle via Build/guardrails/daily_cap.py; status: Build/api/gpu (GET .../gpu/status).
"""
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
for p in (HERE, HERE.parent / "measurement" / "runtime"):  # local only; in the container all sources sit in /root
    if p.is_dir():
        sys.path.insert(0, str(p))

import modal
import modal_track
import scene_job

SOURCES = ("ondemand", "scene_job", "runtime", "image_spec", "modal_image", "modal_track")
ONDEMAND = {"min_containers": 0, "max_containers": 1, "buffer_containers": 0, "scaledown_window": 900, "retries": 0}
app = modal.App("r2s-ondemand")


@app.function(image=scene_job.RUNTIME_IMAGE.add_local_python_source(*SOURCES), gpu=scene_job.s.GPU,
              cpu=scene_job.CPU, memory=scene_job.MEM_MIB, timeout=300, startup_timeout=240, **ONDEMAND)
def reconstruct(frames):
    if not frames:
        return {"warmup": True, "container_start_epoch": scene_job.CONTAINER_START, "function_epoch": time.time()}
    return scene_job.scene_job.local(frames)  # runs the S06d body in this container's process


@app.function(image=modal_track.image.add_local_python_source(*SOURCES),
              **{**modal_track.GPU_KW, "single_use_containers": False, **ONDEMAND})
def track(frames, metadata, frame_map, prompt, object_id=modal_track.OBJECT_ID, masks=False, chunk=0):
    return modal_track.track_one(frames, metadata, frame_map, prompt, object_id, masks, chunk)
