"""Batch-A size/encoding exports and six-mode review sheets; installed Pillow only."""
import hashlib
import json
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / 'Build/web/public/images/marketing'
DATA = json.loads((HERE / 'generation.json').read_text(encoding='utf-8'))
PICKS = {f'a{i}-light-line': f'a{i}-light-line-r2' for i in range(1, 6)}
PICKS.update({'a1-dark-line': 'a1-dark-line'})
PICKS.update({f'a{i}-dark-line': f'a{i}-dark-opaque' for i in (2, 3, 4)})
PICKS['a3-dark-line'] = 'a3-dark-opaque-r2'
SIZES = {'a1': (1600, 1000), 'a2': (800, 600), 'a3': (800, 600), 'a4': (800, 600), 'a5': (1200, 630)}
SURFACES = {'paper': '#fffcf5', 'light': '#ffffff', 'dark': '#18181b', 'midnight': '#111831', 'graphite': '#26282c', 'contrast': '#ffffff'}
FONT = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 20)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, key in PICKS.items():
        master = HERE / 'masters' / f'{name}.png'
        if not master.exists():
            master.parent.mkdir(exist_ok=True)
            shutil.copyfile(DATA['sources'][key], master)
        src = Image.open(master).convert('RGBA')
        brief = name[:2]
        # Controller-approved recovery: opaque family tiles avoid generated alpha artefacts.
        transparent = False
        dark = 'dark-line' in name
        colours = ('#18181b', '#f4f4f5', '#ff8a4c', '#71717c') if dark else ('#f3eee3', '#1c1a16', '#b23a0e', '#d8cfbe')
        ground = Image.new('RGBA', src.size, colours[0])
        ground.alpha_composite(src)
        palette = Image.new('P', (1, 1))
        rgb = [tuple(bytes.fromhex(c[1:])) for c in colours]
        palette.putpalette([v for c in rgb for v in c] + list(rgb[0]) * 252)
        # Palette normalization removes generated ground noise and keeps exactly one motion accent.
        src = ground.convert('RGB').quantize(palette=palette, dither=Image.Dither.NONE).convert('RGBA')
        for scale in (1, 2):
            size = tuple(n * scale for n in SIZES[brief])
            # Contain rather than crop: the brief's edge margins must survive sizing.
            image = ImageOps.contain(src, size, Image.Resampling.LANCZOS)
            ground = colours[0]
            canvas = Image.new('RGBA', size, ground)
            canvas.alpha_composite(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
            if not transparent:
                canvas = canvas.convert('RGB')
            for ext in ('png', 'webp'):
                path = OUT / f'{name}@{scale}x.{ext}'
                canvas.save(path, **({'quality': 82, 'method': 6} if ext == 'webp' else {'optimize': True}))
                with Image.open(path) as check:
                    check.load()
                    assert check.size == size
                    assert (check.convert('RGBA').getchannel('A').getextrema()[0] == 0) == transparent
                rows.append({'file': path.relative_to(ROOT).as_posix(), 'size': list(size), 'bytes': path.stat().st_size, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'source': key})
    for mode, surface in SURFACES.items():
        sheet = Image.new('RGB', (1400, 1050), surface)
        draw = ImageDraw.Draw(sheet)
        ink = '#1c1a16' if mode in ('paper', 'light', 'contrast') else '#f4f4f5'
        draw.text((24, 18), f'{mode} surface {surface} / export review / 240px feature thumbnails', fill=ink, font=FONT)
        for i in range(1, 6):
            variant = 'light-line' if mode in ('paper', 'light', 'contrast') or i == 5 else 'dark-line'
            path = OUT / f'a{i}-{variant}@1x.webp'
            image = Image.open(path).convert('RGBA')
            image.thumbnail((610, 370) if i == 1 else (610, 320) if i == 5 else (240, 180), Image.Resampling.LANCZOS)
            x, y = {1: (25, 80), 2: (720, 85), 3: (1000, 85), 4: (720, 365), 5: (25, 660)}[i]
            sheet.paste(image, (x, y), image)
            draw.text((x, y + image.height + 8), f'A{i} / {variant}', fill=ink, font=FONT)
        sheet.save(HERE / f'contact-{mode}.jpg', quality=92)
    # Actual 200% source-pixel crops on the two explicitly required halo-test grounds.
    for variant, bg in (('light-line', '#ffffff'), ('dark-line', '#111113')):
        sheet = Image.new('RGB', (1200, 800), bg)
        for col, i in enumerate((2, 3, 4)):
            src = Image.open(OUT / f'a{i}-{variant}@1x.png').convert('RGBA')
            box = {2: (300, 220, 500, 420), 3: (420, 40, 620, 240), 4: (300, 300, 500, 500)}[i]
            crop = src.crop(box).resize((400, 400), Image.Resampling.NEAREST)
            sheet.paste(crop, (col * 400, 70), crop)
            ImageDraw.Draw(sheet).text((col * 400 + 12, 20), f'A{i} PNG 200% / {bg}', fill='#999999', font=FONT)
        sheet.save(HERE / f'alpha-200-{variant}.png')
    result = {'exports': rows, 'count': len(rows), 'total_bytes': sum(r['bytes'] for r in rows), 'webp_bytes': sum(r['bytes'] for r in rows if r['file'].endswith('.webp')), 'surfaces': SURFACES, 'notes': ['Sizes, decoding and opacity assertions pass; aesthetic acceptance is separate.', 'Controller-approved opaque family tiles: A2/A3/A4 transparency waived.', 'Palette normalization before sizing; 2x is a Lanczos resample, not native 2x detail.']}
    og = Image.open(OUT / 'a5-light-line@1x.png').convert('RGB')
    blank = og.crop((0, 0, int(og.width * .6), og.height))
    assert blank.getextrema() == ((243, 243), (238, 238), (227, 227)), 'OG left 60% must be a flat empty paper ground'
    assert len(DATA['prompts']) == len(DATA['sources']) == 24
    assert result['total_bytes'] < 8 * 1024 * 1024
    result['og_blank_left_60_percent'] = True
    result['generation_calls'] = len(DATA['prompts'])
    (HERE / 'checks.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    assert len(rows) == 36
    print(json.dumps({k: result[k] for k in ('count', 'total_bytes', 'webp_bytes')}))

if __name__ == '__main__':
    main()
