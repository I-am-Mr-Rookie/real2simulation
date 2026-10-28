"""Validated horizontal-launch inputs and closed-form Gate P reference.

Vacuum +X motion, uniform -Y gravity; no integrator or measured claims.
"""
import copy
import math

from contracts.experiment.validate_experiment import validate_setup


def make_projectile(*, experiment_id, scene, scene_root, origin, gravity, mass,
                    radius, launch_height, horizontal_speed, duration,
                    time_step, clearance, seed=0):
    """Build from explicit sourced quantities and validate the authoritative bundle."""
    spec = copy.deepcopy({
        'schema_version': '1.0.0', 'experiment_id': experiment_id,
        'template': 'projectile',
        'scene': {
            'scene_id': scene['id'], 'schema_version': scene['schema_version'],
            'coordinate_system': 'right-handed-y-up-metres',
            'scale_status': scene['scale']['status'],
            'constraints': {
                'bounds_m': scene['bounds_m'],
                'allowed_surface_ids': [s['id'] for s in scene['surfaces']],
                'collision_obstacle_ids': [c['id'] for c in scene['colliders']],
                'clearance': clearance,
            },
        },
        'environment': {'gravity': gravity, 'gravity_direction': [0, -1, 0],
                        'air_resistance': 'neglected'},
        'body': {'mass': mass, 'radius': radius},
        'placement': {'origin': origin, 'surface_id': None},
        'parameters': {'launch_height': launch_height, 'horizontal_speed': horizontal_speed},
        'simulation': {'duration': duration, 'time_step': time_step, 'seed': seed},
    })
    return validate_setup(spec, scene, scene_root)


def analytic_projectile(spec, scene, scene_root, *, times=()):
    """Full ideal stop-plane impact and explicit pre-impact samples, in SI units.

    Launch velocity is [horizontal_speed, 0, 0]. No post-impact/contact model.
    Duration bounds samples, not full-flight reference metrics. Input uncertainty
    is not propagated; null output uncertainty must not be read as certainty.
    """
    validate_setup(spec, scene, scene_root)
    if spec['template'] != 'projectile':
        raise ValueError('$.template: analytic_projectile requires projectile')
    g = spec['environment']['gravity']['value']
    h = spec['parameters']['launch_height']['value']
    vx = spec['parameters']['horizontal_speed']['value']
    origin = spec['placement']['origin']['value']
    speed_y = math.sqrt(2 * g * h)
    impact = speed_y / g
    if not math.isfinite(impact) or impact <= 0:
        raise ValueError('$.parameters: analytic impact time is not representable')
    distance = vx * impact
    endpoint = [origin[0] + distance, origin[1] - h, origin[2]]
    if not all(math.isfinite(v) for v in [distance, *endpoint]):
        raise ValueError('$.parameters: analytic impact position is not representable')
    limit = min(impact, spec['simulation']['duration']['value'])
    if not isinstance(times, (list, tuple)) or len(times) > 100_001:
        raise ValueError('$.times: expected list/tuple with at most 100001 samples')

    evidence = f"analytic-projectile-v1:experiment/{spec['experiment_id']}"

    def output(value, unit):
        return {'value': value, 'unit': unit, 'uncertainty': None,
                'source': {'label': 'simulated', 'evidence': evidence}}

    samples = []
    for i, t in enumerate(times):
        # Compare the range before isfinite so huge Python ints fail readably.
        if (isinstance(t, bool) or not isinstance(t, (int, float))
                or not 0 <= t <= limit or not math.isfinite(t)):
            raise ValueError(f'$.times[{i}]: finite seconds in [0, {limit}] required')
        position = (list(endpoint) if t == impact else
                    [origin[0] + vx * t, origin[1] - (0.5 * g * t) * t, origin[2]])
        samples.append({'time': output(t, 's'), 'position': output(position, 'm'),
                        'velocity': output([vx, -speed_y if t == impact else -g * t, 0], 'm/s')})
    sources = {'gravity': spec['environment']['gravity']['source'],
               'origin': spec['placement']['origin']['source'],
               **{k: q['source'] for k, q in spec['parameters'].items()}}
    return {'method': 'analytic-projectile-v1', 'experiment_id': spec['experiment_id'],
            'input_sources': copy.deepcopy(sources),
            'impact_time': output(impact, 's'), 'horizontal_range': output(distance, 'm'),
            'impact_position': output(endpoint, 'm'),
            'impact_velocity': output([vx, -speed_y, 0], 'm/s'), 'samples': samples}
