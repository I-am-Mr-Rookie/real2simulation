"""Reuse S02i's PTS-checked extractor; never reinterpret delivery as capture time."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
EXPECTED = 'f2c27c9d821d2c6673f3b080a51aadd1d6890f962c1b180672de17f678cc3265'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('prior', type=Path, help='retained S02i evidence directory, read-only')
    parser.add_argument('start', type=float)
    parser.add_argument('duration', type=float)
    parser.add_argument('--step', type=int, default=1)
    args = parser.parse_args()
    source = args.prior / 'media/RP01-480p.webm'
    digest = hashlib.file_digest(source.open('rb'), 'sha256').hexdigest()
    assert digest == EXPECTED, 'unexpected retained rendition'
    pts = [float(x) for x in (args.prior / 'pts-480p.csv').read_text().splitlines() if x.strip()]
    assert len(pts) == 15361 and all(abs(b-a-0.04) < 1e-9 for a, b in zip(pts, pts[1:]))
    spec = importlib.util.spec_from_file_location('prior_sheets', BASE.parent / 'make_sheets.py')
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    helper.BASE = BASE
    (BASE / 'frames').mkdir(exist_ok=True)
    helper.sheet(source, pts, args.start, args.duration, args.step)
    (BASE / 'source.json').write_text(json.dumps({
        'source_path': str(source), 'sha256': digest, 'bytes': source.stat().st_size,
        'pts_reference': str(args.prior / 'pts-480p.csv'),
        'delivered_frames': len(pts), 'capture_clock_verified': False,
        'note': 'Existing licensed derivative reused read-only; exact delivered PTS only.'
    }, indent=2) + '\n')
