"""Synthetic oracle tests, not simulator Gate P or calibrated measurements."""
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


class FreeFallTests(unittest.TestCase):
    def setUp(self):
        # A missing feature is an assertion failure in RED, not an import error.
        self.assertTrue((ROOT / 'Build/templates/free_fall.py').is_file(),
                        'free-fall template/oracle has not been implemented')
        self.api = importlib.import_module('Build.templates.free_fall')
        self.spec, self.scene = setup()

    def make(self, **changes):
        s = self.spec
        args = dict(experiment_id=s['experiment_id'], scene=self.scene, scene_root=BUNDLE,
                    origin=s['placement']['origin'], gravity=s['environment']['gravity'],
                    mass=s['body']['mass'], radius=s['body']['radius'],
                    drop_height=s['parameters']['drop_height'],
                    initial_vertical_velocity=s['parameters']['initial_vertical_velocity'],
                    duration=s['simulation']['duration'], time_step=s['simulation']['time_step'],
                    clearance=s['scene']['constraints']['clearance'], seed=42)
        args.update(changes)
        return self.api.make_free_fall(**args)

    def test_factory_validates_and_deep_copies(self):
        before = copy.deepcopy((self.spec, self.scene))
        spec = self.make()
        self.assertIs(validator.validate_setup(spec, self.scene, BUNDLE), spec)
        expected = copy.deepcopy(self.spec)
        expected['scene']['constraints']['allowed_surface_ids'] = [s['id'] for s in self.scene['surfaces']]
        self.assertEqual(spec, expected)
        spec['parameters']['drop_height']['value'] = 0.5
        spec['scene']['constraints']['bounds_m']['min'][0] = -100
        self.assertEqual((self.spec, self.scene), before)

    def test_rest_drop_exact_case_and_determinism(self):
        self.scene['gravity']['magnitude_m_s2'] = 8
        spec = self.make(gravity=quantity(8, 'm/s^2'))
        before = copy.deepcopy(spec)
        a = self.api.analytic_free_fall(spec, self.scene, BUNDLE, times=[0, 0.25, 0.5])
        self.assertEqual(a, self.api.analytic_free_fall(spec, self.scene, BUNDLE, times=[0, 0.25, 0.5]))
        self.assertEqual(a['impact_time']['value'], 0.5)
        self.assertEqual(a['impact_vertical_velocity']['value'], -4)
        self.assertEqual(a['impact_position']['value'], [0, 1, 0])
        self.assertEqual([x['position']['value'][1] for x in a['samples']], [2, 1.75, 1])
        self.assertEqual([x['vertical_velocity']['value'] for x in a['samples']], [0, -2, -4])
        self.assertEqual(spec, before)
        self.assertEqual(json.loads(json.dumps(a, allow_nan=False)), a)

    def test_signed_velocity_and_upward_apex(self):
        self.scene['gravity']['magnitude_m_s2'] = 8
        for v, expected_t, expected_v in [(3, 1, -5), (-3, 0.25, -5)]:
            with self.subTest(v=v):
                spec = self.make(gravity=quantity(8, 'm/s^2'),
                                 initial_vertical_velocity=quantity(v, 'm/s'))
                a = self.api.analytic_free_fall(spec, self.scene, BUNDLE, times=[0, expected_t])
                self.assertEqual(a['impact_time']['value'], expected_t)
                self.assertEqual(a['impact_vertical_velocity']['value'], expected_v)
                if v > 0:
                    b = self.api.analytic_free_fall(spec, self.scene, BUNDLE, times=[0.375])
                    self.assertEqual(b['samples'][0]['position']['value'][1], 2.5625)
                    self.assertEqual(b['samples'][0]['vertical_velocity']['value'], 0)

    def test_stable_downward_root(self):
        spec = self.make(initial_vertical_velocity=quantity(-100_000, 'm/s'),
                         time_step=quantity(5e-8, 's'), duration=quantity(0.001, 's'))
        a = self.api.analytic_free_fall(spec, self.scene, BUNDLE)
        self.assertGreater(a['impact_time']['value'], 0)
        self.assertAlmostEqual(a['impact_time']['value'], 1e-5, delta=1e-13)

    def test_short_duration_does_not_fake_impact_sample(self):
        spec = self.make(duration=quantity(0.1, 's'))
        a = self.api.analytic_free_fall(spec, self.scene, BUNDLE, times=[0.1])
        self.assertGreater(a['impact_time']['value'], 0.1)
        with self.assertRaisesRegex(ValueError, 'times'):
            self.api.analytic_free_fall(spec, self.scene, BUNDLE, times=[0.2])

    def test_input_rejections(self):
        for change in [dict(drop_height=quantity(-1, 'm')),
                       dict(gravity=quantity(1, 'm/s^2')),
                       dict(time_step=quantity(1, 's'))]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.make(**change)
        spec = self.make()
        for t in [-1, True, math.nan, math.inf, 2, '0.1']:
            with self.subTest(t=t), self.assertRaisesRegex(ValueError, 'times'):
                self.api.analytic_free_fall(spec, self.scene, BUNDLE, times=[t])
        self.spec['template'] = 'projectile'
        self.spec['parameters'] = dict(launch_height=quantity(1, 'm'), horizontal_speed=quantity(1, 'm/s'))
        with self.assertRaisesRegex(ValueError, 'free_fall'):
            self.api.analytic_free_fall(self.spec, self.scene, BUNDLE)

    def test_authority_and_collision_rechecked(self):
        spec = self.make()
        bad_scene = copy.deepcopy(self.scene)
        bad_scene['assets'][0]['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'SHA256'):
            self.api.analytic_free_fall(spec, bad_scene, BUNDLE)
        self.scene['colliders'] = [dict(id='hidden', shape='box', surface_id=None,
            pose=dict(position_m=[0, 1.5, 0], rotation_xyzw=[0, 0, 0, 1]), half_extents_m=[0.1]*3)]
        with self.assertRaisesRegex(ValueError, 'collider hidden'):
            self.make()
        self.scene['colliders'] = []
        self.scene['bounds_m']['max'][1] = 1
        with self.assertRaises(ValueError):
            self.make()

    def test_signed_huge_sample_times_are_readable_value_errors(self):
        spec = self.make()
        before = copy.deepcopy(spec)
        for value in (10**1000, -(10**1000)):
            with self.subTest(sign=value > 0), self.assertRaisesRegex(ValueError, r'\$\.times\[0\]'):
                self.api.analytic_free_fall(spec, self.scene, BUNDLE, times=[value])
        self.assertEqual(spec, before)

    def test_provenance_units_and_no_fake_uncertainty(self):
        a = self.api.analytic_free_fall(self.make(), self.scene, BUNDLE, times=[0])
        self.assertEqual(a['input_sources']['gravity'], self.spec['environment']['gravity']['source'])
        self.assertEqual(a['impact_time']['unit'], 's')
        self.assertEqual(a['impact_vertical_velocity']['unit'], 'm/s')
        for q in [a['impact_time'], a['impact_vertical_velocity'], a['impact_position']]:
            self.assertEqual(q['source']['label'], 'simulated')
            self.assertIn('analytic', q['source']['evidence'])
            self.assertIsNone(q['uncertainty'])
        self.assertEqual(a['method'], 'analytic-free-fall-v1')


if __name__ == '__main__':
    unittest.main()
