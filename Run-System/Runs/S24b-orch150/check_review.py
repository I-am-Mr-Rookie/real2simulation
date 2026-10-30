"""S24b-orch150 review check: run from repo root. Reruns S24a check, then asserts S24b claim/credit fixes."""
import csv, pathlib, runpy

runpy.run_path('Run-System/Runs/S24a-orch146/check_script.py')
S = pathlib.Path('media/script/DEMO_SCRIPT_DRAFT.md').read_text(encoding='utf-8')
A = pathlib.Path('ATTRIBUTION.md').read_text(encoding='utf-8')
for need in ['MET_AMENDED_Q16 — scale unverified, not setup-validated', 'Gate M: NOT_MET', 'Gate RS: NOT_MET',
             'Metric scale: ABSTAINED', 'Meta cost UNAVAILABLE', '"4 public clips" library fallback: NOT met',
             'open-weight bonus NOT claimed', 'muse-wonder-1.0', 'meta-models/muse-spark-open-1026', 'SAM 3.1',
             'PENDING owner Q19', 'plots', 'Gate D', 'Built Oct 27 – Nov 4']:
    assert need in S, need
assert 'UNKNOWN' not in S
rows = {r['clip_id']: r for r in csv.DictReader(open('clips.csv', encoding='utf-8'))}
for cid in ('PD02', 'RM02', 'ST03'):
    r = rows[cid]
    assert r['attribution'].split(' - Pexels')[0] in S, cid  # shot-list credit = clips.csv attribution
    assert f"| {cid} | {r['creator']} — {r['title']}" in A and 'Pexels License' in A, cid  # ATTRIBUTION agrees
    assert f"{r['creator']} — {r['title']}" in S, cid  # end-card credit block
print('PASS S24b review: labels, model limits, Q19/Gate D pending, 3 credit lines match clips.csv + ATTRIBUTION.md')
