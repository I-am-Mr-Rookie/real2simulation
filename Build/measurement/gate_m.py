"""Offline Gate M: actual-source readiness, never self-authorized measurements."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

from .inputs import validate_input
from .free_fall import fit_free_fall, evaluate_held_out, FitAbstention
from .uncertainty import propagate_uncertainty


REFERENCE_G = 9.81  # Comparison ONLY; never passed into calibration or fitting.
REQUIRED_TRIALS = 3
REQUIRED_SUCCESSES = 2
MAX_RELATIVE_ERROR = .05
# Reviewed S02e receipt grants ONLY scene/tracking, never metric processing.
SCENE_RECEIPT_SHA256 = 'caa5f27093d8bcacd6fcf96cfe43719ef037dd06b86b8c8c2c22da04c4cc74e8'
SCENE_IDS = frozenset('RM02 RM04 RM05 PD02 PD03 PD04 PD06 PJ03 ST03 BN01'.split())


def _empty(clip_id, blockers=()):
    return dict(clip_id=clip_id, capture_group=None, eligible=False,
                g_m_s2=None, relative_error=None, standard_uncertainty_m_s2=None,
                held_out_rmse_m=None, uncertainty_covers_reference=None,
                blockers=list(blockers))


def evaluate_record(data, assumptions, *, metric_authorized=False,
                    custody_verified=False):
    """Trusted caller must authenticate rights/calibration/custody OUTSIDE data.

    Defaults deny; a nonempty approval/evidence string never authorizes a fit.
    The actual-source CLI never sets these flags true under current receipts.
    Tests can explicitly exercise fitter mechanics with synthetic inputs.
    """
    out = _empty(data.get('clip_id') if isinstance(data, dict) else None)
    if metric_authorized is not True:
        out['blockers'].append('metric_use_not_authorized_by_receipt')
    if custody_verified is not True:
        out['blockers'].append('held_out_custody_unverified')
    try:
        parsed = validate_input(data)
        out['blockers'].extend(parsed.blockers)
    except ValueError as error:
        out['blockers'].append(f'invalid_input: {error}')
    if out['blockers']:
        return out
    out['eligible'] = True
    try:
        fitted = fit_free_fall(data)
        uncertainty = propagate_uncertainty(data, assumptions)
        held_out = evaluate_held_out(fitted, data)
    except FitAbstention as error:
        out['blockers'].extend(error.blockers)
        return out
    except ValueError as error:
        out['blockers'].append(f'invalid_uncertainty_or_evaluation: {error}')
        return out
    out.update(g_m_s2=fitted.g_m_s2,
               relative_error=abs(fitted.g_m_s2-REFERENCE_G)/REFERENCE_G,
               standard_uncertainty_m_s2=uncertainty.standard_uncertainty_m_s2,
               held_out_rmse_m=held_out.rmse_m)
    # S07d explicitly provides NO coverage interval. Do not invent k=1/1.96/2.
    out['blockers'].append('coverage_not_established_by_standard_uncertainty')
    return out


def summarize(trials, *, independence_verified=False):
    """Summarize a fixed three-trial panel, never choose the best three or divide
    by only successes. Outcome fixtures used by tests are not production grants.

    Trusted caller must authenticate this exact panel's independent recordings
    OUTSIDE outcome dictionaries. Raw labels cannot prove capture provenance.
    IDs are case-sensitive and canonical (no surrounding whitespace).
    """
    measured = [t for t in trials if type(t.get('g_m_s2')) in (int, float)
                and math.isfinite(t['g_m_s2'])]
    groups = [t.get('capture_group') for t in measured]
    independent = (len({g for g in groups
                        if isinstance(g, str) and g and g == g.strip()})
                   if independence_verified is True else 0)
    # Compare g directly: division can round the inclusive 5% edge above .05.
    good = [t for t in measured
            if REFERENCE_G*(1-MAX_RELATIVE_ERROR) <= t['g_m_s2']
               <= REFERENCE_G*(1+MAX_RELATIVE_ERROR)
            and t.get('uncertainty_covers_reference') is True
            and not t.get('blockers')]
    passed = (len(trials) == REQUIRED_TRIALS and len(measured) == REQUIRED_TRIALS
              and independent == REQUIRED_TRIALS and len(good) >= REQUIRED_SUCCESSES)
    coverage = ([t['uncertainty_covers_reference'] for t in measured]
                if measured and all(type(t.get('uncertainty_covers_reference')) is bool
                                    for t in measured) else None)
    return dict(status='PASSED' if passed else
                'NOT_MET_INPUT_READINESS' if not measured else 'NOT_MET',
                physics_evaluation='NOT_RUN' if not measured else 'EVALUATED',
                gate_passed=passed, required_trials=REQUIRED_TRIALS,
                required_successes=REQUIRED_SUCCESSES,
                max_relative_error=MAX_RELATIVE_ERROR, reference_g_m_s2=REFERENCE_G,
                measured_count=len(measured), independent_measured_count=independent,
                qualifying_count=len(good), coverage=coverage,
                mean_g_m_s2=math.fsum(t['g_m_s2']/len(measured) for t in measured)
                if measured else None,
                mean_relative_error=math.fsum(abs(t['g_m_s2']-REFERENCE_G)
                                             /REFERENCE_G/len(measured)
                                             for t in measured)
                if measured else None)


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scene_approval_ids(text):
    """Ignore Windows checkout EOL translation, never semantic receipt changes."""
    normalized = hashlib.sha256(text.replace('\r\n', '\n').encode('utf-8')).hexdigest()
    return SCENE_IDS if normalized == SCENE_RECEIPT_SHA256 else frozenset()


def evaluate_sources(root):
    """Evaluate current manifest and reviewed receipts, not old summary counts.

    Current source set has no metric-authorized input. No decoding/tracking or
    fabricated empty-frame TrackingInput is needed to establish that abstention.
    Unknown/changed approval receipts fail closed pending review, not promotion.
    """
    root = Path(root)
    receipt = 'evidence/owner/S02/APPROVAL.md'
    candidates_path = 'evidence/clips/calibration-recovery/S02f/candidates.json'
    sources = [
        'clips.csv', receipt, candidates_path,
        'evidence/S07/S07a-candidates.json', 'evidence/S07/S07a-input-audit.md',
        'evidence/clips/S02d-metadata-scale-audit.md',
        'evidence/clips/calibration-recovery/S02i/segments.json',
        'evidence/clips/calibration-recovery/S02i/RESEARCH.md',
        'Run-System/Runs/S02f/REPORT.md', 'Run-System/Runs/S02i/REPORT.md',
        'Build/measurement/inputs.py', 'Build/measurement/tracking.py',
        'Build/measurement/free_fall.py', 'Build/measurement/uncertainty.py',
        'Build/measurement/UNCERTAINTY.md', 'Build/measurement/gate_m.py',
    ]
    hashes = {name: _sha(root / name) for name in sources}
    latest_rp01 = json.loads((root/'evidence/clips/calibration-recovery/S02i/segments.json')
                            .read_text(encoding='utf-8'))
    scene_ids = scene_approval_ids((root/receipt).read_text(encoding='utf-8'))
    recognized = bool(scene_ids)
    with (root/'clips.csv').open(encoding='utf-8-sig', newline='') as stream:
        rows = [r for r in csv.DictReader(stream) if r['experiment'] == 'free_fall']
    replacements = json.loads((root/candidates_path).read_text(encoding='utf-8'))
    trials = []
    for row in rows:
        trial = _empty(row['clip_id'], [
            'metric_use_not_authorized_by_receipt',
            'independent_scale_not_verified', 'capture_timebase_not_verified',
            'no_custody_sealed_tracking_input', 'uncertainty_assumptions_not_verified',
        ])
        trial.update(capture_group=row['capture_group'],
                     scene_tracking_approved=row['clip_id'] in scene_ids,
                     metric_approved=False, source_url=row['source_url'],
                     licence=row['licence'], local_path_declared=row['local_path'],
                     scale_status=row['scale_status'], timebase_status=row['timebase_status'],
                     source_evidence=row['evidence_path'], origin='current_clips_csv')
        if not recognized:
            trial['blockers'].append('unrecognized_approval_receipt')
        trials.append(trial)
    for row in replacements['candidates']:
        trial = _empty(row['id'], [
            'outside_scoped_owner_approval', 'metric_use_not_authorized_by_receipt',
            'no_custody_sealed_tracking_input',
            'capture_timebase_not_verified', 'metric_projection_not_verified',
        ])
        trial.update(capture_group=row['capture_group'], scene_tracking_approved=False,
                     metric_approved=False, source_url=row['source_url'],
                     licence=row['license'], source_sha256=row['sha256'],
                     origin='review_only_S02f_replacement',
                     note='RP01 partial flight is useful; full floor contact is NOT required. '
                          'S02i still leaves capture clock and projection unresolved.'
                          if row['id'] == 'RP01' else row['disposition'])
        trials.append(trial)
    return dict(evidence_kind='actual_source_readiness_evaluation',
                sources_sha256=hashes, approval_receipt_recognized=recognized,
                latest_rp01_readiness={key: latest_rp01[key] for key in (
                    'metric_qualified', 'camera_capture_fps',
                    'capture_to_presentation_mapping', 'metric_scale_m_per_pixel',
                    'scale_uncertainty', 'perspective_uncertainty',
                    'physical_time_uncertainty', 'owner_metric_approval')},
                approval_scope='scene_tracking_only' if recognized else 'unknown_deny',
                candidate_count=len(trials),
                scene_tracking_approved_count=sum(t['scene_tracking_approved'] for t in trials),
                metric_approved_count=sum(t['metric_approved'] for t in trials),
                eligible_count=sum(t['eligible'] for t in trials),
                trials=trials, gate=summarize(trials),
                limitations=[
                    'Input-readiness acceptance NOT MET; not a measured accuracy failure.',
                    'No real tracks, fitter result, interval or empirical coverage exists.',
                    'Raw media not opened/hashed; candidate source hashes are prior receipts.',
                    'Current recognized approval has zero metric grants; CLI never fits.',
                    'Future metric receipt/input support requires explicit reviewed integration.',
                    'S07d standard uncertainty alone cannot establish covering uncertainty.',
                    'Other-vendor follow-up of S07f gate changes remains required.',
                    'No calibrated table-plane fallback activated; parent S07 and S12 not unlocked.',
                ])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    artifact = evaluate_sources(args.root)
    args.output.write_text(json.dumps(artifact, indent=2, sort_keys=True, allow_nan=False)+'\n',
                           encoding='utf-8')
    print(f"Gate M {artifact['gate']['status']}; eligible={artifact['eligible_count']}; "
          f"measured={artifact['gate']['measured_count']}/3")
    return 0 if artifact['gate']['gate_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
