"""Integrity/attribution checks; never substitutes for trackability or owner approval."""
import csv
import hashlib
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
rows = {r['clip_id']: r for r in csv.DictReader((root / 'clips.csv').open(encoding='utf-8', newline=''))}
receipt = json.loads((root / 'evidence/clips/S02c-acquisition.json').read_text(encoding='utf-8'))
for item in receipt['files']:
    row = rows[item['clip_id']]
    for key in ('source_url', 'download_url', 'creator', 'licence', 'licence_url', 'attribution', 'local_path'):
        assert row[key], (row['clip_id'], key)
    assert row['owner_approved'] == 'NO' and row['status'] == 'UNAPPROVED_CANDIDATE'
    assert row['local_path'] == item['local_path'] and row['download_url'] == item['download_url']
    path = (root / row['local_path']).resolve()
    assert path.is_relative_to((root / 'test-data/public').resolve()) and path.is_file()
    assert hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256']
assert len(receipt['files']) == sum(bool(r['local_path']) for r in rows.values())
print(f"PASS: {len(receipt['files'])} local files match receipt and have attribution; unapproved")
print('NOT VERIFIED: 10 usable clips, physical calibration, full motion suitability, owner approval')
if '--require-ten' in sys.argv:
    verified = [item for item in receipt['files'] if item.get('usability_verified') is True
                and item.get('usability_evidence')
                and (root / item['usability_evidence']).is_file()]
    if len(verified) < 10:
        sys.exit(f"FAIL: {len(verified)}/10 individually usability-verified files; {len(receipt['files'])} local candidates")
