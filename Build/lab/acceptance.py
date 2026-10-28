"""Expanded synthetic S10 analytic/replay acceptance.

This orchestrates the existing S08 factories/oracles and S10 Node transports.
It deliberately records every authored case, including rejected or unavailable
cases, and never turns this simulation-only evidence into a physical/UI gate.
"""
import importlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Build.lab.regression import quantity
from Build.simulator.export_validated_setup import export
THRESHOLD = 0.005
SCALE_EPSILON_M = 1e-12
MAX_STEPS = 100_000


def _q(value, unit):
    return quantity(value, unit)


def _case(template, name, *, gravity, duration, time_step, parameters,
          seed=42):
    return {
        'template': template,
        'case': name,
        'gravity': gravity,
        'duration': duration,
        'time_step': time_step,
        'parameters': parameters,
        'seed': seed,
    }


def _ramp_end_time(gravity, length, angle, friction, initial_speed):
    acceleration = gravity * (math.sin(angle) - friction * math.cos(angle))
    if not math.isfinite(acceleration) or acceleration <= 0:
        raise ValueError('ramp case requires positive supported acceleration')
    speed = math.sqrt(initial_speed ** 2 + 2 * acceleration * length)
    return length / ((initial_speed + speed) / 2)


def case_matrix():
    """Return authored, valid-domain cases; no case is selected by its result."""
    ramp_end = _ramp_end_time(9.81, 1.0, 0.5, 0.1, 0.0)
    ramp_pre_end = math.floor((ramp_end - 0.001) / 0.001) * 0.001
    return [
        _case('free_fall', 'baseline-short', gravity=9.81, duration=0.2,
              time_step=0.001,
              parameters={'drop_height': _q(1.0, 'm'),
                          'initial_vertical_velocity': _q(0.0, 'm/s')}),
        _case('free_fall', 'upward-launch', gravity=9.81, duration=0.4,
              time_step=0.002,
              parameters={'drop_height': _q(1.0, 'm'),
                          'initial_vertical_velocity': _q(2.0, 'm/s')}, seed=43),
        _case('free_fall', 'tiny-height', gravity=9.81, duration=0.02,
              time_step=0.0001,
              parameters={'drop_height': _q(0.01, 'm'),
                          'initial_vertical_velocity': _q(0.0, 'm/s')}, seed=44),
        _case('free_fall', 'low-gravity-long-horizon', gravity=3.7,
              duration=0.35, time_step=0.001,
              parameters={'drop_height': _q(0.5, 'm'),
                          'initial_vertical_velocity': _q(-0.5, 'm/s')}, seed=45),
        _case('projectile', 'baseline-short', gravity=9.81, duration=0.2,
              time_step=0.001,
              parameters={'launch_height': _q(1.0, 'm'),
                          'horizontal_speed': _q(1.0, 'm/s')}),
        _case('projectile', 'zero-horizontal', gravity=9.81, duration=0.4,
              time_step=0.002,
              parameters={'launch_height': _q(1.0, 'm'),
                          'horizontal_speed': _q(0.0, 'm/s')}, seed=46),
        _case('projectile', 'tiny-height', gravity=9.81, duration=0.03,
              time_step=0.0001,
              parameters={'launch_height': _q(0.01, 'm'),
                          'horizontal_speed': _q(0.25, 'm/s')}, seed=47),
        _case('projectile', 'low-gravity-long-horizon', gravity=3.7,
              duration=0.4, time_step=0.001,
              parameters={'launch_height': _q(0.5, 'm'),
                          'horizontal_speed': _q(0.0, 'm/s')}, seed=48),
        _case('ramp', 'short-supported-acceleration', gravity=9.81,
              duration=0.1, time_step=0.001,
              parameters={'length': _q(1.0, 'm'),
                          'incline_angle': _q(0.5, 'rad'),
                          'friction_coefficient': _q(0.1, '1'),
                          'initial_speed': _q(0.0, 'm/s')}),
        _case('ramp', 'endpoint-preflight', gravity=9.81,
              duration=ramp_pre_end, time_step=0.001,
              parameters={'length': _q(1.0, 'm'),
                          'incline_angle': _q(0.5, 'rad'),
                          'friction_coefficient': _q(0.1, '1'),
                          'initial_speed': _q(0.0, 'm/s')}, seed=49),
        _case('ramp', 'low-gravity-moving-start', gravity=3.7,
              duration=0.3, time_step=0.001,
              parameters={'length': _q(0.5, 'm'),
                          'incline_angle': _q(0.7, 'rad'),
                          'friction_coefficient': _q(0.05, '1'),
                          'initial_speed': _q(0.1, 'm/s')}, seed=50),
        _case('pendulum', 'short-small-angle', gravity=9.81, duration=0.25,
              time_step=0.001,
              parameters={'length': _q(1.0, 'm'),
                          'release_angle': _q(0.05, 'rad'),
                          'initial_angular_velocity': _q(0.0, 'rad/s')}),
        _case('pendulum', 'two-period-horizon', gravity=9.81, duration=4.0,
              time_step=0.001,
              parameters={'length': _q(1.0, 'm'),
                          'release_angle': _q(0.08, 'rad'),
                          'initial_angular_velocity': _q(0.0, 'rad/s')}, seed=51),
        _case('pendulum', 'initial-angular-velocity', gravity=3.7,
              duration=1.5, time_step=0.001,
              parameters={'length': _q(0.75, 'm'),
                          'release_angle': _q(0.02, 'rad'),
                          'initial_angular_velocity': _q(0.1, 'rad/s')}, seed=52),
        _case('pendulum', 'zero-answer-equilibrium', gravity=9.81,
              duration=0.5, time_step=0.001,
              parameters={'length': _q(1.0, 'm'),
                          'release_angle': _q(0.0, 'rad'),
                          'initial_angular_velocity': _q(0.0, 'rad/s')}, seed=53),
    ]


