"""Synthetic analytic references only, not simulator or measured Gate P evidence."""
import copy
import importlib
import json
import math
import sys
import unittest

from test_setup_validation import BUNDLE, ROOT, setup
from test_experiment_schema import quantity

sys.path.insert(0, str(ROOT))


class RampTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((ROOT / 'Build/templates/ramp.py').is_file(), 'ramp API missing')
        self.api = importlib.import_module('Build.templates.ramp')
        self.spec, self.scene = setup('ramp')

    def make(self, **changes):
        s = self.spec
        args = dict(experiment_id=s['experiment_id'], scene=self.scene, scene_root=BUNDLE,
                    origin=s['placement']['origin'], gravity=s['environment']['gravity'],
                    mass=s['body']['mass'], radius=s['body']['radius'],
                    duration=s['simulation']['duration'], time_step=s['simulation']['time_step'],
                    clearance=s['scene']['constraints']['clearance'], seed=42,
                    **s['parameters'])
        args.update(changes)
        return self.api.make_ramp(**args)

    def oracle(self, spec=None, **kw):
        return self.api.analytic_ramp(spec or self.spec, self.scene, BUNDLE, **kw)

    def test_factory_validates_and_copies(self):
        before = copy.deepcopy((self.spec, self.scene))
        made = self.make()
        expected = copy.deepcopy(self.spec)
        expected['scene']['constraints']['allowed_surface_ids'] = [s['id'] for s in self.scene['surfaces']]
        self.assertEqual(made, expected)
        made['parameters']['length']['value'] = 9
        self.assertEqual((self.spec, self.scene), before)

    def test_exact_frictionless_answer_and_samples(self):
        self.spec['environment']['gravity']['value'] = 8
        self.scene['gravity']['magnitude_m_s2'] = 8
        self.spec['parameters']['incline_angle']['value'] = math.pi / 6
        self.spec['parameters']['friction_coefficient']['value'] = 0
        self.spec['parameters']['initial_speed']['value'] = 1
        self.spec['parameters']['length']['value'] = 1
        # a=4, L=1, u=1 => T=.5, v=3.
        r = self.oracle(times=[0, .25, .5])
        self.assertAlmostEqual(r['acceleration']['value'], 4)
        self.assertAlmostEqual(r['end_time']['value'], .5)
        self.assertAlmostEqual(r['end_speed']['value'], 3)
        self.assertAlmostEqual(r['samples'][1]['distance']['value'], .375)
        for got, expected in zip(r['end_position']['value'], [math.sqrt(3)/2, 1.5, 0]):
            self.assertAlmostEqual(got, expected)
        self.assertEqual(r['samples'][-1]['distance']['value'], 1)

    def test_friction_energy_and_velocity_direction(self):
        r = self.oracle(times=[0, .1])
        p = self.spec['parameters']; g = 9.81
        a = g*(math.sin(.5)-.1*math.cos(.5))
        self.assertAlmostEqual(r['end_speed']['value']**2, 2*a)
        self.assertAlmostEqual(r['end_time']['value'], math.sqrt(2/a))
        v = r['samples'][1]['velocity']['value']
        self.assertAlmostEqual(v[0], .1*a*math.cos(.5))
        self.assertAlmostEqual(v[1], -.1*a*math.sin(.5))
        self.assertEqual(v[2], 0)

    def test_determinism_provenance_and_no_mutation(self):
        before = copy.deepcopy((self.spec, self.scene))
        r = self.oracle(times=[.1, 0, .1])
        self.assertEqual(r, self.oracle(times=[.1, 0, .1]))
        json.dumps(r, allow_nan=False)
        self.assertEqual(r['method'], 'analytic-ramp-v1')
        self.assertEqual(r['input_sources']['length'], self.spec['parameters']['length']['source'])
        self.assertEqual(r['end_time']['source']['label'], 'simulated')
        self.assertIsNone(r['end_time']['uncertainty'])
        r['input_sources']['length']['label'] = 'unknown'
        self.assertEqual((self.spec, self.scene), before)

    def test_duration_bounds_samples_not_reference(self):
        self.spec['simulation']['duration']['value'] = .01
        self.assertGreater(self.oracle()['end_time']['value'], .01)
        with self.assertRaisesRegex(ValueError, 'times'):
            self.oracle(times=[.02])

    def test_bad_times(self):
        for times in ([True], [-1], [math.nan], [math.inf], [10**1000], ['0'], None, {}, [0]*100002):
            with self.subTest(times_type=type(times).__name__):
                with self.assertRaisesRegex(ValueError, 'times'):
                    self.oracle(times=times)

    def test_reject_nonaccelerating_regime_at_both_entries(self):
        self.spec['parameters']['friction_coefficient']['value'] = 1
        for entry in (self.make, self.oracle):
            with self.assertRaisesRegex(ValueError, 'positive downhill acceleration'):
                entry()

    def test_invalid_units_and_timestep_rejected(self):
        with self.assertRaises(ValueError):
            self.make(length=quantity(1, 's'))
        with self.assertRaises(ValueError):
            self.make(time_step=quantity(.1, 's'))
        self.spec['parameters']['length']['value'] = math.nan
        with self.assertRaises(ValueError):
            self.oracle()

    def test_bundle_and_geometry_revalidated(self):
        self.scene['bounds_m']['max'][0] = .1
        self.spec['scene']['constraints']['bounds_m'] = copy.deepcopy(self.scene['bounds_m'])
        for entry in (self.make, self.oracle):
            with self.assertRaises(ValueError):
                entry()

    def test_asset_integrity_revalidated(self):
        # Hash mutation is detected by the authoritative bundle validator.
        self.scene['assets'][0]['sha256'] = '0'*64
        for entry in (self.make, self.oracle):
            with self.assertRaises(ValueError):
                entry()

    def test_endpoint_duration_and_gravity_scaling(self):
        for g in (1.62, 9.81, 20):
            self.spec['environment']['gravity']['value'] = g
            self.scene['gravity']['magnitude_m_s2'] = g
            self.spec['simulation']['duration']['value'] = 3
            r = self.oracle()
            t = r['end_time']['value']
            sampled = self.oracle(times=[t])['samples'][0]
            self.assertEqual(sampled['position'], r['end_position'])
            self.assertEqual(sampled['velocity'], r['end_velocity'])
            self.assertAlmostEqual(.5*r['acceleration']['value']*t*t, 1)
            with self.assertRaisesRegex(ValueError, 'times'):
                self.oracle(times=[math.nextafter(t, math.inf)])

    def test_wrong_template_rejected(self):
        spec, scene = setup('projectile')
        with self.assertRaisesRegex(ValueError, 'requires ramp'):
            self.api.analytic_ramp(spec, scene, BUNDLE)


if __name__ == '__main__':
    unittest.main()
