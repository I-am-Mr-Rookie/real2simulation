"""Measure the real shell-file path with cached public RM02 SAM responses. No paid calls.

Usage: python evidence/N53/shell_files.py SOURCE_JOB SAM_CACHE OUTPUT.json [--strict-codec]
"""
import hashlib
import io
import json
import shutil
import sys
import time
from pathlib import Path
from unittest.mock import patch

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from Build.api.room.objects import build_shell_files
from Build.measurement import hosted_sam
from Build.reconstruction import live_room
from Build.reconstruction import _sam_mask_codec as codec
from evidence.N53.verify_codec import strict_codec


def main():
    src, cache, output = map(Path, sys.argv[1:4])
    original = "--strict-codec" in sys.argv[4:]
    decode = strict_codec().decode_mask_to_raster if original else codec.decode_mask_to_raster
    saves = {}
    write = live_room._write

    def timed_write(path, obj):
        start = time.perf_counter()
        write(path, obj)
        saves[path.name] = time.perf_counter() - start

    def detect(png, noun, w, h):
        key = hashlib.sha256(f"{w}x{h}".encode() + Image.open(io.BytesIO(png)).convert("RGB").tobytes()).hexdigest()[:16]
        response = json.loads((cache / f"{key}-{noun}.json").read_text())
        return hosted_sam.image_instances(hosted_sam.output_text(response), w, h)

    job = output.with_suffix(".local")
    job.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src / "mapanything.npz", job / "mapanything.npz")
    start = time.perf_counter()
    live_room.finish(job)
    finish_s = time.perf_counter() - start
    start = time.perf_counter()
    with patch.object(live_room, "_write", timed_write), patch.object(codec, "decode_mask_to_raster", decode):
        shell, scene = build_shell_files(job, detect, generate=None)
    total_s = time.perf_counter() - start
    assert json.loads((job / "scene.json").read_text()) == scene
    assert json.loads((job / "room.json").read_text())["shell"] == shell
    ids = [o["id"] for o in scene["objects"]]
    assert len(ids) == len(set(ids))
    summary = {"label": "MEASURED local production file path; cached public RM02; GPU and SAM network not run",
               "codec": "base strict" if original else "fused canonical",
               "finish_s": finish_s, "shell_including_save_s": total_s, "shell_stage_timing_s": shell["timing_s"],
               "save_s": saves, "objects": len(scene["objects"])}
    output.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
