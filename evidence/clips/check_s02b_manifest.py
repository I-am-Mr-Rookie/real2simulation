"""Check candidate coverage and conservative status, not footage usability."""
import csv
from pathlib import Path
from urllib.parse import urlparse

root = Path(__file__).resolve().parents[2]
with (root / 'clips.csv').open(encoding='utf-8', newline='') as f:
    rows = list(csv.DictReader(f))
assert all(None not in row for row in rows)
assert len({r['clip_id'] for r in rows}) == len(rows)
selected = [r for r in rows if r['clip_id'] in {'PJ01','BN01','PD01','RM01','RM02','RM03'}]
assert len(selected) == 6
assert {r['experiment'] for r in selected} == {'projectile','bounce','pendulum','room_scene'}
assert sum(r['experiment'] == 'room_scene' for r in selected) == 3
assert len({r['capture_group'] for r in selected}) == 6
for row in selected:
    assert row['status'] == 'UNAPPROVED_CANDIDATE' and row['owner_approved'] == 'NO'
    assert not row['scale_value_m']
    if row['local_path']:
        assert (root / row['local_path']).is_file(), (row['clip_id'], 'missing file')
    assert row['licence'] in {'CC-BY-SA-4.0','Pexels'}
    for k in ('source_url','original_source_url','licence_url'):
        assert urlparse(row[k]).scheme == 'https'
    for k in ('creator','attribution','adaptation_notes','scale_status','timebase_status','suitability'):
        assert row[k], (row['clip_id'],k)
    assert (root / row['evidence_path'].split('#')[0]).is_file()
print('PASS: 3 motion candidates and 3 distinct room-source candidates; provenance fields and unapproved status')
print('NOT VERIFIED: playback, actual media rights beyond source declarations, calibration, owner approval, gates')