def _scene(folder, gravity):
    source = ROOT / 'test-data/synthetic/scene/room-v1'
    scene = json.loads((source / 'scene.json').read_text(encoding='utf-8'))
    scene['bounds_m'] = {'min': [-10, -1, -10], 'max': [10, 10, 10]}
    scene['colliders'] = []
    scene['gravity'] = {
        'status': 'assumed', 'direction': [0, -1, 0],
        'magnitude_m_s2': gravity,
        'evidence': 'authored synthetic S10hi acceptance case',
    }
    scene_path = folder / 'scene.json'
    scene_path.write_text(json.dumps(scene), encoding='utf-8')
    shutil.copyfile(source / 'points.ply', folder / 'points.ply')
    return scene, scene_path


def _build_spec(folder, authored):
    gravity = authored['gravity']
    scene, scene_path = _scene(folder, gravity)
    template = authored['template']
    module = importlib.import_module(f'Build.templates.{template}')
    common = dict(
        experiment_id=f"s10hi-{template}-{authored['case']}",
        scene=scene, scene_root=folder,
        origin={'value': [0, 2, 0], 'unit': 'm',
                'source': _q(0, 'm')['source']},
        gravity=_q(gravity, 'm/s^2'), mass=_q(0.1, 'kg'),
        radius=_q(0.02, 'm'), duration=_q(authored['duration'], 's'),
        time_step=_q(authored['time_step'], 's'), clearance=_q(0.01, 'm'),
        seed=authored['seed'],
    )
    spec = getattr(module, f'make_{template}')(
        **common, **authored['parameters'])
    spec_path = folder / 'spec.json'
    spec_path.write_text(json.dumps(spec), encoding='utf-8')
    return spec_path, scene_path, module


def _node(command, encoded):
    process = subprocess.run(
        ['node', str(ROOT / f'Build/lab/{command}')], input=encoded,
        text=True, capture_output=True, encoding='utf-8', timeout=30,
        cwd=ROOT)
    if process.returncode:
        raise RuntimeError(f'{command}: {process.stderr.strip() or process.stdout.strip()}')
    return process


def _validate_horizon(duration, time_step):
    if not math.isfinite(duration) or not math.isfinite(time_step):
        raise ValueError('duration and time_step must be finite')
    if duration <= 0 or time_step <= 0:
        raise ValueError('duration and time_step must be positive')
    steps = round(duration / time_step)
    if steps <= 0 or steps > MAX_STEPS or not math.isclose(
            steps * time_step, duration, rel_tol=1e-12, abs_tol=1e-12):
        raise ValueError('duration/time_step must be an integer stable horizon')
    return steps


def _characteristic_scale(template, spec, reference):
    origin = spec['placement']['origin']['value']
    if template == 'pendulum':
        scale = (spec['parameters']['length']['value'] *
                 reference['amplitude']['value'])
    elif template == 'ramp':
        scale = max(a['distance']['value'] for a in reference['samples'])
    else:
        scale = max(math.dist(origin, a['position']['value'])
                    for a in reference['samples'])
    if not math.isfinite(scale) or scale < 0:
        raise ValueError('characteristic scale must be finite and non-negative')
    return scale


