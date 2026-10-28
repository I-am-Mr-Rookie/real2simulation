"""Local four-template analytic regression. Not a physical or other-vendor gate.

Errors use a declared characteristic scale, never pointwise division near zero.
The short ballistic/ramp horizon intentionally remains before the analytic event.
"""
import importlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import tempfile

from Build.simulator.export_validated_setup import export

ROOT = Path(__file__).resolve().parents[2]


def quantity(value, unit):
    return {'value': value, 'unit': unit, 'uncertainty': None,
            'source': {'label': 'synthetic', 'evidence': 'authored extension analytic regression input'}}


def regression_case(folder, template):
    """Build actual validated S08 factory inputs, not fake validator labels."""
    source = ROOT / 'test-data/synthetic/scene/room-v1'
    scene = json.loads((source / 'scene.json').read_text(encoding='utf-8'))
    scene['bounds_m'] = {'min': [-10, -1, -10], 'max': [10, 10, 10]}
    scene['colliders'] = []
    scene['gravity'] = dict(status='assumed', direction=[0, -1, 0],
                            magnitude_m_s2=9.81, evidence='authored synthetic regression')
    scene_path = folder / 'scene.json'
    scene_path.write_text(json.dumps(scene), encoding='utf-8')
    shutil.copyfile(source / 'points.ply', folder / 'points.ply')
    module = importlib.import_module(f'Build.templates.{template}')
    common = dict(experiment_id=f'extension-{template}', scene=scene, scene_root=folder,
                  origin={'value': [0, 2, 0], 'unit': 'm', 'source': quantity(0, 'm')['source']},
                  gravity=quantity(9.81, 'm/s^2'), mass=quantity(0.1, 'kg'),
                  radius=quantity(0.02, 'm'), duration=quantity(0.2 if template != 'pendulum' else 1, 's'),
                  time_step=quantity(0.001, 's'), clearance=quantity(0.01, 'm'), seed=42)
    parameters = {
        'free_fall': dict(drop_height=quantity(1, 'm'), initial_vertical_velocity=quantity(0, 'm/s')),
        'projectile': dict(launch_height=quantity(1, 'm'), horizontal_speed=quantity(1, 'm/s')),
        'ramp': dict(length=quantity(1, 'm'), incline_angle=quantity(0.5, 'rad'),
                     friction_coefficient=quantity(0.1, '1'), initial_speed=quantity(0, 'm/s')),
        'pendulum': dict(length=quantity(1, 'm'), release_angle=quantity(0.05, 'rad'),
                         initial_angular_velocity=quantity(0, 'rad/s')),
    }
    spec = getattr(module, f'make_{template}')(**common, **parameters[template])
    spec_path = folder / 'spec.json'
    spec_path.write_text(json.dumps(spec), encoding='utf-8')
    return spec_path, scene_path, module


def run_regression():
    results = []
    for template in ('free_fall', 'projectile', 'ramp', 'pendulum'):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            spec_path, scene_path, module = regression_case(folder, template)
            artifact = export(spec_path, scene_path)
            encoded = json.dumps(artifact, allow_nan=False)
            command = ['node', str(ROOT / 'Build/lab/simulate.mjs')]
            process = subprocess.run(command, input=encoded, text=True, capture_output=True,
                                     encoding='utf-8', timeout=30, cwd=ROOT, check=True)
            trajectory = json.loads(process.stdout)
            repeated = subprocess.run(command, input=encoded, text=True, capture_output=True,
                                      encoding='utf-8', timeout=30, cwd=ROOT, check=True)
            if repeated.stdout != process.stdout:
                raise ValueError(f'{template}: deterministic repeated trace failed')
            samples = trajectory['samples']
            reference = getattr(module, f'analytic_{template}')(
                artifact['spec'], artifact['scene'], folder, times=[s['time_s'] for s in samples])
            position_error = max(math.dist(s['position_m'], a['position']['value'])
                                 for s, a in zip(samples, reference['samples']))
            if template == 'pendulum':
                scale = artifact['spec']['parameters']['length']['value'] * reference['amplitude']['value']
            elif template == 'ramp':
                scale = max(a['distance']['value'] for a in reference['samples'])
            else:
                origin = artifact['spec']['placement']['origin']['value']
                scale = max(math.dist(origin, a['position']['value']) for a in reference['samples'])
            if not math.isfinite(scale) or scale <= 0:
                raise ValueError(f'{template}: comparison scale must be positive and finite')
            relative_error = position_error / scale
            if not math.isfinite(relative_error):
                raise ValueError(f'{template}: non-finite comparison')
            results.append(dict(template=template, samples=len(samples), position_error_m=position_error,
                                characteristic_scale_m=scale, relative_error=relative_error,
                                within_half_percent=relative_error <= 0.005,
                                reference=reference['method'], deterministic=True,
                                contact_scope='pre-contact analytic motion only'))
    return dict(source='simulated', scope='local synthetic analytic regression, not whole Gate P acceptance',
                threshold=0.005, passed=all(r['within_half_percent'] for r in results), cases=results,
                limits=['single authored input per template; not exhaustive parameter validation',
                        'small-angle pendulum oracle differs from nonlinear model',
                        'contact-event and other-vendor review remain separate requirements'])


if __name__ == '__main__':
    print(json.dumps(run_regression(), allow_nan=False, indent=2))
