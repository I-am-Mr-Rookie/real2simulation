"""Reproducible offline Gate C evidence; reuse production guards, not shadow accounting."""
import importlib.util
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("simulated_cap_regression", REPO / "evidence/S20/simulated_cap_regression.py")
regression = importlib.util.module_from_spec(spec)
spec.loader.exec_module(regression)


class SimulatedCapRegression(unittest.TestCase):
    def test_replay_is_deterministic_and_explicitly_simulated(self):
        result = regression.run_regression()
        self.assertEqual(result, regression.run_regression())
        self.assertEqual((result["status"], result["mode"], result["provider_calls"]), ("PASS", "SIMULATED_ONLY", 0))
        self.assertGreaterEqual(len(result["events"]), 30)
        self.assertTrue(all(row["cost_kind"] == "SIMULATED" for row in result["events"]))
        outcomes = {row["scene"]: row["outcome"] for row in result["events"]}
        for scene in ("SIM-meta-4", "SIM-meta-5", "SIM-monthly-floor-below", "SIM-monthly-cap-exact",
                      "SIM-monthly-cap-above", "SIM-credit-floor-below", "SIM-paused-failover"):
            self.assertEqual(outcomes[scene], "SPEND_PAUSED")
        self.assertEqual(outcomes["SIM-monthly-floor-exact"], "PASS")
        self.assertEqual(outcomes["SIM-credit-floor-exact"], "PASS")
        self.assertEqual(outcomes["SIM-modal-tampered-proof"], "SPEND_PAUSED")
        self.assertEqual(outcomes["SIM-active-cap-over"], "SPEND_PAUSED")
        self.assertEqual(outcomes["SIM-active-cap-exact"], "PASS")
        self.assertEqual(len(result["public_library_checks"]), 3)
        self.assertTrue(all(row["outcome"] == "PASS" for row in result["public_library_checks"]))

    def test_weakened_stop_or_floor_is_detected(self):
        for target, value in (("Build.guardrails.accounting.META_ROUTINE_STOP_USD", "121"),
                              ("Build.guardrails.admission.MODAL_FLOOR_USD", "4")):
            with self.subTest(target=target), patch(target, Decimal(value)):
                with self.assertRaisesRegex(AssertionError, "unexpectedly admitted"):
                    regression.run_regression()


if __name__ == "__main__":
    unittest.main()
