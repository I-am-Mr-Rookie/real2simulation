"""Rebuild cached MapAnything data without another GPU job; cache raw SAM replies for repeatable comparisons.

Owner room input/output/cache must ALL be under test-data/private/N52. Public RM02 may use evidence/N52.
Usage: python rebuild.py SOURCE_DIR OUTPUT_DIR CAP_DB [--paid]
"""
import hashlib
import io
import json
import sys
import time
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from Build.reconstruction import live_room, object_lift, room_shell


def main():
    src, out, cap = map(Path, sys.argv[1:4])
    out.mkdir(parents=True, exist_ok=True)
    cache = out / "sam"
    cache.mkdir(exist_ok=True)
    paid = "--paid" in sys.argv[4:]

    def detect(png, noun, w, h):
        key = hashlib.sha256(f"{w}x{h}".encode() + Image.open(io.BytesIO(png)).convert("RGB").tobytes()).hexdigest()[:16]
        path = cache / f"{key}-{noun}.json"
        if path.exists():
            response = json.loads(path.read_text())
        else:
            if not paid:
                raise RuntimeError("Uncached SAM input; pass --paid for the bounded room run")
            response = object_lift._sam_image(png, noun, f"N52 shell {noun}", cap, 120)
            path.write_text(json.dumps(response))
        return object_lift.hosted_sam.image_instances(object_lift.hosted_sam.output_text(response), w, h)

    room = json.loads((src / "room.json").read_text())
    scene = json.loads((src / "scene.json").read_text())
    scene["objects"] = [o for o in scene["objects"] if not str(o.get("id", "")).startswith(("wall-", "room-object-"))]
    npz = (src / "mapanything.npz").read_bytes()
    t = time.monotonic()
    result, shell, _ = room_shell.build(npz, room, scene, detect)
    (out / "scene.json").write_text(json.dumps(result, indent=1))
    (out / "shell.json").write_text(json.dumps(shell, indent=1))
    summary = {"seconds": round(time.monotonic() - t, 2), "objects": len(result["objects"]),
               "openings": shell["openings"], "kept": shell["kept"],
               "looks": [{"id": o["id"], "size": o["size"], **o["look"]} for o in result["objects"] if "look" in o]}
    (out / "summary.json").write_text(json.dumps(summary, indent=1))
    Image.open(io.BytesIO(object_lift.view_png(npz, 4)[0])).save(out / "source-view4.png")
    print(json.dumps({"seconds": summary["seconds"], "objects": summary["objects"], "openings": len(shell["openings"]),
                      "kept": [(k["category"], k["size_m"]) for k in shell["kept"]]}))


if __name__ == "__main__":
    main()
