"""S08 acceptance receipt: synthetic contracts/oracles only, never simulator Gate P."""
import copy
import importlib
import json
import math
import sys
import unittest
from pathlib import Path

from test_setup_validation import BUNDLE, ROOT, setup

sys.path.insert(0, str(ROOT))
from contracts.experiment.validate_experiment import (  # noqa: E402
    ExperimentValidationError, validate_setup,
)

TEMPLATES = ('free_fall', 'projectile', 'ramp', 'pendulum')
CASES = json.loads((Path(__file__).parent / 'fixtures/ten_bad_specs.json').read_text())


def api(template):
    module = importlib.import_module(f'Build.templates.{template}')
    return getattr(module, f'make_{template}'), getattr(module, f'analytic_{template}')


def make_args(spec, scene):
    return dict(experiment_id=spec['experiment_id'], scene=scene, scene_root=BUNDLE,
                origin=spec['placement']['origin'], gravity=spec['environment']['gravity'],
                mass=spec['body']['mass'], radius=spec['body']['radius'],
                duration=spec['simulation']['duration'],
                time_step=spec['simulation']['time_step'],
                clearance=spec['scene']['constraints']['clearance'],
                seed=spec['simulation']['seed'], **spec['parameters'])


class S08AcceptanceTests(unittest.TestCase):
    def test_manifest_has_ten_unique_single_mutations_covering_all_templates(self):
        self.assertEqual(len(CASES), 10)
        self.assertEqual(len({c['name'] for c in CASES}), 10)
        self.assertEqual({c['template'] for c in CASES}, set(TEMPLATES))
        for case in CASES:
            self.assertTrue(case['path'])
            self.assertTrue(case['reason'])

    def test_all_four_factories_and_oracles_are_valid_deterministic_and_sourced(self):
        for template in TEMPLATES:
            with self.subTest(template=template):
                spec, scene = setup(template)
                original = copy.deepcopy((spec, scene))
                factory, oracle = api(template)
                made = factory(**make_args(spec, scene))
                self.assertIs(validate_setup(made, scene, BUNDLE), made)
                before = copy.deepcopy(made)
                first = oracle(made, scene, BUNDLE, times=[0, .1])
                self.assertEqual(first, oracle(made, scene, BUNDLE, times=[0, .1]))
                self.assertEqual(first['experiment_id'], made['experiment_id'])
                self.assertEqual(len(first['samples']), 2)
                self.assertEqual(first['samples'][0]['position']['value'],
                                 made['placement']['origin']['value'] if template != 'pendulum'
                                 else [math.sin(.1), 2 - math.cos(.1), 0])
                if template in ('free_fall', 'projectile'):
                    self.assertAlmostEqual(first['impact_time']['value'], math.sqrt(2/9.81))
                elif template == 'ramp':
                    self.assertAlmostEqual(first['acceleration']['value'],
                                           9.81*(math.sin(.5)-.1*math.cos(.5)))
                else:
                    self.assertAlmostEqual(first['period']['value'], 2*math.pi/math.sqrt(9.81))

                def check_envelopes(value):
                    if isinstance(value, dict):
                        if 'value' in value:
                            self.assertEqual(value['source']['label'], 'simulated')
                            self.assertIsNone(value['uncertainty'])
                            self.assertTrue(value['unit'])
                        for child in value.values():
                            check_envelopes(child)
                    elif isinstance(value, list):
                        for child in value:
                            check_envelopes(child)

                check_envelopes(first)
                self.assertEqual(first['input_sources']['gravity'],
                                 made['environment']['gravity']['source'])
                self.assertEqual(made, before)
                self.assertEqual((spec, scene), original)


def rejection_test(case):
    def test(self):
        spec, scene = setup(case['template'])
        # A valid baseline rules out false positives from a broken fixture/bundle.
        factory, oracle = api(case['template'])
        baseline = factory(**make_args(spec, scene))
        oracle(baseline, scene, BUNDLE, times=[0])
        target = baseline
        for key in case['path'][:-1]:
            target = target[key]
        target[case['path'][-1]] = case['value']
        before = copy.deepcopy((baseline, scene))
        for boundary, call in (
            ('setup', lambda: validate_setup(baseline, scene, BUNDLE)),
            ('oracle', lambda: oracle(baseline, scene, BUNDLE, times=[0])),
        ):
            with self.subTest(boundary=boundary):
                with self.assertRaises(ExperimentValidationError) as caught:
                    call()
                self.assertIn(case['reason'], str(caught.exception))
                self.assertTrue(caught.exception.issues)
                self.assertEqual((baseline, scene), before)
    return test


for index, case in enumerate(CASES, 1):
    name = '_'.join(case['name'].split())
    setattr(S08AcceptanceTests, f'test_bad_{index:02d}_{name}', rejection_test(case))


if __name__ == '__main__':
    unittest.main()
