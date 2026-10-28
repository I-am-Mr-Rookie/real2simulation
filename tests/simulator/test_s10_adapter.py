import copy, importlib.util, json, shutil, unittest
from pathlib import Path
from test_experiment_schema import fixture

ROOT = Path(__file__).resolve().parents[2]
loader = importlib.util.spec_from_file_location('s10_export', ROOT / 'Build/simulator/export_validated_setup.py')
module = importlib.util.module_from_spec(loader); loader.loader.exec_module(module)
BUNDLE = ROOT / 'test-data/synthetic/scene/room-v1'

class S10AdapterTests(unittest.TestCase):
    def test_exact_s08_validate_setup_export(self):
        spec = fixture('free_fall'); scene = json.loads((BUNDLE / 'scene.json').read_text())
        scene['bounds_m'] = {'min': [-10, -1, -10], 'max': [10, 10, 10]}; scene['colliders'] = []
        scene['gravity'] = {'status': 'assumed', 'direction': [0, -1, 0], 'magnitude_m_s2': 9.81, 'evidence': 'synthetic test'}
        spec['scene'].update(scene_id=scene['id'], scale_status=scene['scale']['status']); spec['scene']['constraints']['bounds_m'] = copy.deepcopy(scene['bounds_m'])
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            sp, sc = Path(d) / 'spec.json', Path(d) / 'scene.json'; sp.write_text(json.dumps(spec)); sc.write_text(json.dumps(scene)); shutil.copy(BUNDLE / 'points.ply', Path(d) / 'points.ply')
            artifact = module.export(sp, sc)
        self.assertEqual(artifact['validation'], 'validate_setup'); self.assertEqual(artifact['spec'], spec); self.assertEqual(artifact['scene'], scene)

    def test_invalid_spec_cannot_enter_export(self):
        spec = fixture('free_fall'); spec['body']['radius']['value'] = -1
        scene = json.loads((BUNDLE / 'scene.json').read_text())
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            sp, sc = Path(d) / 'spec.json', Path(d) / 'scene.json'; sp.write_text(json.dumps(spec)); sc.write_text(json.dumps(scene))
            with self.assertRaises(module.validator.ExperimentValidationError): module.export(sp, sc)

if __name__ == '__main__': unittest.main()
