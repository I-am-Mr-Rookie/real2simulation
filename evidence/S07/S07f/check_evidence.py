"""Offline S07f evidence cross-check; no physical fitting or approval grants."""
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from Build.measurement.gate_m import evaluate_sources, summarize

CANONICAL = Path('C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon')
HERE = Path(__file__).resolve().parent
before = json.loads((HERE/'actual-gate-m-before.json').read_text())
after = json.loads((HERE/'actual-gate-m.json').read_text())
assert evaluate_sources(ROOT) == after, 'stale actual-source artifact'
keys = ('evidence_kind', 'approval_receipt_recognized', 'latest_rp01_readiness',
        'approval_scope', 'candidate_count', 'scene_tracking_approved_count',
        'metric_approved_count', 'eligible_count', 'trials', 'gate')
assert all(before[k] == after[k] for k in keys), 'actual-source outcome changed'
assert after['gate']['physics_evaluation'] == 'NOT_RUN'
assert after['metric_approved_count'] == after['eligible_count'] == after['gate']['measured_count'] == 0
assert not after['gate']['gate_passed']
assert all(t[k] is None for t in after['trials']
           for k in ('g_m_s2', 'relative_error', 'uncertainty_covers_reference'))

owned_edits = {'Build/measurement/gate_m.py', 'Build/measurement/UNCERTAINTY.md'}
checks = {}
for name in after['sources_sha256']:
    local, live = (ROOT/name).read_bytes(), (CANONICAL/name).read_bytes()
    normalized_match = local.replace(b'\r\n', b'\n') == live.replace(b'\r\n', b'\n')
    checks[name] = dict(worktree_sha256=hashlib.sha256(local).hexdigest(),
                        canonical_sha256=hashlib.sha256(live).hexdigest(),
                        byte_match=local == live, normalized_match=normalized_match,
                        owned_edit=name in owned_edits)
    assert normalized_match or name in owned_edits, f'canonical drift: {name}'

with (ROOT/'clips.csv').open(encoding='utf-8-sig', newline='') as stream:
    ap15 = next(row for row in csv.DictReader(stream) if row['clip_id'] == 'AP15')
receipt = (ROOT/'evidence/owner/S02/APPROVAL.md').read_text()
audit = (ROOT/'evidence/clips/S02d-metadata-scale-audit.md').read_text()
assert 'AP15 NOT_TRACKABLE' in receipt and 'AP15 remains NOT_TRACKABLE' in audit

panel = [dict(g_m_s2=20., relative_error=0., uncertainty_covers_reference=True,
              capture_group=str(i), blockers=[]) for i in range(3)]
f1 = summarize(panel, independence_verified=True)
assert not f1['gate_passed'] and f1['qualifying_count'] == 0
rb = json.loads((HERE/'review-repro-before.json').read_text())
ra = json.loads((HERE/'review-repro-after.json').read_text())
assert rb['F1_inconsistent_trials_pass'][1] is True and ra['F1_inconsistent_trials_pass'][1] is False
assert rb['F2_alias_groups'][1] is True and ra['F2_alias_groups'] == [0, False]
assert all(rb[k] == ra[k] for k in rb if not k.startswith(('F1', 'F2')))

result = dict(actual_source_result_unchanged=True, source_integrity=checks,
    f1_with_external_independence_verification=f1,
    review_F3_through_F6_and_math_checks_unchanged=True,
    apollo=dict(clip_id=ap15['clip_id'], source_status='NOT_TRACKABLE',
                physics_evaluation='NOT_RUN', g_m_s2=None, relative_error=None,
                uncertainty_covers_reference=None, scale_status=ap15['scale_status'],
                timebase_status=ap15['timebase_status'], owner_metric_approved=False),
    table_plane_fallback='UNAVAILABLE', S12_unlocked=False)
(HERE/'verification.json').write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+'\n')
print(f'PASS: {len(checks)} source fingerprints checked; canonical differences only owned edits/EOL.')
print('PASS: actual-source outcome unchanged; F1 denied even with verified independence; F3-F6/math unchanged.')
print('AP15 NOT_RUN; no calibrated table-plane fallback or S12 unlock.')