def _run_case(authored):
    result = {'template': authored['template'], 'case': authored['case'],
              'gravity_m_s2': authored['gravity'],
              'duration_s': authored['duration'],
              'time_step_s': authored['time_step'], 'seed': authored['seed']}
    try:
        expected_steps = _validate_horizon(authored['duration'],
                                           authored['time_step'])
        result['expected_steps'] = expected_steps
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            spec_path, scene_path, module = _build_spec(folder, authored)
            artifact = export(spec_path, scene_path)
            encoded = json.dumps(artifact, allow_nan=False)
            first = _node('simulate.mjs', encoded)
            second = _node('simulate.mjs', encoded)
            if first.stdout != second.stdout:
                raise ValueError('actual seeded transport is not deterministic')
            trajectory = json.loads(first.stdout)
            samples = trajectory['samples']
            if not samples or len(samples) > expected_steps + 1:
                raise ValueError('trajectory sample count violates stable horizon')
            for index, sample in enumerate(samples):
                if (sample['step'] != index or
                        sample['time_s'] != index * authored['time_step']):
                    raise ValueError('trajectory step/time contract mismatch')
            reference_fn = getattr(module, f"analytic_{authored['template']}")
            oracle_limit = artifact['spec']['simulation']['duration']['value']
            reference_times = []
            endpoint_clamps = []
            for index, sample in enumerate(samples):
                time = sample['time_s']
                if time > oracle_limit:
                    ulp_tolerance = 4 * max(math.ulp(time), math.ulp(oracle_limit))
                    if (not math.isclose(time, oracle_limit, rel_tol=0,
                                         abs_tol=1e-12) or
                            time - oracle_limit > ulp_tolerance):
                        raise ValueError(
                            f'sample {index} exceeds oracle horizon by more than '
                            f'representational ULP tolerance: {time - oracle_limit}')
                    endpoint_clamps.append({
                        'sample_index': index,
                        'observed_time_s': time,
                        'oracle_limit_s': oracle_limit,
                        'absolute_overrun_s': time - oracle_limit,
                        'ulp_tolerance_s': ulp_tolerance,
                        'reason': 'representational fixed-step endpoint rounding',
                    })
                    time = oracle_limit
                reference_times.append(time)
            reference = reference_fn(
                artifact['spec'], artifact['scene'], folder,
                times=reference_times)
            errors = [math.dist(sample['position_m'], ref['position']['value'])
                      for sample, ref in zip(samples, reference['samples'])]
            position_error = max(errors, default=0.0)
            scale = _characteristic_scale(authored['template'], artifact['spec'],
                                          reference)
            if scale <= SCALE_EPSILON_M:
                if position_error > SCALE_EPSILON_M:
                    raise ValueError('near-zero characteristic scale with non-zero answer')
                relative_error = 0.0
                scale_policy = 'zero_answer_guard'
            else:
                relative_error = position_error / scale
                scale_policy = 'dimensional_characteristic_scale'
            replay = json.loads(_node('replay-check.mjs', encoded).stdout)
            if (replay['samples'] != len(samples) or
                    not replay['deterministic'] or not replay['seedBound']):
                raise ValueError('actual seeded replay contract failed')
            result.update({
                'status': 'passed' if relative_error <= THRESHOLD else 'failed',
                'samples': len(samples), 'position_error_m': position_error,
                'characteristic_scale_m': scale,
                'relative_error': relative_error,
                'within_half_percent': relative_error <= THRESHOLD,
                'scale_policy': scale_policy,
                'oracle_endpoint_clamps': endpoint_clamps,
                'reference': reference['method'],
                'deterministic': True, 'replay': replay,
                'contact_scope': 'pre-contact analytic motion only',
            })
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.SubprocessError,
            json.JSONDecodeError) as error:
        result.update({'status': 'rejected', 'reason': str(error)})
    return result


