"""Check custody and frame references, NOT metric eligibility or visual truth."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

BASE = Path(__file__).resolve().parent


def check_frames(frames, pts, step):
    assert frames, 'empty extraction'
    for f in frames:
        n = f['frame_index_0']
        assert isinstance(n, int) and 0 <= n < len(pts), 'invalid source index'
        assert abs(pts[n] - f['pts_s']) < 0.0006, 'mismatched PTS'
    assert all(b['frame_index_0'] - a['frame_index_0'] == step
               for a, b in zip(frames, frames[1:])), 'wrong frame stride'


def self_check():
    pts = [0.004, 0.044, 0.084]
    check_frames([{'frame_index_0': 0, 'pts_s': 0.004},
                  {'frame_index_0': 1, 'pts_s': 0.044}], pts, 1)
    for bad in [
        [{'frame_index_0': 0, 'pts_s': 0.044}],
        [{'frame_index_0': 3, 'pts_s': 0.124}],
        [{'frame_index_0': 0, 'pts_s': 0.004}, {'frame_index_0': 2, 'pts_s': 0.084}]
    ]:
        try:
            check_frames(bad, pts, 1)
        except AssertionError:
            continue
        raise AssertionError('negative guard failed')


if __name__ == '__main__':
    self_check()
    source = json.loads((BASE / 'source.json').read_text())
    path = Path(source['source_path'])
    assert path.stat().st_size == source['bytes'] == 50013019
    with path.open('rb') as stream:
        assert hashlib.file_digest(stream, 'sha256').hexdigest() == source['sha256'] == (
            'f2c27c9d821d2c6673f3b080a51aadd1d6890f962c1b180672de17f678cc3265')
    pts = [float(x) for x in Path(source['pts_reference']).read_text().splitlines() if x.strip()]
    assert len(pts) == 15361
    maps = {}
    for mapping in sorted(BASE.glob('mapping-*.json')):
        sheets = json.loads(mapping.read_text())
        frames = [f for sheet in sheets for f in sheet['frames']]
        step = int(mapping.stem.rsplit('step', 1)[1])
        check_frames(frames, pts, step)
        maps[mapping.name] = frames
        start = mapping.stem.removeprefix('mapping-').split('-step')[0]
        raw = BASE / 'media' / f'raw-{start}'
        log_pts = [float(t) for t in re.findall(r'pts_time:([\d.]+)',
                                               (raw / 'ffmpeg.txt').read_text())][:len(frames)]
        assert len(log_pts) == len(frames) == len(list(raw.glob('*.png')))
        assert all(abs(t-f['pts_s']) < 0.0006 for t, f in zip(log_pts, frames))
        for sheet in sheets:
            with Image.open(BASE / sheet['sheet']) as image:
                image.verify()
    inventory = json.loads((BASE / 'inventory.json').read_text())
    for event in inventory['events']:
        frames = maps[event['mapping']]
        assert event['frames'] == [frames[0]['frame_index_0'], frames[-1]['frame_index_0']]
        assert event['pts_s'] == [frames[0]['pts_s'], frames[-1]['pts_s']]
        assert event['flight_certified'] is False
    for log, target in [('witness-440.txt', 440.924), ('witness-457.txt', 457.644)]:
        actual = re.findall(r'pts_time:([\d.]+)', (BASE / 'media' / log).read_text())
        assert actual and abs(float(actual[0])-target) < 0.0006
    for path in (BASE / 'frames').iterdir():
        with Image.open(path) as image:
            image.verify()
    native = [f for name, fs in maps.items() if name.endswith('step1.json') for f in fs]
    receipt = {
        'checked_utc': datetime.now(timezone.utc).isoformat(), 'status': 'PASS',
        'source_sha256_verified': True, 'mapping_files': len(maps),
        'mapped_samples': sum(map(len, maps.values())),
        'native_frame_references': len(native),
        'native_unique_frames': len({f['frame_index_0'] for f in native}),
        'event_entries_including_nested_details': len(inventory['events']),
        'negative_guard_self_checks': 3, 'metric_eligibility_verified': False,
        'limitation': 'Machine checks verify source identity/indexing/images, not visual classification or acquisition clock.'
    }
    (BASE / 'verification.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))
