"""Offline S06e checks: timing fields, list-rate estimate, billed only from this app's Modal rows. No Modal/GPU."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cost_log as c

REMOTE = {"container_start_epoch": 1010.0, "function_start_epoch": 1012.0, "function_end_epoch": 1033.0,
          "model_load_s": 18.0, "inference_s": 2.0}  # SYNTHETIC timings
S06D_ROWS = [  # actual S06d rows (evidence/S06/S06e/billing-pre-today-hourly.json) + another app
    {"object_id": "ap-DwCMDeReYWQYBxl3xvR2IO", "resource": "A10G", "cost": "0.00794449"},
    {"object_id": "ap-DwCMDeReYWQYBxl3xvR2IO", "resource": "CPU", "cost": "0.00068323"},
    {"object_id": "ap-DwCMDeReYWQYBxl3xvR2IO", "resource": "Memory", "cost": "0.00092445"},
    {"object_id": "ap-DwCMDeReYWQYBxl3xvR2IO", "resource": "Network Egress", "cost": "0.00000106"},
    {"object_id": "ap-other", "resource": "A10G", "cost": "9.0"},
]


class CostLog(unittest.TestCase):
    def log(self, app="ap-DwCMDeReYWQYBxl3xvR2IO"):
        return c.scene_log(app, 1000.0, 1040.0, REMOTE, "A10G", 2, 16, 2)

    def test_timing_and_estimate(self):
        lg = self.log()
        t = lg["timing_s"]
        self.assertEqual((t["container_boot_s"], t["cold_start_s"], t["cold_start_to_model_ready_s"]), (10.0, 12.0, 30.0))
        self.assertEqual((t["function_s"], t["client_round_trip_s"]), (21.0, 40.0))
        self.assertEqual(lg["gpu_seconds"], {"estimated": 25.0, "upper_bound": 42.0, "billed": None})
        self.assertAlmostEqual(lg["cost"]["estimated"]["total_usd"], 25 * (0.000306 + 2 * 0.0000131 + 16 * 0.00000222))
        self.assertEqual(lg["cost"]["billed"]["status"], "unavailable")

    def test_rates_match_s06d_bill(self):
        # list rates reproduce one common ~26 s container lifetime from three independently billed resources
        secs = [0.00794449 / c.RATES["A10G"], 0.00068323 / (2 * c.RATES["CPU"]), 0.00092445 / (16 * c.RATES["Memory"])]
        self.assertLess(max(secs) - min(secs), 0.2)

    def test_reconcile_billed_only_own_app(self):
        lg = c.reconcile(self.log(), S06D_ROWS, "t")
        b = lg["cost"]["billed"]
        self.assertEqual(b["status"], "billed")
        self.assertAlmostEqual(b["total_usd"], 0.00955323)
        self.assertAlmostEqual(lg["gpu_seconds"]["billed"], 25.962, places=3)

    def test_missing_rows_stay_unavailable(self):
        lg = c.reconcile(self.log("ap-none"), S06D_ROWS, "t")
        self.assertEqual(lg["cost"]["billed"]["status"], "unavailable")
        self.assertIsNone(lg["gpu_seconds"]["billed"])

    def test_missing_remote_timing_refused(self):
        with self.assertRaises(ValueError):
            c.scene_log("ap", 0, 1, {"function_start_epoch": 1}, "A10G", 2, 16, 2)


if __name__ == "__main__":
    unittest.main()
