"""Record locally downloaded source files; does not approve or qualify footage."""
import csv
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / 'clips.csv'
RECEIPT = ROOT / 'evidence/clips/S02c-acquisition.json'
existing = {x['clip_id']: x for x in json.loads(RECEIPT.read_text(encoding='utf-8')).get('files', [])} if RECEIPT.exists() else {}
MEDIA = {
    'FF01': ('FF01.webm', None),
    'FF02': ('FF02.webm', None),
    'AP15': ('AP15.m4v', None),
    'PJ01': ('PJ01.webm', 'https://upload.wikimedia.org/wikipedia/commons/6/61/Wurfparabel_%28Raketenflug%29.webm'),
    'BN01': ('BN01.webm', 'https://upload.wikimedia.org/wikipedia/commons/1/1d/Bouncy_ball_240fps.webm'),
    'PD01': ('PD01.webm', 'https://upload.wikimedia.org/wikipedia/commons/f/f7/Fadenpendelgeschwindigkeit_%282_grad%29.webm'),
    'BN02': ('BN02.webm', 'https://upload.wikimedia.org/wikipedia/commons/9/9a/Gymnastikball-Flummi.webm'),
    'RM02': ('RM02.mp4', 'https://www.pexels.com/download/video/6671552/'),
    'RM04': ('RM04.mp4', 'https://www.pexels.com/download/video/8342689/'),
    'PD02': ('PD02.mp4', 'https://www.pexels.com/download/video/35640361/'),
    'PD03': ('PD03.mp4', 'https://www.pexels.com/download/video/6613341/'),
}

with MANIFEST.open(encoding='utf-8', newline='') as f:
    reader = csv.DictReader(f)
    fields, rows = reader.fieldnames, list(reader)
if not any(r['clip_id'] == 'BN02' for r in rows):
    row = dict.fromkeys(fields, '')
    row.update(clip_id='BN02', experiment='bounce', title='Gymnastikball-Flummi',
        source_url='https://commons.wikimedia.org/wiki/File:Gymnastikball-Flummi.webm',
        original_source_url='https://www.rhetos.de/html/lex/flummiversuche.htm',
        creator='Rhetos', licence='CC-BY-SA-4.0', licence_url='https://creativecommons.org/licenses/by-sa/4.0/',
        attribution='Rhetos - Gymnastikball-Flummi - Wikimedia Commons - CC BY-SA 4.0',
        adaptation_notes='Identify edits; share adaptations under same or compatible licence',
        status='UNAPPROVED_CANDIDATE', owner_approved='NO', source_duration_label='41 s',
        source_resolution='1920x1080', scale_reference='Ball diameter unverified', scale_status='UNVERIFIED',
        timebase_status='SLOW_MOTION_FACTOR_AND_SEGMENTS_UNKNOWN',
        suitability='Exercise ball bounce; includes frame-by-frame segments; continuous motion and scale unverified',
        capture_group='RHETOS_GYMBALL_2025', evidence_path='evidence/clips/S02c-sourcing.md')
    rows.append(row)
new_sources = [
    ('RM04', 'scene', 'An Empty Classroom', 'an-empty-classroom-8342689', 'Pavel Danilyuk', '9 s', '3840x2160', 'SCENE_ONLY', 'Zoom-dominant classroom; weak translation/parallax, third-party wall art; reconstruction and rights review required'),
    ('PD02', 'pendulum', 'Foucault Pendulum Swing in Grand Hall', 'foucault-pendulum-swing-in-grand-hall-35640361', 'Alexandre Henry Alves', '14 s', '1920x1080', 'UNVERIFIED', 'Visible bob; no pivot or independent scale; people/depicted rights require review'),
    ('PD03', 'pendulum', 'A Swinging Pendulum', 'a-swinging-pendulum-6613341', 'Engin Akyurt', 'unknown', 'unknown', 'UNVERIFIED', 'Newton cradle motion visible; source describes slow motion; unknown capture factor and scale'),
]
for ident, kind, title, slug, author, duration, resolution, scale_status, suitability in new_sources:
    if any(r['clip_id'] == ident for r in rows):
        continue
    row = dict.fromkeys(fields, '')
    row.update(clip_id=ident, experiment=kind, title=title,
        source_url='https://www.pexels.com/video/' + slug + '/',
        original_source_url='https://www.pexels.com/video/' + slug + '/', creator=author,
        licence='Pexels License', licence_url='https://www.pexels.com/license/',
        attribution=author + ' - ' + title + ' - Pexels',
        adaptation_notes='Check Pexels restrictions and third-party rights before distribution',
        status='UNAPPROVED_CANDIDATE', owner_approved='NO', source_duration_label=duration,
        source_resolution=resolution, scale_reference='No independently verified reference size',
        scale_status=scale_status, timebase_status='CAPTURE_TIMEBASE_UNVERIFIED',
        suitability=suitability, capture_group=ident, evidence_path='evidence/clips/S02c-alternate-sources.md')
    rows.append(row)
receipts = []
for row in rows:
    if row['clip_id'] not in MEDIA:
        continue
    filename, url = MEDIA[row['clip_id']]
    path = ROOT / 'test-data/public' / filename
    if not path.is_file():
        continue
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries',
        'format=duration,size:stream=codec_type,codec_name,avg_frame_rate,width,height', '-of', 'json', str(path)]))
    video = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    assert float(probe['format']['duration']) > 0 and int(probe['format']['size']) == path.stat().st_size
    if url:
        row['download_url'] = url
    row['local_path'] = f'test-data/public/{filename}'
    row['file_fps'] = video['avg_frame_rate']
    row['file_duration_s'] = probe['format']['duration']
    item = {'clip_id': row['clip_id'], 'local_path': row['local_path'],
        'source_url': row['source_url'], 'download_url': row['download_url'],
        'licence': row['licence'], 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'probe': probe}
    old = existing.get(row['clip_id'], {})
    # Preserve narrow visual evidence only if the underlying source file is unchanged.
    if old.get('sha256') == item['sha256']:
        for key in ('usability_verified', 'usability_evidence', 'usability_scope'):
            if key in old:
                item[key] = old[key]
    receipts.append(item)
with MANIFEST.open('w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
RECEIPT.write_text(json.dumps({'files': receipts}, indent=2) + '\n', encoding='utf-8')
print(f'Recorded {len(receipts)} local files; all remain unapproved; retained evidence applies only to matching hashes')
