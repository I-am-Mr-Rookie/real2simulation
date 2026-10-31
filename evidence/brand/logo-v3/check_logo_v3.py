"""S15at: assert logo v3 exports keep filenames/sizes and correct alpha (copied from check_logo_v2.py)."""
import pathlib, xml.etree.ElementTree as ET
from PIL import Image

B = pathlib.Path(__file__).resolve().parents[3] / "Build/web/public/brand"
SIZES = {"mark-1024.png": (1024, 1024), "mark-512.png": (512, 512), "mark-192.png": (192, 192), "mark-32.png": (32, 32),
         "icon-maskable-512.png": (512, 512), "wordmark-light.png": (924, 192), "wordmark-dark.png": (924, 192)}
for name, size in SIZES.items():
    im = Image.open(B / name); assert im.size == size and im.mode == "RGBA", (name, im.size, im.mode)
    a = im.getchannel("A"); lo, hi = a.getextrema()
    if name == "icon-maskable-512.png":
        assert lo == 255, "maskable must be opaque"
        bg = im.getpixel((0, 0))
        diff = [(x, y) for y in range(0, 512, 4) for x in range(0, 512, 4) if im.getpixel((x, y)) != bg]
        assert all((x - 256) ** 2 + (y - 256) ** 2 <= (0.4 * 512) ** 2 for x, y in diff), "art outside 80% safe circle"
    else:
        assert lo == 0 and hi == 255, (name, "needs transparent background and opaque art")
        assert im.getpixel((0, 0))[3] == 0, (name, "corner not transparent")
        if name.startswith("wordmark"):
            box = a.getbbox(); assert box[1] >= 0 and box[3] <= 192 and a.crop((0, 0, 192, 192)).getbbox()[1] > 0, (name, "mark clipped")
ico = Image.open(B / "favicon.ico"); assert ico.format == "ICO" and {(16, 16), (32, 32), (48, 48)} <= set(ico.ico.sizes()), ico.ico.sizes()
for s in (16, 32, 48): assert ico.ico.getimage((s, s)).size == (s, s)
for svg in ("mark.svg", "mark-dark.svg", "mark-16.svg"):
    root = ET.parse(B / svg).getroot(); assert root.tag.endswith("svg") and root.get("viewBox"), svg
    assert not any(e.tag.endswith("image") for e in root.iter()), (svg, "raster embedded")
# v3 structure: hatched support, dashed (or faint at 16u) ghost strings, two hollow ghosts, one solid bob.
for svg, dashes in (("mark.svg", True), ("mark-16.svg", False)):
    root = ET.parse(B / svg).getroot(); circles = [e for e in root.iter() if e.tag.endswith("circle")]
    assert sum(e.get("fill") == "none" for e in circles) == 2 and sum(e.get("fill") != "none" for e in circles) == 1, (svg, "bobs")
    lines = [e for e in root.iter() if e.tag.endswith("line")]
    assert len(lines) >= (14 if dashes else 7), (svg, "support/hatch/strings missing", len(lines))
print("logo-v3 checks OK")

