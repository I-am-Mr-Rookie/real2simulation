import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('s10_bridge', ROOT / 'Build/lab/session-bridge.py')
MODULE = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(MODULE)

class BridgeTests(unittest.TestCase):
    def test_all_templates_use_actual_s08_factories(self):
        for template in ('free_fall', 'projectile', 'ramp', 'pendulum'):
            result = MODULE.handle({'action': 'start', 'template': template})
            self.assertEqual(result['status'], 'ok'); self.assertGreater(len(result['observations']), 100)
            self.assertEqual(set(result['observations'][0]), {'time_s', 'position_m'})

    def test_ballistic_fit_uses_actual_s11_and_errors_are_clean(self):
        start = MODULE.handle({'action': 'start', 'template': 'free_fall'})
        result = MODULE.handle({'action': 'fit', 'observations': start['observations']})
        self.assertEqual(result['status'], 'ok'); self.assertAlmostEqual(result['gravity']['value'], 9.81, places=3)
        self.assertNotIn('traceback', json.dumps(result).lower())
        self.assertEqual(MODULE.handle({'action': 'fit', 'observations': [{'time_s': 'x', 'position_m': 0}]}), {'status': 'error', 'error': {'code': 'nonfinite_observation'}})

    def test_subprocess_protocol_rejects_bad_action_without_traceback(self):
        proc = subprocess.run([sys.executable, str(ROOT / 'Build/lab/session-bridge.py')], input='{"action":"wat"}', text=True, capture_output=True, cwd=ROOT, timeout=5)
        self.assertEqual(proc.returncode, 0); self.assertEqual(json.loads(proc.stdout)['status'], 'error'); self.assertNotIn('traceback', proc.stdout.lower())

if __name__ == '__main__': unittest.main()
