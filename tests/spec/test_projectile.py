"""Synthetic closed-form checks only; not measured data or simulator Gate P."""
import copy
import importlib
import json
import math
import sys
import unittest

from test_setup_validation import BUNDLE, ROOT, setup
from test_experiment_schema import quantity
from test_experiment_validation import validator

sys.path.insert(0, str(ROOT))


class ProjectileTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((ROOT / 'Build/templates/projectile.py').is_file(),
                        'projectile template/oracle has not been implemented')
        self.api = importlib.import_module('Build.templates.projectile')
        self.spec, self.scene = setup('projectile')

    def make(self, **changes):
        s = self.spec
        args = dict(experiment_id=s['experiment_id'], scene=self.scene, scene_root=BUNDLE,
                    origin=s['placement']['origin'], gravity=s['environment']['gravity'],
                    mass=s['body']['mass'], radius=s['body']['radius'],
                    launch_height=s['parameters']['launch_height'],
                    horizontal_speed=s['parameters']['horizontal_speed'],
                    duration=s['simulation']['duration'], time_step=s['simulation']['time_step'],
                    clearance=s['scene']['constraints']['clearance'], seed=42)
        args.update(changes)
        return self.api.make_projectile(**args)

    def test_factory_validates_and_isolates_inputs(self):
        before = copy.deepcopy((self.spec, self.scene))
        spec = self.make()
        expected = copy.deepcopy(self.spec)
        expected['scene']['constraints']['allowed_surface_ids'] = [s['id'] for s in self.scene['surfaces']]
        self.assertEqual(spec, expected)
        self.assertIs(validator.validate_setup(spec, self.scene, BUNDLE), spec)
        spec['parameters']['horizontal_speed']['value'] = 0
        spec['placement']['origin']['value'][0] = 8
        spec['scene']['constraints']['bounds_m']['min'][0] = -100
        self.assertEqual((self.spec, self.scene), before)

    def test_exact_horizontal_flight_and_determinism(self):
        self.scene['gravity']['magnitude_m_s2'] = 8
        spec = self.make(gravity=quantity(8, 'm/s^2'), horizontal_speed=quantity(3, 'm/s'))
        before = copy.deepcopy(spec)
        a = self.api.analytic_projectile(spec, self.scene, BUNDLE, times=[0, 0.25, 0.5])
        self.assertEqual(a, self.api.analytic_projectile(spec, self.scene, BUNDLE, times=[0, 0.25, 0.5]))
        self.assertEqual(a['impact_time']['value'], 0.5)
        self.assertEqual(a['horizontal_range']['value'], 1.5)
        self.assertEqual(a['impact_position']['value'], [1.5, 1, 0])
        self.assertEqual(a['impact_velocity']['value'], [3, -4, 0])
        self.assertEqual([s['position']['value'] for s in a['samples']],
                         [[0, 2, 0], [0.75, 1.75, 0], [1.5, 1, 0]])
        self.assertEqual([s['velocity']['value'] for s in a['samples']],
                         [[3, 0, 0], [3, -2, 0], [3, -4, 0]])
        self.assertEqual(spec, before)
        self.assertEqual(json.loads(json.dumps(a, allow_nan=False)), a)

    def test_zero_horizontal_speed_is_free_fall(self):
        from Build.templates.free_fall import make_free_fall, analytic_free_fall
        p = self.make(horizontal_speed=quantity(0, 'm/s'))
        f = make_free_fall(experiment_id=p['experiment_id'], scene=self.scene, scene_root=BUNDLE,
            origin=p['placement']['origin'], gravity=p['environment']['gravity'],
            mass=p['body']['mass'], radius=p['body']['radius'],
            drop_height=p['parameters']['launch_height'], initial_vertical_velocity=quantity(0, 'm/s'),
            duration=p['simulation']['duration'], time_step=p['simulation']['time_step'],
            clearance=p['scene']['constraints']['clearance'])
        a = self.api.analytic_projectile(p, self.scene, BUNDLE, times=[0, 0.2])
        b = analytic_free_fall(f, self.scene, BUNDLE, times=[0, 0.2])
        self.assertEqual(a['impact_time']['value'], b['impact_time']['value'])
        self.assertEqual(a['impact_position']['value'], b['impact_position']['value'])
        self.assertEqual(a['horizontal_range']['value'], 0)
        for ps, fs in zip(a['samples'], b['samples']):
            self.assertEqual(ps['position']['value'], fs['position']['value'])
            self.assertEqual(ps['velocity']['value'][1], fs['vertical_velocity']['value'])

    def test_translated_origin_and_gravity_variation(self):
        self.spec['placement']['origin']['value'] = [-2, 4, 3]
        for g in (1.62, 9.81, 12):
            with self.subTest(g=g):
                self.scene['gravity']['magnitude_m_s2'] = g
                spec = self.make(gravity=quantity(g, 'm/s^2'), launch_height=quantity(2, 'm'),
                                 horizontal_speed=quantity(2, 'm/s'))
                a = self.api.analytic_projectile(spec, self.scene, BUNDLE)
                t = math.sqrt(4 / g)
                self.assertAlmostEqual(a['impact_time']['value'], t)
                self.assertAlmostEqual(a['horizontal_range']['value'], 2 * t)
                self.assertAlmostEqual(a['impact_position']['value'][0], -2 + 2 * t)
                self.assertEqual(a['impact_position']['value'][1:], [2, 3])
                vx, vy, vz = a['impact_velocity']['value']
                self.assertAlmostEqual(vx * vx + vy * vy + vz * vz, 4 + 4 * g)

    def test_time_domain_short_duration_and_order(self):
        spec = self.make(duration=quantity(0.1, 's'))
        a = self.api.analytic_projectile(spec, self.scene, BUNDLE, times=[0.1, 0, 0.1])
        self.assertGreater(a['impact_time']['value'], 0.1)
        self.assertEqual([s['time']['value'] for s in a['samples']], [0.1, 0, 0.1])
        self.assertEqual(self.api.analytic_projectile(spec, self.scene, BUNDLE)['samples'], [])
        for times in (None, iter([0]), '0', [0] * 100_002,
                      [-0.1], [True], [float('nan')], [float('inf')], [10**400], [0.101]):
            with self.subTest(kind=str(type(times))), self.assertRaisesRegex(ValueError, 'times'):
                self.api.analytic_projectile(spec, self.scene, BUNDLE, times=times)
        full = self.make()
        impact = self.api.analytic_projectile(full, self.scene, BUNDLE)['impact_time']['value']
        end = self.api.analytic_projectile(full, self.scene, BUNDLE, times=[impact])
        self.assertEqual(end['samples'][0]['position'], end['impact_position'])
        with self.assertRaisesRegex(ValueError, 'times'):
            self.api.analytic_projectile(full, self.scene, BUNDLE, times=[math.nextafter(impact, math.inf)])

    def test_factory_rejects_invalid_physics_and_units(self):
        for changes, reason in ((dict(horizontal_speed=quantity(-1, 'm/s')), 'horizontal_speed'),
                                (dict(launch_height=quantity(0, 'm')), 'launch_height'),
                                (dict(horizontal_speed=quantity(1, 'm')), 'unit'),
                                (dict(time_step=quantity(0.1, 's')), 'time_step')):
            with self.subTest(changes=changes), self.assertRaisesRegex(ValueError, reason):
                self.make(**changes)

    def test_oracle_revalidates_input_and_rejects_wrong_template(self):
        spec = self.make()
        spec['parameters']['horizontal_speed']['value'] = -1
        with self.assertRaisesRegex(ValueError, 'horizontal_speed'):
            self.api.analytic_projectile(spec, self.scene, BUNDLE)
        wrong, _ = setup('free_fall')
        with self.assertRaisesRegex(ValueError, 'projectile'):
            self.api.analytic_projectile(wrong, self.scene, BUNDLE)

    def test_bundle_geometry_and_hidden_collision_rechecked(self):
        spec = self.make()
        bad = copy.deepcopy(self.scene)
        bad['assets'][0]['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'SHA256'):
            self.api.analytic_projectile(spec, bad, BUNDLE)
        self.scene['colliders'] = [dict(id='hidden', shape='box', surface_id=None,
            pose=dict(position_m=[0.25, 1.5, 0], rotation_xyzw=[0, 0, 0, 1]), half_extents_m=[0.1]*3)]
        with self.assertRaisesRegex(ValueError, 'collider hidden'):
            self.make()
        # Even a client spec omitting the newly added collider must fail closed.
        with self.assertRaisesRegex(ValueError, 'collider hidden'):
            self.api.analytic_projectile(spec, self.scene, BUNDLE)
        self.scene['colliders'] = []
        self.scene['bounds_m']['max'][0] = 0.1
        with self.assertRaisesRegex(ValueError, 'bounds'):
            self.make()

    def test_provenance_units_and_unknown_uncertainty(self):
        spec = self.make()
        a = self.api.analytic_projectile(spec, self.scene, BUNDLE, times=[0])
        self.assertEqual(a['method'], 'analytic-projectile-v1')
        self.assertEqual(a['input_sources']['horizontal_speed'], spec['parameters']['horizontal_speed']['source'])
        self.assertEqual(a['input_sources']['gravity'], spec['environment']['gravity']['source'])
        for name, unit in [('impact_time', 's'), ('horizontal_range', 'm'),
                           ('impact_position', 'm'), ('impact_velocity', 'm/s')]:
            q = a[name]
            self.assertEqual(q['unit'], unit)
            self.assertEqual(q['source']['label'], 'simulated')
            self.assertEqual(q['source']['evidence'], 'analytic-projectile-v1:experiment/' + spec['experiment_id'])
            self.assertIsNone(q['uncertainty'])
        a['input_sources']['gravity']['label'] = 'unknown'
        self.assertEqual(spec['environment']['gravity']['source']['label'], 'synthetic')


if __name__ == '__main__':
    unittest.main()
