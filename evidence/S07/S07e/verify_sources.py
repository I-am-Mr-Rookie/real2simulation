"""Check only evaluator-owned artifact and its explicit non-secret source list."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--canonical', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    folder = Path(__file__).resolve().parent
    artifact = json.loads((folder/'actual-gate-m.json').read_text(encoding='utf-8'))
    results = []
    for name, expected in artifact['sources_sha256'].items():
        local = (root/name).resolve()
        canonical = (args.canonical/name).resolve()
        assert local.is_relative_to(root)
        assert canonical.is_relative_to(args.canonical.resolve())
        current = local.read_bytes()
        assert hashlib.sha256(current).hexdigest() == expected, name
        if name == 'Build/measurement/gate_m.py':
            results.append(dict(path=name, artifact_hash_matches=True,
                                canonical_comparison='new owned implementation'))
            continue
        original = canonical.read_bytes()
        normalized_match = current.replace(b'\r\n', b'\n') == original.replace(b'\r\n', b'\n')
        assert normalized_match, f'canonical semantic drift: {name}'
        results.append(dict(path=name, artifact_hash_matches=True,
                            canonical_bytes_match=current == original,
                            canonical_text_matches_after_eol_normalization=normalized_match,
                            canonical_sha256=hashlib.sha256(original).hexdigest()))
    assert artifact['scene_tracking_approved_count'] == 1
    assert artifact['metric_approved_count'] == artifact['eligible_count'] == 0
    assert artifact['gate']['measured_count'] == 0
    assert artifact['gate']['required_trials'] == 3
    assert artifact['gate']['required_successes'] == 2
    assert artifact['gate']['max_relative_error'] == .05
    assert artifact['gate']['mean_g_m_s2'] is None
    assert artifact['gate']['mean_relative_error'] is None
    assert artifact['gate']['coverage'] is None
    assert artifact['latest_rp01_readiness']['metric_qualified'] is False
    assert artifact['latest_rp01_readiness']['capture_to_presentation_mapping'] is None
    assert not artifact['gate']['gate_passed']
    for trial in artifact['trials']:
        assert not trial['eligible'] and trial['blockers']
        assert trial['g_m_s2'] is trial['relative_error'] is trial['uncertainty_covers_reference'] is None
    result = dict(status='PASS', comparison='source evidence only; no media read',
                  sources=results)
    (folder/'source-integrity.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(f'Source-integrity PASS: {len(results)} hashes; canonical evidence content matches')


if __name__ == '__main__':
    main()
