"""Resolve the tiny bearing without another video download (native-pixel crop)."""
import json
import re
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parent
source = json.loads((BASE / 'source.json').read_text())['source_path']
out = BASE / 'media/crop-459.8'
out.mkdir(parents=True, exist_ok=True)
result = subprocess.run([
    'ffmpeg', '-v', 'info', '-threads', '1', '-copyts', '-ss', '459.8',
    '-i', source, '-to', '467', '-vf', 'crop=140:330:350:0,showinfo',
    '-fps_mode', 'passthrough', '-y', str(out / '%05d.png')
], capture_output=True, text=True)
(out / 'ffmpeg.txt').write_text(result.stderr)
assert result.returncode == 0, result.stderr[-1000:]
expected = [f for s in json.loads((BASE / 'mapping-459.8-step1.json').read_text()) for f in s['frames']]
paths = sorted(out.glob('*.png'))
actual = [float(t) for t in re.findall(r'pts_time:([\d.]+)', result.stderr)][:len(paths)]
assert len(paths) == len(expected) == len(actual) == 180
assert all(abs(t - f['pts_s']) < 0.0006 for t, f in zip(actual, expected))
for offset in range(0, len(paths), 24):
    canvas = Image.new('RGB', (840, 1400), 'black')
    draw = ImageDraw.Draw(canvas)
    for j, path in enumerate(paths[offset:offset+24]):
        x, y = (j % 6) * 140, (j // 6) * 350
        with Image.open(path) as frame:
            assert frame.size == (140, 330)
            canvas.paste(frame, (x, y+20))
        f = expected[offset+j]
        draw.text((x, y), f"{f['frame_index_0']} {f['pts_s']:.3f}", fill='white')
    canvas.save(BASE / f'frames/crop-459.8-{offset//24+1:02d}.png')
for page in range(2):
    canvas = Image.new('RGB', (1400, 1400), 'black')
    draw = ImageDraw.Draw(canvas)
    for j in range(10):
        k = 11638 - 11495 + page * 10 + j
        x, y = j % 5 * 280, j // 5 * 700
        with Image.open(paths[k]) as frame:
            canvas.paste(frame.resize((280, 660), Image.Resampling.NEAREST), (x, y+40))
        f = expected[k]
        draw.text((x+4, y+4), f"n={f['frame_index_0']} {f['pts_s']:.3f}", fill='white')
    canvas.save(BASE / f'frames/zoom-465-{page+1:02d}.png')
print('180 native-pixel crops; PTS cross-checked; 8 sheets + 2 nearest-neighbour zooms')
