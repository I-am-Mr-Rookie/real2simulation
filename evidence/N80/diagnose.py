"""CPU-only public RM02 replay; raw cached SAM masks versus depth/collision masks. No provider calls."""
import hashlib
import io
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from Build.measurement import hosted_sam
from Build.reconstruction import object_lift, room_shell

SOURCE_SHA = "82e6cc99142b9791ad30c18ac2c92106a30a0082b61d6063aace74d31c986154"
IDS = (1, 2, 4, 7)


def load_public(bundle, cache):
    raw = (bundle / "RM02-mapanything.npz").read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA:
        raise ValueError("Only the approved public RM02 archive is allowed")
    room = json.loads((bundle / "RM02-sample-room.json").read_text())
    detections = []
    for view in range(16):
        png, w, h = object_lift.view_png(raw, view)
        key = hashlib.sha256(f"{w}x{h}".encode() + Image.open(io.BytesIO(png)).convert("RGB").tobytes()).hexdigest()[:16]
        for noun in room_shell.FURNITURE:
            response = json.loads((cache / f"{key}-{noun}.json").read_text())
            detections.extend((view, noun, d) for d in hosted_sam.image_instances(hosted_sam.output_text(response), w, h))
    return raw, room, detections


if __name__ == "__main__":
    bundle, cache = map(Path, sys.argv[1:3])
    raw, room, detections = load_public(bundle, cache)
    kept, _ = room_shell.furniture(raw, room, detections)
    out = ROOT / "evidence/N80"
    (out / "diagnosis.local").mkdir(exist_ok=True)
    sheet = Image.new("RGB", (1200, 500), "#ddd")
    draw, rows = ImageDraw.Draw(sheet), []
    for i, n in enumerate(IDS):
        it = kept[n - 1]
        view, box = (it["crop"][k] for k in ("view", "box"))
        mask = room_shell.crop_mask(raw, it, room)
        noun = it["noun"]
        image = Image.open(io.BytesIO(object_lift.crop_rgba(raw, view, box, mask))).convert("RGBA")
        image.save(out / f"diagnosis.local/raw-sam-{n}.png")
        bg = Image.new("RGBA", image.size, "#737373")
        bg.alpha_composite(image)
        bg = bg.convert("RGB")
        bg.thumbnail((290, 425))
        sheet.paste(bg, (i * 300, 55))
        row = {"id": n, "view": view, "noun": noun, "box": list(box),
               "sam_pixels": int(it["crop"]["mask"].sum()), "appearance_pixels": int(mask.sum()),
               "depth_material_supported_repair_pixels": int((mask & ~it["crop"]["mask"]).sum()),
               "proxy_pixels": int(it["proxy"]["mask"].sum()), "views": it["views"], "size": it["proxy"]["size"]}
        rows.append(row)
        draw.text((i * 300, 5), f"{n} view {view} {noun}", fill="black")
    sheet.save(out / "crops-after.jpg", quality=95)
    (out / "diagnosis.json").write_text(json.dumps({"kept": len(kept), "objects": rows}, indent=2) + "\n")
    print(json.dumps(rows))
