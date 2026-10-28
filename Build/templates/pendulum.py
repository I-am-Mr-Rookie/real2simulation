"""Validated linearized pendulum reference; not a nonlinear solver or integrator."""
import copy
import math

from contracts.experiment.validate_experiment import validate_setup


def _reference(spec):
    p = spec['parameters']
    w = math.sqrt(spec['environment']['gravity']['value'] / p['length']['value'])
    amplitude = math.hypot(p['release_angle']['value'], p['initial_angular_velocity']['value']/w)
    period = 2*math.pi/w
    if (not all(math.isfinite(v) for v in (w, amplitude, period))
            or w <= 0 or period <= 0):
        raise ValueError('$.parameters: pendulum reference is not representable')
    if amplitude > .1:
        raise ValueError('$.parameters: small-angle oracle requires amplitude <= 0.1 rad; '
                         'large-angle and rotating pendulums are unsupported')
    return w, amplitude, period


def make_pendulum(*, experiment_id, scene, scene_root, origin, gravity, mass,
                  radius, length, release_angle, initial_angular_velocity,
                  duration, time_step, clearance, seed=0):
    """Explicit sourced inputs. Origin is the fixed pivot; positive angle is +X."""
    spec = copy.deepcopy({
        'schema_version': '1.0.0', 'experiment_id': experiment_id, 'template': 'pendulum',
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
        'parameters': {'length': length, 'release_angle': release_angle,
                       'initial_angular_velocity': initial_angular_velocity},
        'simulation': {'duration': duration, 'time_step': time_step, 'seed': seed},
    })
    validate_setup(spec, scene, scene_root)
    _reference(spec)
    return spec


def analytic_pendulum(spec, scene, scene_root, *, times=()):
    """Solve theta''+(g/L)theta=0, amplitude <=.1 rad, no damping or contact.

    Circular bob geometry is reconstructed from approximate theta; the period
    is the linearized model's period, not an exact finite-amplitude prediction.
    """
    validate_setup(spec, scene, scene_root)
    if spec['template'] != 'pendulum':
        raise ValueError('$.template: analytic_pendulum requires pendulum')
    w, amplitude, period = _reference(spec)
    p = spec['parameters']
    length, theta0, omega0 = (p[k]['value'] for k in
                            ('length', 'release_angle', 'initial_angular_velocity'))
    origin = spec['placement']['origin']['value']
    limit = spec['simulation']['duration']['value']
    if not isinstance(times, (list, tuple)) or len(times) > 100_001:
        raise ValueError('$.times: expected list/tuple with at most 100001 samples')
    evidence = f"analytic-pendulum-small-angle-v1:experiment/{spec['experiment_id']}"

    def output(value, unit):
        return {'value': value, 'unit': unit, 'uncertainty': None,
                'source': {'label': 'simulated', 'evidence': evidence}}

    samples = []
    for i, t in enumerate(times):
        if (isinstance(t, bool) or not isinstance(t, (int, float))
                or not 0 <= t <= limit or not math.isfinite(t)):
            raise ValueError(f'$.times[{i}]: finite seconds in [0, {limit}] required')
        phase = w*t
        if not math.isfinite(phase):
            raise ValueError(f'$.times[{i}]: pendulum phase is not representable')
        c, s = math.cos(phase), math.sin(phase)
        theta = theta0*c + (omega0/w)*s
        omega = -theta0*w*s + omega0*c
        st, ct = math.sin(theta), math.cos(theta)
        position = [origin[0]+length*st, origin[1]-length*ct, origin[2]]
        velocity = [length*ct*omega, length*st*omega, 0]
        if not all(math.isfinite(v) for v in [theta, omega, *position, *velocity]):
            raise ValueError(f'$.times[{i}]: pendulum sample is not representable')
        samples.append({'time': output(t, 's'), 'angle': output(theta, 'rad'),
                        'angular_velocity': output(omega, 'rad/s'),
                        'position': output(position, 'm'), 'velocity': output(velocity, 'm/s')})
    sources = {'gravity': spec['environment']['gravity']['source'],
               'origin': spec['placement']['origin']['source'],
               **{k: q['source'] for k, q in p.items()}}
    return {'method': 'analytic-pendulum-small-angle-v1', 'model': 'linearized-small-angle',
            'experiment_id': spec['experiment_id'], 'input_sources': copy.deepcopy(sources),
            'angular_frequency': output(w, 'rad/s'), 'period': output(period, 's'),
            'amplitude': output(amplitude, 'rad'), 'samples': samples}
