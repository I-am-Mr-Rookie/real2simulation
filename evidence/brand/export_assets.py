"""Export the selected generated raster logo; run from any working directory."""
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE.parents[1] / "Build/web/public/brand"
FONT = Path("C:/Windows/Fonts/segoeui.ttf")
BLUE = "#2878E8"
THEMES = {"light": ("#FFFFFF", "#17181C"), "dark": ("#0B0B0F", "#F4F4F5")}
CANDIDATES = {
    "A measured arc": "candidate-a-measured-arc.png",
    "B real to sim": "candidate-b-real-to-sim.png",
    "C falling samples": "candidate-c-falling-samples.png",
    "A refined - PICK": "candidate-a-refined.png",
}


def mark(path):
    source = Image.open(path).convert("RGBA")
    # Generated alpha has nearly invisible remote speckles; retain the real edges.
    alpha = source.getchannel("A").point(lambda a: a if a >= 16 else 0)
    alpha = alpha.filter(ImageFilter.MedianFilter(3))
    assert alpha.getbbox(), f"Empty generated mark: {path}"
    flat = Image.new("RGBA", source.size, BLUE)
    flat.putalpha(alpha)
    crop = flat.crop(alpha.getbbox())
    crop.thumbnail((860, 860), Image.Resampling.LANCZOS)
    result = Image.new("RGBA", (1024, 1024))
    result.alpha_composite(crop, ((1024 - crop.width) // 2, (1024 - crop.height) // 2))
    return result


def sized_mark(symbol, size):
    result = Image.new("RGBA", (size, size), BLUE)
    result.putalpha(symbol.getchannel("A").resize((size, size), Image.Resampling.LANCZOS))
    return result


def lockup(symbol, ink):
    font = ImageFont.truetype(str(FONT), 96)
    label = "Real2Simulation"
    left, top, right, bottom = font.getbbox(label)
    result = Image.new("RGBA", (192 + 28 + right - left + 24, 192))
    result.alpha_composite(sized_mark(symbol, 192))
    ImageDraw.Draw(result).text((220 - left, (192 - (bottom - top)) // 2 - top),
                               label, font=font, fill=ink)
    return result


def luminance(colour):
    rgb = Image.new("RGB", (1, 1), colour).getpixel((0, 0))
    linear = [v / 255 / 12.92 if v / 255 <= .04045 else ((v / 255 + .055) / 1.055) ** 2.4 for v in rgb]
    return sum(v * w for v, w in zip(linear, (.2126, .7152, .0722)))


def contrast(a, b):
    values = sorted((luminance(a), luminance(b)))
    return (values[1] + .05) / (values[0] + .05)


def main():
    assert FONT.is_file(), "Needs the existing Windows Segoe UI font; no font is redistributed"
    OUT.mkdir(parents=True, exist_ok=True)
    selected = mark(HERE / "candidate-a-refined.png")
    for size in (1024, 512, 192, 32):
        sized_mark(selected, size).save(OUT / f"mark-{size}.png")
    selected.save(OUT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    maskable = Image.new("RGBA", (512, 512), THEMES["dark"][0])
    maskable.alpha_composite(sized_mark(selected, 340), (86, 86))
    maskable.save(OUT / "icon-maskable-512.png")

    title_font = ImageFont.truetype(str(FONT), 25)
    label_font = ImageFont.truetype(str(FONT), 18)
    for theme, (background, ink) in THEMES.items():
        wordmark = lockup(selected, ink)
        wordmark.save(OUT / f"wordmark-{theme}.png")
        sheet = Image.new("RGBA", (1080, 720), background)
        draw = ImageDraw.Draw(sheet)
        draw.text((32, 24), f"Real2Simulation - selected A / {theme} {background}", font=title_font, fill=ink)
        sheet.alpha_composite(selected.resize((320, 320), Image.Resampling.LANCZOS), (32, 80))
        preview = wordmark.copy()
        preview.thumbnail((650, 120), Image.Resampling.LANCZOS)
        sheet.alpha_composite(preview, (380, 160))
        draw.text((380, 300), "Flat #2878E8. Below: actual pixel sizes (not enlarged).", font=label_font, fill=ink)
        for size, x in zip((16, 24, 32, 48, 64, 192), (48, 152, 264, 384, 512, 704)):
            if size in (16, 48):
                symbol = Image.open(OUT / "favicon.ico").ico.getimage((size, size)).convert("RGBA")
            elif size in (32, 192):
                symbol = Image.open(OUT / f"mark-{size}.png").convert("RGBA")
            else:
                symbol = sized_mark(selected, size)
            sheet.alpha_composite(symbol, (x, 465))
            draw.text((x, 430), f"{size}px", font=label_font, fill=ink)
        sheet.convert("RGB").save(HERE / f"legibility-{theme}.png")

    comparison = Image.new("RGBA", (1400, 860))
    for column, (theme, (background, ink)) in enumerate(THEMES.items()):
        comparison.paste(background, (column * 700, 0, (column + 1) * 700, 860))
        draw = ImageDraw.Draw(comparison)
        draw.text((column * 700 + 24, 20), f"Candidates / {theme} {background}", font=title_font, fill=ink)
        for row, (label, filename) in enumerate(CANDIDATES.items()):
            symbol = mark(HERE / filename)
            x, y = column * 700 + 24, 70 + row * 194
            draw.text((x, y), label, font=label_font, fill=ink)
            comparison.alpha_composite(symbol.resize((144, 144), Image.Resampling.LANCZOS), (x, y + 28))
            wordmark = lockup(symbol, ink)
            if theme == "light":
                wordmark.save(HERE / filename.replace(".png", "-wordmark.png"))
            wordmark.thumbnail((470, 96), Image.Resampling.LANCZOS)
            comparison.alpha_composite(wordmark, (x + 170, y + 65))
    comparison.convert("RGB").save(HERE / "candidates-light-dark.png")

    checks = {"pillow": Image.__version__, "palette": BLUE, "files": {}, "contrast": {}}
    for size in (1024, 512, 192, 32):
        image = Image.open(OUT / f"mark-{size}.png")
        assert image.size == (size, size) and image.mode == "RGBA"
        alpha = image.getchannel("A")
        assert alpha.getextrema() == (0, 255)
        assert alpha.getpixel((0, 0)) == 0 and alpha.getbbox()
        opaque = [pixel[:3] for pixel in image.get_flattened_data() if pixel[3] == 255]
        assert opaque and set(opaque) == {(40, 120, 232)}, "Solid interiors must use one exact flat colour"
    ico = Image.open(OUT / "favicon.ico")
    assert ico.ico.sizes() == {(16, 16), (32, 32), (48, 48)}
    for size in ico.ico.sizes():
        frame = ico.ico.getimage(size).convert("RGBA")
        assert frame.size == size and frame.getchannel("A").getextrema() == (0, 255)
    # The entire nontransparent foreground must fit the PWA central 80% circle.
    foreground = sized_mark(selected, 340).getchannel("A")
    for y in range(340):
        for x in range(340):
            if foreground.getpixel((x, y)) > 0:
                assert (x + 86 - 255.5) ** 2 + (y + 86 - 255.5) ** 2 <= 204.8 ** 2
    assert maskable.getchannel("A").getextrema() == (255, 255)
    for theme, (background, ink) in THEMES.items():
        ratio = contrast(BLUE, background)
        assert ratio >= 3, "Nontext mark contrast"
        assert contrast(ink, background) >= 4.5, "Wordmark text contrast"
        checks["contrast"][theme] = {"mark": round(ratio, 3), "wordmark": round(contrast(ink, background), 3)}
    for path in sorted(OUT.iterdir()):
        image = Image.open(path)
        checks["files"][path.name] = {"size": image.size, "mode": image.mode,
                                     "bytes": path.stat().st_size,
                                     "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    checks["assertions"] = "PASS: mark dimensions/alpha/flat fill; ICO 16/32/48 alpha; maskable 80% circle/opaque; light/dark contrast"
    (HERE / "checks.json").write_text(json.dumps(checks, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    main()
