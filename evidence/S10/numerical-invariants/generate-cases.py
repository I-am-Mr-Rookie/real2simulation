"""Synthetic R14 cases, exported through the actual S08 validator; no copied validator."""
import json
import importlib
import math
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from Build.lab.regression import regression_case
from Build.simulator.export_validated_setup import export


def make_case(template, *, gravity=9.81, duration=None, dt=None, origin=None, parameters=None, times=()):
    with tempfile.TemporaryDirectory(prefix='r14-invariant-') as tmp:
        spec_path, scene_path, _ = regression_case(Path(tmp), template)
        spec = json.loads(spec_path.read_text(encoding='utf-8'))
        scene = json.loads(scene_path.read_text(encoding='utf-8'))
        spec['environment']['gravity']['value'] = gravity
        scene['gravity']['magnitude_m_s2'] = gravity
        for key, value in (parameters or {}).items():
            spec['parameters'][key]['value'] = value
        for key, value in [('duration', duration), ('time_step', dt)]:
            if value is not None:
                spec['simulation'][key]['value'] = value
        if origin is not None:
            spec['placement']['origin']['value'] = origin
        spec_path.write_text(json.dumps(spec, allow_nan=False), encoding='utf-8')
        scene_path.write_text(json.dumps(scene, allow_nan=False), encoding='utf-8')
        artifact = export(spec_path, scene_path)
        module = importlib.import_module(f'Build.templates.{template}')
        oracle_fn = getattr(module, f'analytic_{template}')
        metrics = oracle_fn(spec, scene, Path(tmp), times=[])
        limit = min(spec['simulation']['duration']['value'],
                    metrics.get('end_time', metrics.get('impact_time', {'value': math.inf}))['value'])
        oracle = oracle_fn(spec, scene, Path(tmp), times=[0, *times, limit])
        return {'artifact': artifact, 'oracle': oracle}


def cases():
    return {
        'pendulum-amplitude-boundary': make_case('pendulum', duration=4, dt=0.001, times=[3.531],
                                               parameters={'release_angle': 0.1}),
        'pendulum-amplitude-boundary-half-step': make_case('pendulum', duration=4, dt=0.0005, times=[3.531],
                                                         parameters={'release_angle': 0.1}),
        'ramp-positive-near-friction-boundary': make_case('ramp', gravity=1.62,
                                                        origin=[0, 0, 0],
                                                        parameters={'incline_angle': 0.7,
                                                                    'friction_coefficient': 0.8422883804630792}),
        'free-fall-large-finite-gravity': make_case('free_fall', gravity=5e307,
                                                  duration=8 * 2**-1030, dt=2**-1030, origin=[0, 0, 0],
                                                  parameters={'drop_height': 1e-308}),
        'projectile-large-finite-gravity': make_case('projectile', gravity=5e307,
                                                   duration=8 * 2**-1030, dt=2**-1030, origin=[0, 0, 0],
                                                   parameters={'launch_height': 1e-308}),
        'ramp-large-finite-gravity': make_case('ramp', gravity=5e307,
                                              duration=8 * 2**-1030, dt=2**-1030, origin=[0, 0, 0],
                                              parameters={'length': 1e-308, 'incline_angle': 1.4,
                                                          'friction_coefficient': 0}),
        'control-ramp-shallow': make_case('ramp', origin=[0, 2, 0],
                                         parameters={'incline_angle': 1e-8, 'friction_coefficient': 0}),
        'control-ramp-steep': make_case('ramp', duration=0.1,
                                       parameters={'incline_angle': math.pi / 2 - 1e-8,
                                                   'friction_coefficient': 0}),
        'control-ramp-friction-above-one': make_case('ramp', duration=0.1, dt=0.0005,
                                                    parameters={'incline_angle': 1.3,
                                                                'friction_coefficient': 2}),
        'control-free-fall-through-apex': make_case('free_fall', gravity=20, duration=0.3, dt=0.0005,
                                                   parameters={'drop_height': 0.5,
                                                               'initial_vertical_velocity': 3}),
        'control-free-fall-fast-downward': make_case('free_fall', duration=0.003, dt=0.00005,
                                                    parameters={'drop_height': 0.5,
                                                                'initial_vertical_velocity': -100}),
        'control-free-fall-min-normal-gravity': make_case('free_fall', gravity=sys.float_info.min),
        'control-projectile-fast-horizontal': make_case('projectile', dt=0.0005,
                                                        parameters={'horizontal_speed': 10}),
        'control-projectile-low-gravity': make_case('projectile', gravity=0.001, duration=1,
                                                    parameters={'horizontal_speed': 0.1}),
        'control-pendulum-negative-phase': make_case('pendulum', gravity=1.62, duration=2, origin=[0, 4, 0],
                                                     parameters={'length': 3, 'release_angle': -0.05,
                                                                 'initial_angular_velocity': 0.02}),
        'control-pendulum-frequency-step-boundary': make_case(
            'pendulum', duration=32 * (0.05 / math.sqrt(9.81 / 0.01)),
            dt=0.05 / math.sqrt(9.81 / 0.01),
            parameters={'length': 0.01, 'release_angle': 0.005}),
    }


def precision_reference():
    from decimal import Decimal, localcontext
    with localcontext() as context:
        context.prec = 100
        angle = Decimal.from_float(0.7)

        def series(cosine):
            term = Decimal(1) if cosine else angle
            total = term
            for n in range(1, 100):
                term *= -angle * angle / Decimal((2*n-1 if cosine else 2*n) * (2*n if cosine else 2*n+1))
                total += term
            return total

        mu = Decimal.from_float(0.8422883804630792)
        gravity = Decimal.from_float(1.62)
        return {'method': '100-digit Decimal Taylor sin/cos, 100 terms; exact binary64 inputs',
                'angle_exact': str(angle), 'friction_exact': str(mu), 'gravity_exact': str(gravity),
                'positive_acceleration_m_s2': str(gravity * (series(False) - mu * series(True)))}


def boundary_checks():
    boundary = 0.05 / math.sqrt(9.81 / 0.01)
    rows = []
    for name, dt in [('below', math.nextafter(boundary, 0)), ('boundary', boundary),
                     ('above', math.nextafter(boundary, math.inf))]:
        row = {'case': name, 'dt_s': dt, 'dt_times_frequency': dt * math.sqrt(9.81 / 0.01)}
        try:
            make_case('pendulum', duration=32 * dt, dt=dt,
                      parameters={'length': 0.01, 'release_angle': 0.005})
            row['validation'] = 'accepted'
        except ValueError as error:
            row.update(validation='rejected', error=str(error))
        rows.append(row)
    return rows


if __name__ == '__main__':
    if '--precision' in sys.argv:
        result = precision_reference()
    elif '--boundary-check' in sys.argv:
        result = boundary_checks()
    elif '--check' in sys.argv:
        current = cases()
        frozen = json.loads(Path(__file__).with_name('validated-cases.json').read_text(encoding='utf-8'))
        assert current == frozen, 'frozen artifacts/oracles differ from fresh authoritative export'
        result = {'fresh_authoritative_export_matches_frozen': True, 'cases': len(current)}
    else:
        result = cases()
    print(json.dumps(result, allow_nan=False, indent=2, sort_keys=True))
