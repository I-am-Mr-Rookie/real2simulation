"""S24a-orch146 re-quote check: run from repo root. Links resolve; every quoted value is in evidence; timing = 180 s."""
import itertools, json, os, pathlib, re

S = pathlib.Path('media/script/DEMO_SCRIPT_DRAFT.md').read_text(encoding='utf-8')
SRC = ''.join(pathlib.Path(p).read_text(encoding='utf-8', errors='ignore') for p in [
    'BENCHMARK.md', 'evidence/S14/GATE_A.json', 'evidence/S16/S16e-orch108-live.json',
    'evidence/S14/S14g-fix3-live.json', 'evidence/S12/gate-rs/gate-rs.json',
    'evidence/S21/S21b-errors.json', 'evidence/S21/S21c-predictions.json', 'evidence/S21/S21d-costs.json'])
links = {l for l in re.findall(r'\]\((\.\./[^)#]+?(?:\(public\)[^)#]*)?)\)', S)}
missing = [l for l in links if not os.path.exists(os.path.normpath(os.path.join('media/script', l)))]
assert not missing, missing
model_names = {'1.0', '1.3', '3.1'}  # Muse Wonder 1.0 / Spark 1.3, SAM 3.1
bad = [n for n in set(re.findall(r'\d+\.\d+', S)) - model_names if n not in SRC]
assert not bad, bad
g = json.load(open('evidence/S14/GATE_A.json')); c = g['counts']
assert (g['verdict'], g['label']) == ('MET_AMENDED_Q16', 'scale unverified, not setup-validated')
assert [c[k]['value'] for k in ('numeric_contract_valid_specs', 'setup_validator_valid_specs', 'replay_turns_shown_unchanged', 'oracle_flagged_shown_inventions')] == ['10/10', '0/10', '30/30', 0]
d = json.load(open('evidence/S16/S16e-orch108-live.json'))
assert d['request_count'] == 1 and d['cost_usd'] is None and d['usage_measured']['total_tokens'] == 1176
p = json.load(open('evidence/S07/S07-chunktrack-orch67/PD02-summary.json'))
assert p['frames_observed'] == p['frames_total'] == 439 and 'A10G' in p['gpu']
f = json.load(open('evidence/S14/S14g-fix3-live.json'))['summary']
assert (f['spark_calls'], f['wonder_calls']) == (30, 10)
assert '7/466' in SRC and 'This is not a blind test.' in pathlib.Path('Build/web/src/app/(public)/library/library-copy.mjs').read_text(encoding='utf-8')
t = [12, 28, 20, 25, 25, 25, 20, 15, 10]
starts = [int(a) * 60 + int(b) for a, b in re.findall(r'^\[(\d):(\d\d)\]', S, re.M)]
assert sum(t) == 180 and starts == list(itertools.accumulate([0] + t[:-1])), starts
print(f'PASS links={len(links)} decimals_checked timing=180 captions={len(starts)}')

