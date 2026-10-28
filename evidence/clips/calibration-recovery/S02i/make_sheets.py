"""Bounded source-frame evidence; labels are delivered PTS, never capture time."""
import argparse
import bisect
import json
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parent

def sheet(source, pts, start, duration, step=1):
    first = bisect.bisect_left(pts, start)
    last = bisect.bisect_left(pts, start + duration)
    assert last > first and step >= 1
    out = BASE / 'media' / f'raw-{start:g}'
    out.mkdir(parents=True, exist_ok=True)
    # Keep the source timestamps in showinfo, independently verify extraction map.
    cmd = ['ffmpeg', '-v', 'info', '-threads', '1', '-copyts', '-ss', str(start),
           '-i', str(source), '-to', str(start + duration), '-vf',
           f'select=not(mod(n\\,{step})),showinfo,scale=426:240',
           '-fps_mode', 'passthrough', '-y', str(out / '%05d.png')]
    result = subprocess.run(cmd, capture_output=True, text=True)
    (out / 'ffmpeg.txt').write_text(result.stderr, encoding='utf-8')
    assert result.returncode == 0, result.stderr[-1000:]
    import re
    extracted = [float(t) for t in re.findall(r'pts_time:([\d.]+)', result.stderr)]
    paths = sorted(out.glob('*.png'))
    # showinfo can log encoder-lookahead frames beyond output -to; never label them.
    assert len(paths) == len(range(first, last, step)) > 0, (len(paths), first, last)
    extracted = extracted[:len(paths)]
    assert len(paths) == len(extracted) and all(start <= t < start+duration for t in extracted)
    mapping = []
    for i, t in enumerate(extracted):
        n = bisect.bisect_left(pts, t - 0.0005)
        assert n < len(pts) and abs(pts[n] - t) < 0.0006, (n, t)
        assert n == first + i * step, (n, first, i, step)
        mapping.append({'frame_index_0': n, 'pts_s': t})
    records = []
    for offset in range(0, len(paths), 24):
        subset = paths[offset:offset+24]
        canvas = Image.new('RGB', (426*4, 264*6), 'black')
        draw = ImageDraw.Draw(canvas)
        for i, path in enumerate(subset):
            x, y = i % 4 * 426, i // 4 * 264
            with Image.open(path) as im:
                canvas.paste(im, (x, y+24))
            m = mapping[offset+i]
            draw.text((x+4, y+4), f"n={m['frame_index_0']} PTS={m['pts_s']:.3f}s", fill='white')
        name = f'frames/native-{start:g}-step{step}-{offset//24+1:02d}.jpg'
        canvas.save(BASE / name, quality=88)
        records.append({'sheet': name, 'frames': mapping[offset:offset+24]})
    (BASE / f'mapping-{start:g}-step{step}.json').write_text(json.dumps(records, indent=2))
    print(f'{start:g}: {len(paths)} verified frames, {len(records)} sheets')

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('start', type=float)
    p.add_argument('duration', type=float)
    p.add_argument('--step', type=int, default=1)
    a = p.parse_args()
    pts = [float(x) for x in (BASE / 'pts-480p.csv').read_text().splitlines() if x.strip()]
    assert pts and all(b > a for a, b in zip(pts, pts[1:])), 'PTS must be monotonic'
    sheet(BASE / 'media/RP01-480p.webm', pts, a.start, a.duration, a.step)
