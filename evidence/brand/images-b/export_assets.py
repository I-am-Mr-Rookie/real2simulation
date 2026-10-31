"""Authorized white-key recovery, deterministic palette exports and six-mode proof sheets."""
from pathlib import Path
import json
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageChops

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'Build/web/public/images/app'
SIZES = {'b1': (512, 512), 'b2': (512, 512), 'b3': (960, 540),
         'b4': (800, 600), 'b5': (384, 384), 'b6': (512, 512)}
MODES = {'paper': '#f3eee3', 'light': '#f7f7f8', 'dark': '#111113',
         'midnight': '#0b1020', 'graphite': '#1f2023', 'contrast': '#ffffff'}


def extract(source, variant):
    rgb = source.convert('RGB')
    # Controller Oct31 recovery: alpha=255-luminance, thresholded to suppress white noise.
    alpha = rgb.convert('L').point(lambda x: max(0, min(255, (255-x-24)*255//208)))
    r, g, b = rgb.split()
    warm = ImageChops.subtract(r, g).point(lambda x: 255 if x > 32 else 0)
    warm = ImageChops.multiply(warm, ImageChops.subtract(r, b).point(lambda x: 255 if x > 45 else 0))
    alpha = ImageChops.lighter(alpha, warm)
    ink, spot = ('#1c1a16', '#b23a0e') if variant == 'light' else ('#f4f4f5', '#ff8a4c')
    result = Image.composite(Image.new('RGB', rgb.size, spot), Image.new('RGB', rgb.size, ink), warm).convert('RGBA')
    result.putalpha(alpha)
    box = alpha.point(lambda x: 255 if x > 32 else 0).getbbox()
    assert box, 'Empty generated master'
    return result.crop(box)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    for brief, size in SIZES.items():
        master = Image.open(HERE / 'masters' / f'{brief}-white.png')
        for variant in ('light', 'dark'):
            art = extract(master, variant)
            for scale in (1, 2):
                target = tuple(v*scale for v in size)
                # B3's quiet cluster is intentionally half-width; others keep 15% margins.
                bounds = (int(target[0]*(.50 if brief == 'b3' else .70)), int(target[1]*.70))
                fitted = ImageOps.contain(art, bounds, Image.Resampling.LANCZOS)
                canvas = Image.new('RGBA', target)
                canvas.alpha_composite(fitted, ((target[0]-fitted.width)//2, (target[1]-fitted.height)//2))
                assert canvas.getchannel('A').getextrema() == (0, 255)
                assert canvas.getchannel('A').getpixel((0, 0)) == 0
                for ext in ('png', 'webp'):
                    path = OUT / f'{brief}-{variant}@{scale}x.{ext}'
                    canvas.save(path, **({'quality': 82, 'method': 6, 'exact': True} if ext == 'webp' else {'optimize': True}))
                    with Image.open(path) as saved:
                        assert saved.size == target and saved.mode == 'RGBA'
                        assert saved.getchannel('A').getextrema() == (0, 255)
                    records.append({'brief': brief, 'path': path.relative_to(ROOT).as_posix(), 'size': list(target), 'bytes': path.stat().st_size})
    for mode, bg in MODES.items():
        variant = 'dark' if mode in ('dark', 'midnight', 'graphite') else 'light'
        ink = '#f4f4f5' if variant == 'dark' else '#1c1a16'
        sheet = Image.new('RGB', (1200, 620), bg)
        draw = ImageDraw.Draw(sheet)
        draw.text((24, 18), f'{mode} {bg} | selected {variant}-line | actual placement + enlarged', fill=ink)
        for index, brief in enumerate(SIZES):
            x, y = (index % 3)*400, 50+(index//3)*280
            art = Image.open(OUT / f'{brief}-{variant}@2x.png')
            large = ImageOps.contain(art, (210, 210), Image.Resampling.LANCZOS)
            sheet.paste(large, (x+15, y+10), large)
            small_width = {'b1': 120, 'b2': 160, 'b3': 160, 'b4': 200, 'b5': 64, 'b6': 140}[brief]
            small = ImageOps.contain(art, (small_width, 150), Image.Resampling.LANCZOS)
            sheet.paste(small, (x+225, y+60), small)
            draw.text((x+20, y+235), f'{brief} / smallest {small_width}px', fill=ink)
        sheet.save(HERE / f'contact-{mode}.png', optimize=True)
    # 200% edge proof: one source crop on both prescribed alpha-test grounds.
    proof = Image.new('RGB', (1200, 600), '#ffffff')
    proof.paste(Image.new('RGB', (600, 600), '#111113'), (600, 0))
    for x, variant in ((0, 'light'), (600, 'dark')):
        art = Image.open(OUT / f'b5-{variant}@1x.png').resize((768, 768), Image.Resampling.NEAREST)
        crop = art.crop((140, 140, 740, 740))
        proof.paste(crop, (x, 0), crop)
    proof.save(HERE / 'alpha-200pct.png', optimize=True)
    (HERE / 'EXPORTS.json').write_text(json.dumps({'exports': records, 'total_bytes': sum(r['bytes'] for r in records)}, indent=2)+'\n')
    print(f"PASS: {len(records)} transparent exports, 6 mode sheets; total {sum(r['bytes'] for r in records):,} bytes")


if __name__ == '__main__':
    # Tiny trust-boundary self-check: white disappears; dark ink and orange survive.
    probe = Image.new('RGB', (3, 1), 'white')
    probe.putpixel((1, 0), (28, 26, 22)); probe.putpixel((2, 0), (178, 58, 14))
    result = extract(probe, 'dark')
    assert result.size == (2, 1) and result.getpixel((0, 0))[:3] == (244, 244, 245)
    assert result.getpixel((1, 0)) == (255, 138, 76, 255)
    main()
