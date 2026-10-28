"""Run the real Python/Node acceptance and replay paths without overwriting prior evidence."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from Build.lab.acceptance import run_acceptance
from Build.lab.regression import run_regression

destination = Path(__file__).resolve().parent
acceptance = run_acceptance(write_evidence=False)
regression = run_regression()
for name, result in [('acceptance', acceptance), ('regression', regression)]:
    (destination / f'{name}.json').write_text(
        json.dumps(result, allow_nan=False, indent=2) + '\n', encoding='utf-8')
    assert result['threshold'] == 0.005, result
    assert result['passed'], result
    assert all(case['deterministic'] and case['replay']['deterministic']
               and case['replay']['seedBound'] for case in result['cases']), result
assert acceptance['case_counts'] == {'authored': 15, 'passed': 15, 'failed': 0, 'rejected': 0}
contact = acceptance['contact_diagnostic']
assert contact['status'] == 'measured' and len(contact['rows']) == 6, contact
assert not contact['assessment']['contact_jitter_observed'], contact
assert not contact['assessment']['fallback_observed'], contact
assert all(row['status'] == 'contact_observed'
           and row['contact_bracket_s'][0] <= row['expected_contact_time_s'] <= row['contact_bracket_s'][1]
           for row in contact['rows']), contact
print(json.dumps({'acceptance': acceptance['case_counts'],
                  'regression_cases': len(regression['cases']), 'threshold': 0.005,
                  'actual_replay_deterministic_and_seed_bound': True,
                  'contact_cases': len(contact['rows']), 'jitter_observed': False,
                  'scope': 'synthetic only; no contact response or physical/real-scene gate'}, indent=2))
