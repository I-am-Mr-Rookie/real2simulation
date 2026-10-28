"""Validated accelerating sliding-ramp inputs and closed-form reference; no integrator."""
import copy
import math

from contracts.experiment.validate_experiment import validate_setup


def _acceleration(spec):
    p = spec['parameters']
    angle = p['incline_angle']['value']
    a = spec['environment']['gravity']['value'] * (
        math.sin(angle) - p['friction_coefficient']['value'] * math.cos(angle))
    if not math.isfinite(a) or a <= 0:
        raise ValueError('$.parameters: ramp oracle requires finite positive downhill acceleration; '
                         'coasting, stalling and static friction are unsupported')
    return a


def make_ramp(*, experiment_id, scene, scene_root, origin, gravity, mass,
              radius, length, incline_angle, friction_coefficient, initial_speed,
              duration, time_step, clearance, seed=0):
    """Explicit sourced inputs; ideal centre path, no attached physical support."""
    spec = copy.deepcopy({
        'schema_version': '1.0.0', 'experiment_id': experiment_id, 'template': 'ramp',
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
        'parameters': {'length': length, 'incline_angle': incline_angle,
                       'friction_coefficient': friction_coefficient, 'initial_speed': initial_speed},
        'simulation': {'duration': duration, 'time_step': time_step, 'seed': seed},
    })
    validate_setup(spec, scene, scene_root)
    _acceleration(spec)
    return spec


def analytic_ramp(spec, scene, scene_root, *, times=()):
    """Full ramp-end metrics plus duration-bounded samples; no rolling/post-end motion.

    Kinetic Coulomb sliding with positive downhill acceleration only. Starting
    from rest means ideal incipient sliding, not a static-friction prediction.
    """
    validate_setup(spec, scene, scene_root)
    if spec['template'] != 'ramp':
        raise ValueError('$.template: analytic_ramp requires ramp')
    a = _acceleration(spec)
    p = spec['parameters']
    length, u, angle = (p[k]['value'] for k in ('length', 'initial_speed', 'incline_angle'))
    direction = [math.cos(angle), -math.sin(angle), 0]
    origin = spec['placement']['origin']['value']
    speed = math.sqrt(u*u + 2*a*length)
    end_time = length / ((u + speed) / 2)  # Stable positive quadratic root.
    endpoint = [o + length*d for o, d in zip(origin, direction)]
    if (not all(math.isfinite(v) for v in [speed, end_time, *endpoint])
            or end_time <= 0 or speed <= 0):
        raise ValueError('$.parameters: analytic ramp endpoint is not representable')
    limit = min(end_time, spec['simulation']['duration']['value'])
    if not isinstance(times, (list, tuple)) or len(times) > 100_001:
        raise ValueError('$.times: expected list/tuple with at most 100001 samples')
    evidence = f"analytic-ramp-v1:experiment/{spec['experiment_id']}"

    def output(value, unit):
        return {'value': value, 'unit': unit, 'uncertainty': None,
                'source': {'label': 'simulated', 'evidence': evidence}}

    samples = []
    for i, t in enumerate(times):
        if (isinstance(t, bool) or not isinstance(t, (int, float))
                or not 0 <= t <= limit or not math.isfinite(t)):
            raise ValueError(f'$.times[{i}]: finite seconds in [0, {limit}] required')
        distance = length if t == end_time else (u + .5*a*t)*t
        velocity = speed if t == end_time else u + a*t
        position = [o + distance*d for o, d in zip(origin, direction)]
        samples.append({'time': output(t, 's'), 'distance': output(distance, 'm'),
                        'position': output(position, 'm'),
                        'velocity': output([velocity*d for d in direction], 'm/s')})
    sources = {'gravity': spec['environment']['gravity']['source'],
               'origin': spec['placement']['origin']['source'],
               **{k: q['source'] for k, q in p.items()}}
    return {'method': 'analytic-ramp-v1', 'experiment_id': spec['experiment_id'],
            'input_sources': copy.deepcopy(sources), 'acceleration': output(a, 'm/s^2'),
            'end_time': output(end_time, 's'), 'end_speed': output(speed, 'm/s'),
            'end_position': output(endpoint, 'm'),
            'end_velocity': output([speed*d for d in direction], 'm/s'), 'samples': samples}
