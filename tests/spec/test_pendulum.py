"""Synthetic small-angle references, not nonlinear simulation or Gate P evidence."""
import copy
import importlib
import json
import math
import sys
import unittest

from test_setup_validation import BUNDLE, ROOT, setup
from test_experiment_schema import quantity

sys.path.insert(0, str(ROOT))


class PendulumTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((ROOT / 'Build/templates/pendulum.py').is_file(), 'pendulum API missing')
        self.api = importlib.import_module('Build.templates.pendulum')
        self.spec, self.scene = setup('pendulum')
        self.spec['parameters']['release_angle']['value'] = .05
        self.spec['parameters']['initial_angular_velocity']['value'] = 0

    def make(self, **changes):
        s = self.spec
        args = dict(experiment_id=s['experiment_id'], scene=self.scene, scene_root=BUNDLE,
                    origin=s['placement']['origin'], gravity=s['environment']['gravity'],
                    mass=s['body']['mass'], radius=s['body']['radius'],
                    duration=s['simulation']['duration'], time_step=s['simulation']['time_step'],
                    clearance=s['scene']['constraints']['clearance'], seed=42,
                    **s['parameters'])
        args.update(changes)
        return self.api.make_pendulum(**args)

    def oracle(self, spec=None, **kw):
        return self.api.analytic_pendulum(spec or self.spec, self.scene, BUNDLE, **kw)

    def test_factory_validates_and_copies(self):
        before = copy.deepcopy((self.spec, self.scene))
        made = self.make()
        expected = copy.deepcopy(self.spec)
        expected['scene']['constraints']['allowed_surface_ids'] = [s['id'] for s in self.scene['surfaces']]
        self.assertEqual(made, expected)
        made['parameters']['length']['value'] = .5
        made['scene']['constraints']['bounds_m']['min'][0] = -100
        self.assertEqual((self.spec, self.scene), before)

    def test_quarter_period_and_pivot_geometry(self):
        r = self.oracle()
        w = math.sqrt(9.81 / self.spec['parameters']['length']['value'])
        T = 2*math.pi/w
        self.spec['simulation']['duration']['value'] = T
        r = self.oracle(times=[0, T/4, T/2, T])
        self.assertAlmostEqual(r['period']['value'], T)
        self.assertAlmostEqual(r['angular_frequency']['value'], w)
        self.assertEqual(r['amplitude']['value'], .05)
        for s, angle in zip(r['samples'], [.05, 0, -.05, .05]):
            self.assertAlmostEqual(s['angle']['value'], angle)
            p = s['position']['value']; o = self.spec['placement']['origin']['value']
            L = self.spec['parameters']['length']['value']
            self.assertAlmostEqual(p[0], o[0]+L*math.sin(angle))
            self.assertAlmostEqual(p[1], o[1]-L*math.cos(angle))
            self.assertEqual(p[2], o[2])
            self.assertAlmostEqual(sum((a-b)**2 for a, b in zip(p, o)), L*L)
        self.assertAlmostEqual(r['samples'][1]['angular_velocity']['value'], -.05*w)

    def test_initial_velocity_signs_and_linear_energy(self):
        for theta, omega in [(.03, -.1), (-.03, .1), (0, -.1)]:
            self.spec['parameters']['release_angle']['value'] = theta
            self.spec['parameters']['initial_angular_velocity']['value'] = omega
            r = self.oracle(times=[0, .1, .3])
            w = r['angular_frequency']['value']; L = self.spec['parameters']['length']['value']
            self.assertAlmostEqual(r['amplitude']['value'], math.hypot(theta, omega/w))
            for s in r['samples']:
                a, v = s['angle']['value'], s['angular_velocity']['value']
                self.assertAlmostEqual(v*v+w*w*a*a, omega*omega+w*w*theta*theta)
                self.assertAlmostEqual(s['velocity']['value'][0], L*math.cos(a)*v)
                self.assertAlmostEqual(s['velocity']['value'][1], L*math.sin(a)*v)
            self.assertAlmostEqual(r['samples'][0]['angle']['value'], theta)
            self.assertAlmostEqual(r['samples'][0]['angular_velocity']['value'], omega)

    def test_zero_equilibrium_and_boundary_amplitude(self):
        for angle in (0, .1, -.1):
            self.spec['parameters']['release_angle']['value'] = angle
            r = self.oracle(times=[0, .1])
            self.assertEqual(r['amplitude']['value'], abs(angle))
            if angle == 0:
                self.assertEqual(r['samples'][0]['position'], r['samples'][1]['position'])
                self.assertEqual(r['samples'][1]['velocity']['value'], [0, 0, 0])

    def test_large_angle_or_velocity_rejected_by_both_entries(self):
        for field, value in [('release_angle', .10001), ('release_angle', -.2),
                             ('initial_angular_velocity', 1)]:
            with self.subTest(field=field, value=value):
                s = copy.deepcopy(self.spec); s['parameters'][field]['value'] = value
                with self.assertRaisesRegex(ValueError, 'amplitude'):
                    self.oracle(s)
                with self.assertRaisesRegex(ValueError, 'amplitude'):
                    self.make(**{field: s['parameters'][field]})

    def test_gravity_and_length_period_scaling(self):
        for g, L in [(1.62, .5), (9.81, 1), (24.79, 2)]:
            self.scene['gravity']['magnitude_m_s2'] = g
            s = self.make(gravity=quantity(g, 'm/s^2'), length=quantity(L, 'm'),
                          time_step=quantity(.0001, 's'))
            self.assertAlmostEqual(self.oracle(s)['period']['value'], 2*math.pi*math.sqrt(L/g))

    def test_duration_bounds_not_period(self):
        a = self.oracle()
        self.spec['simulation']['duration']['value'] = .01
        self.assertEqual(self.oracle(times=[.01])['period'], a['period'])
        with self.assertRaisesRegex(ValueError, 'times'):
            self.oracle(times=[.01001])

    def test_bad_samples_and_preserved_order(self):
        for times in (None, iter([0]), [0]*100_002, [True], ['0'], [-.1], [math.nan], [math.inf]):
            with self.subTest(kind=str(type(times))):
                with self.assertRaisesRegex(ValueError, 'times'):
                    self.oracle(times=times)
        self.assertEqual([s['time']['value'] for s in self.oracle(times=[.1, 0, .1])['samples']], [.1, 0, .1])
        self.assertEqual(self.oracle()['samples'], [])

    def test_determinism_provenance_units_and_no_mutation(self):
        before = copy.deepcopy((self.spec, self.scene))
        r = self.oracle(times=[0, .1])
        self.assertEqual(r, self.oracle(times=[0, .1]))
        json.dumps(r, allow_nan=False)
        self.assertEqual(r['method'], 'analytic-pendulum-small-angle-v1')
        self.assertEqual(r['model'], 'linearized-small-angle')
        for field, unit in [('period', 's'), ('angular_frequency', 'rad/s'), ('amplitude', 'rad')]:
            self.assertEqual(r[field]['unit'], unit)
            self.assertEqual(r[field]['source']['label'], 'simulated')
            self.assertIsNone(r[field]['uncertainty'])
        self.assertEqual(r['input_sources']['length'], self.spec['parameters']['length']['source'])
        r['input_sources']['length']['label'] = 'unknown'
        self.assertEqual((self.spec, self.scene), before)

    def test_validation_not_bypassed(self):
        for section, field, value, reason in [('body', 'mass', math.nan, 'finite'),
                ('parameters', 'length', 0, 'length'),
                ('simulation', 'time_step', .1, 'time_step')]:
            s = copy.deepcopy(self.spec); s[section][field]['value'] = value
            with self.assertRaisesRegex(ValueError, reason):
                self.oracle(s)
        with self.assertRaisesRegex(ValueError, 'unit'):
            self.make(length=quantity(1, 's'))
        bad_origin = copy.deepcopy(self.spec['placement']['origin']); bad_origin['value'][0] = 10
        with self.assertRaisesRegex(ValueError, 'bounds'):
            self.make(origin=bad_origin)
        self.scene['assets'][0]['sha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'SHA256'):
            self.oracle()
        with self.assertRaisesRegex(ValueError, 'SHA256'):
            self.make()

    def test_wrong_template_rejected(self):
        s, scene = setup('ramp')
        with self.assertRaisesRegex(ValueError, 'requires pendulum'):
            self.api.analytic_pendulum(s, scene, BUNDLE)


if __name__ == '__main__':
    unittest.main()
