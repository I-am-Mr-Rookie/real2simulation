"""Offline synthetic lab: actual S08 validation -> Node RK4 -> instruments -> fitter.

This is an internal diagnostic API, not a Mystery-g public projection. The caller
must provide every instrument setting; no clock/scale calibration is inferred.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import subprocess

from Build.fitter.api import handle
from Build.instruments.synthetic import light_gate_observation, ruler_observation
from Build.simulator.export_validated_setup import export
from contracts.fit.quantity import validate_quantity

ROOT = Path(__file__).resolve().parents[2]
INSTRUMENT_FIELDS = frozenset((
    'time_resolution_s', 'time_uncertainty_s', 'time_bias_s',
    'distance_resolution_m', 'distance_uncertainty_m', 'distance_bias_m',
))


def run_lab(spec_path: Path, scene_path: Path, *, instruments: dict) -> dict:
    """Fit downward displacement from free-fall/projectile synthetic observations.

    A rising free-fall launch is unsupported by this displacement-ruler adapter,
    not silently filtered out. Every simulated sample is used in the fit.
    """
    if not isinstance(instruments, dict) or set(instruments) != INSTRUMENT_FIELDS:
        raise ValueError('all six explicit instrument settings are required; no extra fields')
    artifact = export(Path(spec_path), Path(scene_path))
    spec = artifact['spec']
    if artifact['scene']['synthetic'] is not True or spec['template'] not in ('free_fall', 'projectile'):
        raise ValueError('offline ballistic lab requires a synthetic free_fall/projectile setup')
    if spec['template'] == 'free_fall' and spec['parameters']['initial_vertical_velocity']['value'] > 0:
        raise ValueError('rising launch unsupported by downward displacement ruler')
    process = subprocess.run(
        ['node', str(ROOT / 'Build/lab/simulate.mjs')],
        input=json.dumps(artifact, allow_nan=False), text=True, capture_output=True,
        encoding='utf-8', timeout=30, cwd=ROOT,
    )
    if process.returncode:
        raise ValueError('synthetic simulator rejected the validated transport')
    trajectory = json.loads(process.stdout)
    expected_kind = 'free-fall' if spec['template'] == 'free_fall' else 'projectile'
    if (not isinstance(trajectory, dict) or trajectory.get('kind') != expected_kind
            or trajectory.get('source') != 'simulated' or trajectory.get('inputProvenance') != 'synthetic'
            or trajectory.get('integrator') != 'rk4-fixed-step'
            or trajectory.get('dt_s') != spec['simulation']['time_step']['value']):
        raise ValueError('simulator returned an incompatible trajectory contract')
    samples = trajectory.get('samples')
    if not isinstance(samples, list) or not samples or len(samples) > 1_000_001:
        raise ValueError('simulator returned invalid samples')
    for index, sample in enumerate(samples):
        if not isinstance(sample, dict) or sample.get('step') != index:
            raise ValueError('simulator returned invalid sample ordering')
        for field in ('position_m', 'velocity_m_s'):
            vector = sample.get(field)
            if (not isinstance(vector, list) or len(vector) != 3
                    or any(type(x) not in (int, float) or not math.isfinite(x) for x in vector)):
                raise ValueError('simulator returned invalid vector state')
        time = sample.get('time_s')
        if type(time) not in (int, float) or not math.isfinite(time) or time != index * trajectory['dt_s']:
            raise ValueError('simulator returned invalid sample time')
    origin_y = trajectory['samples'][0]['position_m'][1]
    times, positions = [], []
    for sample in trajectory['samples']:
        times.append(light_gate_observation(
            sample['time_s'], resolution_s=instruments['time_resolution_s'],
            uncertainty_s=instruments['time_uncertainty_s'], bias_s=instruments['time_bias_s'],
        ))
        positions.append(ruler_observation(
            origin_y - sample['position_m'][1],
            resolution_m=instruments['distance_resolution_m'],
            uncertainty_m=instruments['distance_uncertainty_m'], bias_m=instruments['distance_bias_m'],
        ))
    fit = handle({'times': times, 'positions': positions, 'degree': 2, 'select_model': True})
    if fit['status'] == 'ok' and fit.get('gravity') is not None:
        gravity = validate_quantity(fit['gravity'])
        if gravity['unit'] != 'm/s^2':
            raise ValueError('fitter returned an incompatible gravity unit')
    return {
        'source': 'simulated', 'inputProvenance': 'synthetic',
        'scope': 'internal offline ballistic lab; not a public Mystery-g payload',
        'template': spec['template'], 'trajectory': trajectory,
        'instrument_model': 'deterministic quantization/bias; no stochastic stream or seed dependence',
        'observations': {'times': times, 'positions': positions, 'coordinate': 'downward displacement'},
        'fit': fit,
        'limits': ['first-order independent timing/position uncertainty; scale fixed',
                   'no correlated clock-rate or scale uncertainty; not calibrated',
                   'not calibrated physical evidence', 'sampled stop-plane crossing may overshoot'],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('spec', type=Path)
    parser.add_argument('scene', type=Path)
    parser.add_argument('instruments', type=Path)
    args = parser.parse_args()
    try:
        result = run_lab(args.spec, args.scene, instruments=json.loads(args.instruments.read_text(encoding='utf-8')))
        print(json.dumps(result, allow_nan=False, sort_keys=True))
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, f'OFFLINE_LAB_ERROR: {error}\n')


if __name__ == '__main__':
    main()
