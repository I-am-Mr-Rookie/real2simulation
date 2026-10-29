"""S05f: dump every MapAnything input frame (view*_img_no_norm) of the approved clips for visual standard-object search.

CPU only; reads existing NPZ (S05d manifest paths); writes one PNG per clip with view labels + 50px grid ticks
so any annotation can cite exact (row, col) on the 294x518 NPZ image.
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).parent


def main(manifest):
    out = {}
    for c in json.loads(Path(manifest).read_text()):
        d = np.load(c["npz"])
        n = len({k.split("_")[0] for k in d.files if k.startswith("view")})
        tiles = []
        for i in range(n):
            img = d[f"view{i}_img_no_norm"][0]
            img = (np.clip(img, 0, 1) * 255).astype(np.uint8) if img.max() <= 1.5 else img.astype(np.uint8)
            im = Image.fromarray(img)
            dr = ImageDraw.Draw(im)
            for x in range(0, im.width, 50):
                dr.line([(x, 0), (x, 4)], fill=(255, 0, 0))
            for y in range(0, im.height, 50):
                dr.line([(0, y), (4, y)], fill=(255, 0, 0))
            dr.text((6, 6), f"{c['clip_id']} view{i}", fill=(255, 255, 0))
            tiles.append(im)
        sheet = Image.new("RGB", (tiles[0].width * 2, tiles[0].height * ((n + 1) // 2)))
        for i, t in enumerate(tiles):
            sheet.paste(t, ((i % 2) * t.width, (i // 2) * t.height))
        p = HERE / f"frames-{c['clip_id']}.png"
        sheet.save(p)
        out[c["clip_id"]] = {"views": n, "image_rows_cols": list(tiles[0].size[::-1]),
                             "npz_sha256": hashlib.sha256(Path(c["npz"]).read_bytes()).hexdigest(),
                             "sheet": p.name, "sheet_sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
    (HERE / "frames.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "evidence/S05/S05d/manifest.json")
