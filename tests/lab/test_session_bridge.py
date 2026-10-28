import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('s10_bridge', ROOT / 'Build/lab/session-bridge.py')
MODULE = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(MODULE)

class BridgeTests(unittest.TestCase):
    def test_normal_dto_is_the_actual_validated_export_for_all_four_templates(self):
        from Build.lab.regression import regression_case
        from Build.simulator.export_validated_setup import export
        for template in ('free_fall', 'projectile', 'ramp', 'pendulum'):
            with self.subTest(template=template), tempfile.TemporaryDirectory() as tmp:
                spec, scene, _ = regression_case(Path(tmp), template)
                expected = export(spec, scene)
                with patch('Build.simulator.export_validated_setup.export', wraps=export) as actual_export:
                    start = MODULE.handle({'action': 'start', 'template': template, 'mystery': False})
                self.assertEqual(actual_export.call_count, 1)
                self.assertEqual(start['browserSimulation'], {'mode': 'normal', 'validatedSetup': expected})
                self.assertEqual(start['source'], 'simulated')
                self.assertTrue(expected['scene']['synthetic'])
                self.assertEqual(expected['scene']['provenance']['method'], 'synthetic')
                sim = expected['spec']['simulation']
                self.assertLessEqual(round(sim['duration']['value'] / sim['time_step']['value']) + 1, 2000)
                self.assertLessEqual(len(start['observations']), 2000)

    def test_mystery_has_no_public_setup_or_authored_gravity_for_ballistic_seeds(self):
        for template in ('free_fall', 'projectile'):
            for seed in (0, 1, 2**31, 2**32 - 1):
                with self.subTest(template=template, seed=seed), patch.object(MODULE.secrets, 'randbits', return_value=seed):
                    start = MODULE.handle({'action': 'start', 'template': template, 'mystery': True})
                self.assertEqual(start['status'], 'ok')
                self.assertNotIn('browserSimulation', start)
                self.assertNotIn('gravity', start)
                public = {key: value for key, value in start.items() if key != 'private'}
                for forbidden in ('validatedSetup', 'artifact_version', 'seed', 'gravity_m_s2', 'setup'):
                    self.assertNotIn(forbidden, json.dumps(public))

    def test_export_exception_is_redacted_without_setup(self):
        for mystery in (False, True):
            with patch('Build.simulator.export_validated_setup.export', side_effect=ValueError('private seed gravity setup')):
                result = MODULE.handle({'action': 'start', 'template': 'free_fall', 'mystery': mystery})
            self.assertEqual(result, {'status': 'error', 'error': {'code': 'lab_bridge_failed'}})

    def test_uncaught_protocol_exception_is_redacted(self):
        output = io.StringIO()
        with patch.object(MODULE, '_start', side_effect=RuntimeError('private seed gravity setup')), \
             patch.object(sys, 'stdin', io.StringIO('{"action":"start","template":"free_fall","mystery":true}')), \
             patch.object(sys, 'stdout', output):
            MODULE.main()
        self.assertEqual(json.loads(output.getvalue()), {'status': 'error', 'error': {'code': 'invalid_json'}})

    def test_oversized_fractional_and_invalid_horizons_fail_before_spawning(self):
        from Build.simulator.export_validated_setup import export
        for duration, dt in ((2, 0.001), (0.2005, 0.001), (0.2, 0), (-1, 0.001), (True, 0.001), (1, float('nan'))):
            def changed_export(*args):
                artifact = export(*args)
                artifact['spec']['simulation']['duration']['value'] = duration
                artifact['spec']['simulation']['time_step']['value'] = dt
                return artifact
            with self.subTest(duration=duration, dt=dt), \
                 patch('Build.simulator.export_validated_setup.export', side_effect=changed_export), \
                 patch.object(MODULE.subprocess, 'Popen') as popen:
                result = MODULE.handle({'action': 'start', 'template': 'free_fall'})
            self.assertEqual(result, {'status': 'error', 'error': {'code': 'invalid_simulation_horizon'}})
            popen.assert_not_called()

    def test_setup_editing_remains_outside_fixed_request_allowlist(self):
        for mystery in (False, True):
            for key in ('browserSimulation', 'validatedSetup', 'private', 'seed', 'gravity'):
                result = MODULE.handle({'action': 'start', 'template': 'free_fall', 'mystery': mystery, key: {}})
                self.assertEqual(result, {'status': 'error', 'error': {'code': 'invalid_start_request'}})

    def test_mystery_seed_changes_private_gravity_and_actual_fit(self):
        values = []
        for seed in (0, 2**31):
            with patch.object(MODULE.secrets, 'randbits', return_value=seed):
                start = MODULE.handle({'action': 'start', 'template': 'free_fall', 'mystery': True})
            self.assertEqual(start['status'], 'ok')
            fit = MODULE.handle({'action': 'fit', 'observations': start['observations']})
            self.assertEqual(fit['status'], 'ok')
            self.assertAlmostEqual(fit['gravity']['value'], start['private']['gravity_m_s2'], places=3)
            values.append(fit['gravity']['value'])
        self.assertGreater(abs(values[0] - values[1]), 5)

    def test_all_templates_use_actual_s08_factories(self):
        for template in ('free_fall', 'projectile', 'ramp', 'pendulum'):
            result = MODULE.handle({'action': 'start', 'template': template})
            self.assertEqual(result['status'], 'ok'); self.assertGreater(len(result['observations']), 100)
            self.assertEqual(set(result['observations'][0]), {'time_s', 'position_m'})

    def test_ballistic_fit_uses_actual_s11_and_errors_are_clean(self):
        start = MODULE.handle({'action': 'start', 'template': 'free_fall'})
        result = MODULE.handle({'action': 'fit', 'observations': start['observations']})
        self.assertEqual(result['status'], 'ok'); self.assertAlmostEqual(result['gravity']['value'], 9.81, places=3)
        self.assertEqual(result['uncertainty']['model'], 'independent_position_time_first_order')
        self.assertGreater(result['gravity']['uncertainty'], 0)
        self.assertNotIn('traceback', json.dumps(result).lower())
        self.assertEqual(MODULE.handle({'action': 'fit', 'observations': [{'time_s': 'x', 'position_m': 0}]}), {'status': 'error', 'error': {'code': 'nonfinite_observation'}})

    def test_subprocess_protocol_rejects_bad_action_without_traceback(self):
        proc = subprocess.run([sys.executable, str(ROOT / 'Build/lab/session-bridge.py')], input='{"action":"wat"}', text=True, capture_output=True, cwd=ROOT, timeout=5)
        self.assertEqual(proc.returncode, 0); self.assertEqual(json.loads(proc.stdout)['status'], 'error'); self.assertNotIn('traceback', proc.stdout.lower())

if __name__ == '__main__': unittest.main()
