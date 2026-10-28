"""Real local cross-language integration; synthetic evidence, not a physical gate."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/spec'))
from test_setup_validation import BUNDLE, setup
from Build.lab.pipeline import run_lab

INSTRUMENTS = dict(time_resolution_s=1e-6, time_uncertainty_s=1e-6, time_bias_s=0,
                   distance_resolution_m=1e-6, distance_uncertainty_m=1e-6, distance_bias_m=0)


class PipelineTests(unittest.TestCase):
    def write_setup(self, folder, template='free_fall'):
        spec, scene = setup(template)
        spec_path, scene_path = folder / 'spec.json', folder / 'scene.json'
        spec_path.write_text(json.dumps(spec), encoding='utf-8')
        scene_path.write_text(json.dumps(scene), encoding='utf-8')
        shutil.copyfile(BUNDLE / 'points.ply', folder / 'points.ply')
        return spec_path, scene_path

    def test_two_ballistic_templates_reach_actual_fitter(self):
        for template in ('free_fall', 'projectile'):
            with self.subTest(template=template), tempfile.TemporaryDirectory() as tmp:
                spec, scene = self.write_setup(Path(tmp), template)
                before = copy.deepcopy(INSTRUMENTS)
                result = run_lab(spec, scene, instruments=INSTRUMENTS)
                self.assertEqual(INSTRUMENTS, before)
                self.assertEqual(result['fit']['status'], 'ok')
                self.assertLess(abs(result['fit']['gravity']['value'] - 9.81) / 9.81, 0.005)
                self.assertEqual(result['fit']['gravity']['source']['label'], 'simulated')
                self.assertEqual(len(result['observations']['times']), len(result['trajectory']['samples']))
                self.assertIn('input instrument uncertainty not propagated', result['limits'])
                self.assertEqual(result, run_lab(spec, scene, instruments=INSTRUMENTS))
                json.dumps(result, allow_nan=False)

    def test_cli_and_explicit_settings(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec, scene = self.write_setup(Path(tmp))
            instruments = Path(tmp) / 'instruments.json'
            instruments.write_text(json.dumps(INSTRUMENTS), encoding='utf-8')
            process = subprocess.run([sys.executable, '-m', 'Build.lab.pipeline', str(spec), str(scene), str(instruments)],
                                     cwd=ROOT, capture_output=True, text=True, timeout=40)
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertEqual(json.loads(process.stdout)['fit']['status'], 'ok')
            with self.assertRaisesRegex(ValueError, 'six explicit'):
                run_lab(spec, scene, instruments={})
            with self.assertRaises(ValueError):
                run_lab(spec, scene, instruments={**INSTRUMENTS, 'time_resolution_s': True})

    def test_invalid_spec_cannot_enter_simulator(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec, scene = self.write_setup(Path(tmp))
            data = json.loads(spec.read_text(encoding='utf-8'))
            data['simulation']['time_step']['value'] = 0
            spec.write_text(json.dumps(data), encoding='utf-8')
            with self.assertRaises(ValueError):
                run_lab(spec, scene, instruments=INSTRUMENTS)

    def test_cross_process_contract_is_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec, scene = self.write_setup(Path(tmp))
            with patch('Build.lab.pipeline.subprocess.run') as execute:
                execute.return_value.returncode = 0
                execute.return_value.stdout = '{}'
                with self.assertRaisesRegex(ValueError, 'incompatible trajectory'):
                    run_lab(spec, scene, instruments=INSTRUMENTS)


if __name__ == '__main__':
    unittest.main()
