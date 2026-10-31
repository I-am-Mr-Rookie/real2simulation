"""S15ap: assert logo v2 exports keep filenames/sizes and correct alpha."""
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
ico = Image.open(B / "favicon.ico"); assert ico.format == "ICO" and {(16, 16), (32, 32), (48, 48)} <= set(ico.ico.sizes()), ico.ico.sizes()
for s in (16, 32, 48): assert ico.ico.getimage((s, s)).size == (s, s)
for svg in ("mark.svg", "mark-dark.svg", "mark-16.svg"):
    root = ET.parse(B / svg).getroot(); assert root.tag.endswith("svg") and root.get("viewBox"), svg
    assert not any(e.tag.endswith("image") for e in root.iter()), (svg, "raster embedded")
print("logo-v2 checks OK")

