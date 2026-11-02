"""Offline, public RM02 replay. Existing N52 SAM replies; no network, GPU, or private data.

Usage: python evidence/N53/replay.py SOURCE_JOB SAM_CACHE OUTPUT.json
"""
import hashlib
import io
import json
import sys
import threading
import time
from pathlib import Path
from unittest.mock import patch

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from Build.reconstruction import live_room, object_lift, room_shell
from Build.measurement import hosted_sam


def main():
    src, cache, output = map(Path, sys.argv[1:])
    totals, lock = {}, threading.Lock()

    def timed(name, fn):
        def run(*a, **kw):
            start = time.perf_counter()
            try:
                return fn(*a, **kw)
            finally:
                with lock:
                    totals[name] = totals.get(name, 0) + time.perf_counter() - start
        return run

    def detect(png, noun, w, h):
        key = hashlib.sha256(f"{w}x{h}".encode() + Image.open(io.BytesIO(png)).convert("RGB").tobytes()).hexdigest()[:16]
        response = json.loads((cache / f"{key}-{noun}.json").read_text())
        return hosted_sam.image_instances(hosted_sam.output_text(response), w, h)

    npz = (src / "mapanything.npz").read_bytes()
    room = json.loads((src / "room.json").read_text())
    scene = json.loads((src / "scene.json").read_text())
    scene["objects"] = [o for o in scene["objects"] if not str(o.get("id", "")).startswith(("wall-", "room-object-"))]
    start = time.perf_counter()
    with patch.object(hosted_sam, "image_instances", timed("decode_validation_thread_sum_s", hosted_sam.image_instances)), \
         patch.object(room_shell, "furniture", timed("lift_s", room_shell.furniture)), \
         patch.object(live_room, "analyse", timed("analyse_s", live_room.analyse)):
        result, shell, _ = room_shell.build(npz, room, scene, detect)
    elapsed = time.perf_counter() - start
    summary = {"label": "MEASURED local cached public RM02 replay; no GPU/SAM/SF3D calls",
               "total_s": elapsed, **totals, "sam_calls_replayed": shell["sam_calls"],
               "objects": len(result["objects"]), "scene_sha256": hashlib.sha256(
                   json.dumps(result, sort_keys=True).encode()).hexdigest()}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
