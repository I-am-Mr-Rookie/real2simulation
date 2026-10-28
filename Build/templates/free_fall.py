"""Validated free-fall inputs and an independent closed-form Gate P reference.

No integrator, fitter, external calls, default physical numbers or measured claims.
"""
import copy
import math

from contracts.experiment.validate_experiment import validate_setup


def make_free_fall(*, experiment_id, scene, scene_root, origin, gravity, mass,
                   radius, drop_height, initial_vertical_velocity, duration,
                   time_step, clearance, seed=0):
    """Build from explicit provenance-bearing quantities; revalidate the bundle.

    origin is the contract's sourced position; all other physical inputs use
    {value, unit, source, uncertainty}. Never infer gravity/scale from a model.
    """
    spec = copy.deepcopy({
        'schema_version': '1.0.0', 'experiment_id': experiment_id,
        'template': 'free_fall',
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
        'parameters': {'drop_height': drop_height,
                       'initial_vertical_velocity': initial_vertical_velocity},
        'simulation': {'duration': duration, 'time_step': time_step, 'seed': seed},
    })
    return validate_setup(spec, scene, scene_root)


def analytic_free_fall(spec, scene, scene_root, *, times=()):
    """Return ideal stop-plane impact plus requested pre-impact samples.

    Positive Y velocity is upward. Samples must lie in [0, min(duration, impact)].
    Impact metrics describe the full ideal flight, even if duration is shorter.
    Input uncertainty is NOT propagated; result uncertainty stays null.
    """
    validate_setup(spec, scene, scene_root)
    if spec['template'] != 'free_fall':
        raise ValueError('$.template: analytic_free_fall requires free_fall')
    g = spec['environment']['gravity']['value']
    h = spec['parameters']['drop_height']['value']
    v = spec['parameters']['initial_vertical_velocity']['value']
    origin = spec['placement']['origin']['value']
    speed = math.sqrt(v * v + 2 * g * h)
    # Avoid cancellation when initial velocity points downwards.
    impact = (v + speed) / g if v >= 0 else 2 * h / (speed - v)
    if not math.isfinite(impact) or impact <= 0:
        raise ValueError('$.parameters: analytic impact time is not representable')
    limit = min(impact, spec['simulation']['duration']['value'])
    if not isinstance(times, (list, tuple)) or len(times) > 100_001:
        raise ValueError('$.times: expected list/tuple with at most 100001 samples')

    evidence = f"analytic-free-fall-v1:experiment/{spec['experiment_id']}"

    def output(value, unit):
        return {'value': value, 'unit': unit, 'uncertainty': None,
                'source': {'label': 'simulated', 'evidence': evidence}}

    samples = []
    for i, t in enumerate(times):
        if (isinstance(t, bool) or not isinstance(t, (int, float))
                or not math.isfinite(t) or not 0 <= t <= limit):
            raise ValueError(f'$.times[{i}]: finite seconds in [0, {limit}] required')
        # Anchor the endpoint to its exact stop-plane definition.
        y = origin[1] - h if t == impact else origin[1] + t * (v - 0.5 * g * t)
        samples.append({'time': output(t, 's'),
                        'position': output([origin[0], y, origin[2]], 'm'),
                        'vertical_velocity': output(v - g * t, 'm/s')})
    sources = {'gravity': spec['environment']['gravity']['source'],
               'origin': spec['placement']['origin']['source'],
               **{k: q['source'] for k, q in spec['parameters'].items()}}
    return {'method': 'analytic-free-fall-v1', 'experiment_id': spec['experiment_id'],
            'input_sources': copy.deepcopy(sources),
            'impact_time': output(impact, 's'),
            'impact_vertical_velocity': output(-speed, 'm/s'),
            'impact_position': output([origin[0], origin[1] - h, origin[2]], 'm'),
            'samples': samples}
