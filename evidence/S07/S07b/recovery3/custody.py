"""One approved local ST03 receipt; never downloads, loads models or exports suffix."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone
from fractions import Fraction

from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from Build.measurement.tracking import _context

CANON = Path('C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon')
OUT = Path(__file__).resolve().parent
SOURCE = CANON / 'test-data/public/ST03.mp4'
JPEG = OUT / 'local/prefix'
EXPECTED = '7239da801ff407cf5ff047fceb82351724ad35985be298ffcb0e4ba1a53df051'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def run(args):
    result = subprocess.run(args, check=True, capture_output=True, text=True)
    return result.stdout


def verify(manifest):
    assert not SOURCE.is_symlink() and SOURCE.stat().st_size == 5457582
    assert sha(SOURCE) == EXPECTED
    n = manifest['training_count']
    assert 3 <= n <= 300 and n == manifest['source_frame_count'] // 2
    assert manifest['last_training_frame'] == n - 1
    assert manifest['suffix_first_frame'] == n < manifest['source_frame_count']
    pts_map = json.loads((OUT / 'presentation-map.json').read_text())
    assert len(pts_map['frames']) == manifest['source_frame_count']
    assert len(manifest['prefix']) == n
    assert not JPEG.is_symlink() and not JPEG.parent.is_symlink()
    assert {p.name for p in JPEG.iterdir()} == {f'{i:05d}.jpg' for i in range(n)}
    for i, row in enumerate(manifest['prefix']):
        path = JPEG / row['name']
        assert row['name'] == f'{i:05d}.jpg' and row['source_frame_index'] == i
        actual = pts_map['frames'][i]
        assert row['pts'] == actual['pts'] and row['pts_time'] == actual['pts_time']
        assert abs(Fraction(row['pts']) * Fraction(pts_map['time_base']) - Fraction(row['pts_time'])) <= Fraction(1, 1000000)
        assert path.is_file() and not path.is_symlink() and sha(path) == row['sha256']
        with Image.open(path) as image:
            assert image.format == 'JPEG' and image.size == (720, 1366)
            image.verify()
    frame_map = [(row['source_frame_index'], float(row['pts_time'])) for row in manifest['prefix']]
    _context(manifest['adapter_metadata'], frame_map, 0)
    # Negative boundary check reuses product validation without predictor/model calls.
    try:
        _context(manifest['adapter_metadata'], frame_map + [(n, float(manifest['first_suffix_pts_time']))], 0)
    except ValueError:
        pass
    else:
        raise AssertionError('suffix mapping accepted')
    assert 'torch' not in sys.modules and 'sam3' not in sys.modules
    return {'verified_utc': datetime.now(timezone.utc).isoformat(), 'jpeg_count': n,
            'source_hash': 'PASS', 'prefix_names_hashes_geometry_pts': 'PASS',
            'adapter_context_and_suffix_rejection': 'PASS', 'heavy_model_imports': False,
            'os_immutable_or_exclusive_lock': False}


def main():
    if sys.argv[1:] == ['--verify-only']:
        write('self-check.json', verify(json.loads((OUT / 'manifest.json').read_text())))
        return
    assert not sys.argv[1:], 'only --verify-only supported'
    assert not (OUT / 'manifest.json').exists() and not JPEG.exists(), 'never overwrite frozen resources'
    acquisition = json.loads((CANON / 'evidence/clips/S02c-acquisition.json').read_text(encoding='utf-8-sig'))
    entry, = [x for x in acquisition['files'] if x['clip_id'] == 'ST03']
    assert entry['sha256'] == EXPECTED and int(entry['probe']['format']['size']) == 5457582
    assert entry['licence'] == 'Pexels License' and not SOURCE.is_symlink()
    assert SOURCE.stat().st_size == 5457582 and sha(SOURCE) == EXPECTED
    write('source-verification.json', {'verified_before_decode_utc': datetime.now(timezone.utc).isoformat(),
          'path': str(SOURCE), 'sha256': EXPECTED, 'bytes': SOURCE.stat().st_size,
          'acquisition_record': entry, 'approval_receipt_sha256': sha(CANON / 'evidence/owner/S02/APPROVAL.md'),
          'scope': 'scene_tracking_only', 'raw_source_copy': False})
    probe_args = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_frames',
                  '-show_streams', '-show_entries',
                  'frame=pts,pts_time,best_effort_timestamp,width,height:stream=width,height,time_base,nb_frames',
                  '-of', 'json', str(SOURCE)]
    probe = json.loads(run(probe_args))
    frames = probe['frames']
    stream, = probe['streams']
    n = len(frames) // 2
    assert 3 <= n <= 300 and n < len(frames), 'front-half bound failed; do not change split'
    assert stream['width'] == 720 and stream['height'] == 1366
    assert all(f['width'] == 720 and f['height'] == 1366 and 'pts' in f and 'pts_time' in f for f in frames)
    assert all(int(a['pts']) < int(b['pts']) for a, b in zip(frames, frames[1:]))
    write('presentation-map.json', {'time_base': stream['time_base'], 'frames': [
        {'source_frame_index': i, 'pts': f['pts'], 'pts_time': f['pts_time']} for i, f in enumerate(frames)],
        'interpretation': 'container presentation timestamps only; capture clock unknown'})
    write('split-frozen.json', {'frozen_before_jpeg_decode_utc': datetime.now(timezone.utc).isoformat(),
          'selection': 'floor(decoded presentation frame count / 2), fixed before visual inspection',
          'source_frame_count': len(frames), 'training_count': n, 'last_training_frame': n - 1,
          'suffix_first_frame': n, 'suffix_count': len(frames) - n,
          'operational_split_not_physical_gate': True, 'source_sha256': EXPECTED})
    JPEG.mkdir(parents=True)
    decode_args = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', '-n',
                   '-threads', '1', '-noautorotate', '-i', str(SOURCE), '-map', '0:v:0', '-an',
                   '-vf', f'trim=end_frame={n}', '-frames:v', str(n), '-fps_mode', 'passthrough',
                   '-q:v', '2', '-start_number', '0', str(JPEG / '%05d.jpg')]
    write('commands.json', {'probe': probe_args, 'prefix_export': decode_args,
          'ffmpeg_version': run(['ffmpeg', '-version']).splitlines()[0],
          'ffprobe_version': run(['ffprobe', '-version']).splitlines()[0]})
    run(decode_args)
    manifest = {'source_sha256': EXPECTED, 'source_frame_count': len(frames), 'training_count': n,
                'last_training_frame': n - 1, 'suffix_first_frame': n,
                'first_suffix_pts_time': frames[n]['pts_time'], 'prefix_directory': str(JPEG),
                'adapter_metadata': {'clip_id': 'ST03', 'licence': 'Pexels License',
                    'provenance': 'clips.csv; evidence/clips/S02c-acquisition.json; source-verification.json',
                    'motion': 'free_fall', 'source_sha256': EXPECTED,
                    'approval': {'scope': 'scene_tracking', 'evidence': 'evidence/owner/S02/APPROVAL.md'},
                    'width_px': 720, 'height_px': 1366, 'last_training_frame': n - 1,
                    'capture_clock': None, 'physical_scale': None},
                'prefix': [{'name': f'{i:05d}.jpg', 'source_frame_index': i, 'pts': f['pts'],
                            'pts_time': f['pts_time'], 'sha256': sha(JPEG / f'{i:05d}.jpg'),
                            'width_px': 720, 'height_px': 1366} for i, f in enumerate(frames[:n])],
                'custody': {'suffix_exported': False, 'predictor_called': False,
                            'source_custodian': str(SOURCE), 'os_immutable_or_exclusive_lock': False}}
    write('manifest.json', manifest)
    write('self-check.json', verify(manifest))


if __name__ == '__main__':
    main()
