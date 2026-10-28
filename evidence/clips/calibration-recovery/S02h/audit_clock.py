"""Bounded RP03 presentation diagnostics, not a sensor clock or physical fit."""
import argparse
import csv
import hashlib
import json
import subprocess
from pathlib import Path

import cv2
import numpy as np


def projective_family(x, k):
    # Endpoint-preserving counterexample; dimensionless, not observed positions.
    return x / (1 + k * (1 - x))


def self_check():
    for k in (0, 1, 3):
        assert projective_family(0, k) == 0
        assert projective_family(1, k) == 1
    assert projective_family(.5, 0) != projective_family(.5, 1)
    assert abs((240 / 200) - 1.2) < 1e-12
    assert abs((1 / 200) / (1 / 240) - 1.2) < 1e-12
    a = np.array([0, 255], dtype=np.uint8)
    b = np.array([255, 0], dtype=np.uint8)
    assert np.mean(np.abs(a.astype(np.float32) - b)) == 255


def run(media, out):
    self_check()
    out.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(media.read_bytes()).hexdigest()
    assert digest == 'e72d5406cd74f02dd76ad310adda42b4f1bdff0ec0953efa45b46069faa5fa7c', 'Not retained RP03 rendition'
    probe = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_frames',
        '-show_entries', 'frame=best_effort_timestamp_time,pkt_duration_time',
        '-of', 'json', str(media)], text=True))
    frames = probe['frames']
    cap = cv2.VideoCapture(str(media))
    rows, descriptors = [], {}
    prev = None
    for n, f in enumerate(frames):
        ok, image = cap.read()
        assert ok, f'Decode stopped at {n}'
        # Exclude right-side burned-in clock; same fixed crop in both replays.
        gray = cv2.cvtColor(image[:, :310], cv2.COLOR_BGR2GRAY)
        small = cv2.resize(gray, (80, 60), interpolation=cv2.INTER_AREA)
        pts = float(f['best_effort_timestamp_time'])
        mad = None if prev is None else float(np.mean(np.abs(small.astype(np.float32) - prev)))
        rows.append({'frame': n, 'pts_s': pts, 'crop_md5': hashlib.md5(gray.tobytes()).hexdigest(), 'crop_mad_prev': mad})
        if 9 <= pts <= 60:
            descriptors[n] = small.astype(np.float32)
        prev = small.astype(np.float32)
    assert not cap.read()[0], 'More decoded frames than ffprobe rows'
    cap.release()
    with (out / 'frame-diagnostics.csv').open('w', newline='') as fp:
        writer = csv.DictWriter(fp, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    # Candidate correspondences only; manual image inspection must check them.
    target_ids = [n for n in descriptors if 18 <= rows[n]['pts_s'] <= 59]
    targets = np.stack([descriptors[n] for n in target_ids])
    matches = []
    for n in descriptors:
        if not 10 <= rows[n]['pts_s'] <= 14.5 or n % 3:
            continue
        errors = np.mean(np.abs(targets - descriptors[n]), axis=(1, 2))
        rank = int(np.argmin(errors))
        j = target_ids[rank]
        matches.append({'realtime_frame': n, 'realtime_pts_s': rows[n]['pts_s'], 'replay_frame': j, 'replay_pts_s': rows[j]['pts_s'], 'crop_mad': float(errors[rank])})
    with (out / 'replay-correspondences.csv').open('w', newline='') as fp:
        writer = csv.DictWriter(fp, fieldnames=list(matches[0]))
        writer.writeheader()
        writer.writerows(matches)
    delta = np.diff([r['pts_s'] for r in rows])
    result = {'sha256': digest, 'frames': len(rows), 'first_pts_s': rows[0]['pts_s'], 'last_pts_s': rows[-1]['pts_s'],
              'pts_delta_values_s': sorted(set(np.round(delta, 6))), 'decode_complete': True,
              'crop': 'x=0..309, y=0..239; grayscale; MAD descriptor 80x60',
              'exact_adjacent_crop_hash_equal': sum(a['crop_md5'] == b['crop_md5'] for a,b in zip(rows, rows[1:])),
              'windows': {}, 'physical_clock_verified': False,
              'limitation': 'Compression/interpolation/camera motion confound uniqueness; PTS and burned-in timer are editor evidence, not independent sensor timestamps.'}
    for lo, hi in [(10, 11), (11, 14), (20, 21), (22, 23), (24, 25), (30, 31), (40, 41), (50, 51)]:
        vals = np.array([r['crop_mad_prev'] for r in rows if lo <= r['pts_s'] < hi])
        result['windows'][f'{lo}-{hi}'] = {'frames': len(vals), 'mad_percentiles': np.percentile(vals, [0, 25, 50, 75, 100]).tolist(), 'mad_over_1': int(sum(vals > 1))}
    (out / 'clock-summary.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('media', type=Path, nargs='?')
    parser.add_argument('--out', type=Path, default=Path(__file__).parent)
    args = parser.parse_args()
    if args.media:
        run(args.media, args.out)
    else:
        self_check()
        print('PASS: endpoint ambiguity, clock ratio, unsigned-difference self-checks')
