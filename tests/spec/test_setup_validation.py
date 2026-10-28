"""Synthetic safety fixtures only; no measured physics or gate evidence."""
import copy
import json
import math
from pathlib import Path
import unittest

from test_experiment_schema import fixture
from test_experiment_validation import validator

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / 'test-data/synthetic/scene/room-v1'


def setup(template='free_fall'):
    scene = json.loads((BUNDLE / 'scene.json').read_text(encoding='utf-8'))
    scene['bounds_m'] = {'min': [-10, -1, -10], 'max': [10, 10, 10]}
    scene['colliders'] = []
    scene['gravity'] = dict(status='assumed', direction=[0, -1, 0], magnitude_m_s2=9.81, evidence='synthetic test')
    spec = fixture(template)
    spec['scene'].update(scene_id=scene['id'], scale_status=scene['scale']['status'])
    spec['scene']['constraints']['bounds_m'] = copy.deepcopy(scene['bounds_m'])
    return spec, scene


class SetupValidationTests(unittest.TestCase):
    def check(self, spec, scene):
        return validator.validate_setup(spec, scene, BUNDLE)

    def reject(self, spec, scene, reason):
        with self.assertRaises(validator.ExperimentValidationError) as caught:
            self.check(spec, scene)
        self.assertIn(reason, str(caught.exception))

    def test_four_templates_unchanged(self):
        for template in ('free_fall', 'projectile', 'ramp', 'pendulum'):
            spec, scene = setup(template)
            before = copy.deepcopy((spec, scene))
            self.assertIs(self.check(spec, scene), spec)
            self.assertEqual((spec, scene), before)

    def test_negative_fixture_table(self):
        cases = json.loads((Path(__file__).parent / 'fixtures/unsafe_setups.json').read_text())
        for case in cases:
            with self.subTest(case=case['name']):
                spec, scene = setup(case.get('template', 'free_fall'))
                target = spec if case['target'] == 'spec' else scene
                parts = case['path']
                for key in parts[:-1]:
                    target = target[key]
                target[parts[-1]] = case['value']
                self.reject(spec, scene, case['reason'])

    def test_numeric_validation_cannot_be_bypassed(self):
        spec, scene = setup()
        spec['body']['mass']['value'] = math.nan
        self.reject(spec, scene, 'finite')

    def test_bundle_integrity_is_checked(self):
        spec, scene = setup()
        scene['assets'][0]['sha256'] = '0' * 64
        self.reject(spec, scene, 'SHA256')

    def test_all_colliders_checked_not_only_requested_ids(self):
        for rotation in ([0, 0, 0, 1], [0, 0, math.sin(0.3), math.cos(0.3)]):
            spec, scene = setup()
            scene['colliders'] = [dict(id='hidden', shape='box', surface_id=None,
                pose=dict(position_m=[0, 1.5, 0], rotation_xyzw=rotation), half_extents_m=[0.1]*3)]
            self.reject(spec, scene, 'collider hidden')

    def test_selected_surface_never_exempts_collider(self):
        spec, scene = setup()
        spec['placement']['surface_id'] = 'floor'
        scene['colliders'] = [dict(id='floor-wall', shape='box', surface_id='floor',
            pose=dict(position_m=[0, 1.5, 0], rotation_xyzw=[0, 0, 0, 1]), half_extents_m=[0.1]*3)]
        self.reject(spec, scene, 'collider floor-wall')

    def test_boundary_body_touch_and_clearance(self):
        spec, scene = setup()
        spec['placement']['origin']['value'][0] = 9.98
        spec['scene']['constraints']['clearance']['value'] = 0
        self.check(spec, scene)
        spec['scene']['constraints']['clearance']['value'] = 0.01
        self.reject(spec, scene, 'bounds')

    def test_swept_envelope_includes_ballistic_apex(self):
        spec, scene = setup()
        spec['parameters']['initial_vertical_velocity']['value'] = 20
        self.reject(spec, scene, 'bounds')

    def test_stability_scales_with_radius_and_pendulum_frequency(self):
        spec, scene = setup()
        spec['body']['radius']['value'] = 1e-8
        self.reject(spec, scene, 'time_step')
        spec, scene = setup('pendulum')
        spec['parameters']['length']['value'] = 1e-8
        self.reject(spec, scene, 'time_step')

    def test_contact_and_tiny_numeric_domains_fail_closed(self):
        spec, scene = setup()
        spec['placement']['surface_id'] = 'table'
        self.reject(spec, scene, 'surface')
        spec, scene = setup()
        spec['body']['mass']['value'] = 1e308
        self.reject(spec, scene, 'energy')
        spec, scene = setup()
        spec['environment']['gravity']['value'] = 1e-320
        scene['gravity']['magnitude_m_s2'] = 1e-320
        self.reject(spec, scene, 'numerical')

    def test_separated_collider_and_estimated_scale_are_accepted(self):
        spec, scene = setup()
        scene['scale']['status'] = spec['scene']['scale_status'] = 'estimated'
        scene['colliders'] = [dict(id='far', shape='box', surface_id=None,
            pose=dict(position_m=[5, 2, 0], rotation_xyzw=[0, 0, 0, 1]), half_extents_m=[0.1]*3)]
        self.check(spec, scene)

    def test_scene_authority_mismatch_and_malformed_inputs(self):
        spec, scene = setup()
        scene['gravity']['magnitude_m_s2'] = 1.62
        self.reject(spec, scene, 'gravity')
        spec, scene = setup()
        scene['gravity']['direction'] = [1, 0, 0]
        self.reject(spec, scene, 'gravity')
        spec, scene = setup()
        spec['scene']['scale_status'] = 'estimated'
        self.reject(spec, scene, 'scale')
        for invalid in (None, [], {}, {'assets': []}):
            self.reject(setup()[0], invalid, 'scene')

    def test_stop_plane_displacement_must_survive_world_coordinate_rounding(self):
        for template in ('free_fall', 'projectile'):
            for origin_y in (2.0, 4.0):
                spec, scene = setup(template)
                field = 'drop_height' if template == 'free_fall' else 'launch_height'
                spec['placement']['origin']['value'][1] = origin_y
                spec['parameters'][field]['value'] = math.ulp(origin_y) / 8
                before = copy.deepcopy((spec, scene))
                with self.subTest(template=template, origin=origin_y):
                    self.reject(spec, scene, field)
                    self.assertEqual((spec, scene), before)
                spec['parameters'][field]['value'] = math.ulp(origin_y)
                self.assertIs(self.check(spec, scene), spec)
                self.assertLess(origin_y - spec['parameters'][field]['value'], origin_y)

    def test_rejection_preserves_inputs(self):
        spec, scene = setup()
        spec['placement']['origin']['value'][0] = 100
        before = copy.deepcopy((spec, scene))
        self.reject(spec, scene, 'bounds')
        self.assertEqual((spec, scene), before)


if __name__ == '__main__':
    unittest.main()
