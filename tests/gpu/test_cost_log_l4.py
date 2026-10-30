"""Offline L4 list-rate estimates and billing reconciliation; no Modal client."""
import unittest

from Build.gpu.cost_log import RATES, cost, reconcile, scene_log


class L4Cost(unittest.TestCase):
    def test_estimate_includes_cpu_and_memory(self):
        self.assertEqual(RATES["L4"], 0.000222)
        estimate = cost(100, "L4", 2, 16)
        self.assertEqual(estimate["by_resource_usd"],
                         {"L4": 0.0222, "CPU": 0.00262, "Memory": 0.003552})
        self.assertEqual(estimate["total_usd"], 0.028372)
        self.assertEqual(cost(0, "L4", 2, 16)["total_usd"], 0)

    def test_scene_receipt_and_billed_seconds(self):
        remote = {"container_start_epoch": 10, "function_start_epoch": 12,
                  "function_end_epoch": 30, "model_load_s": 3, "inference_s": 15}
        log = scene_log("ap-test", 0, 35, remote, "L4", 2, 16, 2)
        self.assertEqual(log["cost"]["billed"]["status"], "unavailable")
        self.assertEqual(log["cost"]["estimated"], cost(22, "L4", 2, 16))
        self.assertEqual(log["cost"]["upper_bound"], cost(37, "L4", 2, 16))
        rows = [{"object_id": "ap-other", "resource": "L4", "cost": "9"},
                {"object_id": "ap-test", "resource": "L4", "cost": "0.0222"},
                {"object_id": "ap-test", "resource": "CPU", "cost": "0.00262"}]
        reconcile(log, rows, "2026-10-30T00:00:00+00:00")
        self.assertEqual(log["gpu_seconds"]["billed"], 100)
        self.assertEqual(log["cost"]["billed"]["total_usd"], 0.02482)


if __name__ == "__main__":
    unittest.main()