def _contact_diagnostic():
    script = r"""
const run = async () => {
  try {
    const { freeFallTrajectory, projectileTrajectory } = await import('./Build/simulator/trajectories.mjs');
    const { contactAwareTrajectory } = await import('./Build/simulator/contacts.mjs');
    const rows = [];
    const expectedContactTime = Math.sqrt(2 * (2 - 0.1) / 9.81);
    for (const template of ['free_fall', 'projectile']) {
      for (const dt of [0.02, 0.01, 0.005]) {
        const trajectory = (template === 'projectile' ? projectileTrajectory : freeFallTrajectory)({
          initialPosition: [0, 2, 0],
          initialVelocity: template === 'projectile' ? [1, 0, 0] : [0, 0, 0],
          gravity: 9.81, dt, steps: Math.round(3 / dt),
          source: 'simulated', inputProvenance: 'synthetic', stopPlaneY: 0.1
        });
        try {
          const output = await contactAwareTrajectory({ trajectory,
            gravity: 9.81,
            geometry: { floorY: 0, floorHalfExtents: [5, 0.1, 5], sphereRadius: 0.1 },
            physics: { friction: 0.4, restitution: 0, density: 1 } });
          const hit = output.samples.find((sample) => sample.contact) ?? null;
          rows.push({ template, dt_s: dt, status: hit ? 'contact_observed' : 'no_contact',
            contact_step: hit?.step ?? null, contact_time_s: hit?.time_s ?? null,
            expected_contact_time_s: expectedContactTime,
            contact_time_error_s: hit ? hit.time_s - expectedContactTime : null,
            rebound_claim: false, samples: output.samples.length,
            contact_semantics: output.contactSemantics });
        } catch (error) { rows.push({ template, dt_s: dt, status: 'rejected', reason: String(error) }); }
      }
    }
    process.stdout.write(JSON.stringify({ status: 'measured', rows }));
  } catch (error) {
    process.stdout.write(JSON.stringify({ status: 'unavailable', reason: String(error), rows: [] }));
  }
};
await run();
"""
    try:
        process = subprocess.run(['node', '--input-type=module', '-e', script],
                                 text=True, capture_output=True, encoding='utf-8',
                                 timeout=30, cwd=ROOT, check=True)
        result = json.loads(process.stdout)
        rows = result.get('rows', [])
        measured = [row for row in rows if row.get('status') == 'contact_observed']
        by_template = {}
        for row in measured:
            by_template.setdefault(row['template'], []).append(row)
        result['assessment'] = {
            'contact_jitter_observed': any(
                max(row['contact_time_s'] for row in group) -
                min(row['contact_time_s'] for row in group) > 0
                for group in by_template.values()),
            'max_contact_time_spread_s': max((
                max(row['contact_time_s'] for row in group) -
                min(row['contact_time_s'] for row in group)
                for group in by_template.values()), default=0.0),
            'max_abs_contact_time_error_s': max((
                abs(row['contact_time_error_s']) for row in measured), default=0.0),
            'fallback_observed': any(row.get('status') != 'contact_observed'
                                     for row in rows),
            'fallback_applied': False,
            'fallback_reason': 'not triggered by this dt sweep',
        }
        return result
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as error:
        return {'status': 'unavailable', 'reason': str(error), 'rows': [],
                'assessment': {'contact_jitter_observed': False,
                               'fallback_observed': False,
                               'fallback_applied': False,
                               'fallback_reason': 'runtime unavailable'}}


def _ui_readiness():
    files = list((ROOT / 'Build/web/src').rglob('*'))
    candidates = []
    for path in files:
        if path.is_file() and path.suffix in {'.js', '.mjs', '.jsx', '.ts', '.tsx'}:
            text = path.read_text(encoding='utf-8', errors='replace')
            if any(token in text for token in
                   ('contactAwareTrajectory', 'runContactAwareTrajectory',
                    'mystery-g', 'replay-check.mjs')):
                candidates.append(str(path.relative_to(ROOT)))
    return {
        'status': 'verifiable-path-found' if candidates else 'not-verified',
        'evidence_files': candidates,
        'reason': ('S10g UI transport/toggle references found in web source'
                   if candidates else
                   'no S10g UI transport/toggle path found in this checkout'),
        'gate_claim': 'not-a-UI-or-physical-Gate-P-result',
    }


def run_acceptance(*, write_evidence=True):
    cases = [_run_case(authored) for authored in case_matrix()]
    contact = _contact_diagnostic()
    result = {
        'source': 'simulated',
        'scope': 'synthetic four-template acceptance only',
        'threshold': THRESHOLD,
        'cases': cases,
        'case_counts': {
            'authored': len(cases),
            'passed': sum(case['status'] == 'passed' for case in cases),
            'failed': sum(case['status'] == 'failed' for case in cases),
            'rejected': sum(case['status'] == 'rejected' for case in cases),
        },
        'passed': all(case['status'] == 'passed' for case in cases),
        'contact_diagnostic': contact,
        'fallback_policy': {
            'allowed': True,
            'trigger': 'contact jitter or unsupported contact integration',
            'rk4_only': True,
            'free_dragging_enabled': False,
            'rebound_claim': False,
        },
        'ui_readiness': _ui_readiness(),
        'limits': [
            'synthetic only; no calibrated physical or real-scene gate',
            'Rapier is a same-state sampled contact detector and does not advance response',
            'required other-vendor R-P review is not represented by this evidence',
            'S10g UI integration and reviewer receipts remain prerequisite evidence',
        ],
    }
    if write_evidence:
        destination = ROOT / 'evidence/S10/acceptance'
        destination.mkdir(parents=True, exist_ok=True)
        (destination / 'acceptance.json').write_text(
            json.dumps(result, allow_nan=False, indent=2) + '\n', encoding='utf-8')
    return result


if __name__ == '__main__':
    print(json.dumps(run_acceptance(), allow_nan=False, indent=2))
