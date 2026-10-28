import json
import math
import unittest

from Build.fitter.api import handle
from Build.instruments.synthetic import ruler_observation, stopwatch_observation


def q(value, unit, evidence="test synthetic"):
    return {"value": value, "unit": unit, "uncertainty": 0.001, "source": {"label": "simulated", "evidence": evidence}}


class ApiTests(unittest.TestCase):
    def test_instrument_to_fit_to_sourced_response(self):
        times, positions = [], []
        for i in range(5):
            t = i * 0.1
            times.append(stopwatch_observation(t, seed=i, bias_s=0, noise_std_s=0,
                                                resolution_s=1e-6, uncertainty_s=1e-6))
            positions.append(ruler_observation(1.0 + 0.4*t + 4.905*t*t,
                                                resolution_m=1e-6, uncertainty_m=1e-6,
                                                bias_m=0))
        out = handle({"times": times, "positions": positions, "degree": 2, "select_model": True})
        self.assertEqual(out["status"], "ok"), out
        self.assertEqual(out["gravity"]["source"]["label"], "simulated")
        self.assertEqual(out["covariance"]["status"], "available")
        self.assertEqual(out["covariance"]["variance_unit"], "m^2/s^4")
        self.assertEqual(out["covariance"]["standard_error_unit"], "m/s^2")
        self.assertIn("input quantity uncertainty not propagated", out["covariance"]["assumptions"])
        json.dumps(out, allow_nan=False)

    def test_invalid_and_degenerate_inputs_are_readable(self):
        bad = handle({"times": [q(0, "s"), q(1, "s")], "positions": [q(0, "m")], "degree": 1})
        self.assertEqual(bad["status"], "error")
        degenerate = handle({"times": [q(0, "s"), q(0, "s"), q(0, "s")], "positions": [q(1, "m"), q(2, "m"), q(3, "m")]})
        self.assertEqual(degenerate["status"], "error")
        self.assertIn("time_span", degenerate["error"]["code"])

    def test_source_and_nonfinite_contract(self):
        wrong = q(1, "m")
        wrong["source"]["label"] = "measured"
        out = handle({"times": [q(0, "s"), q(1, "s"), q(2, "s")], "positions": [wrong] * 3})
        self.assertEqual(out["status"], "error")
        out = handle({"times": [q(0, "s"), q(1, "s"), q(2, "s")], "positions": [q(0, "m"), q(1, "m"), q(4, "m")]})
        self.assertTrue(math.isfinite(out["fit"]["rss"]))
        json.dumps(out, allow_nan=False)

    def test_unsupported_uncertainty_and_strict_options(self):
        data = {"times": [q(0, "s"), q(1, "s"), q(2, "s")], "positions": [q(0, "m"), q(1, "m"), q(4, "m")]}
        self.assertEqual(handle({**data, "select_model": "yes"})["status"], "error")
        self.assertEqual(handle({**data, "uncertainty_model": "weighted"})["status"], "error")

    def test_degree_one_also_reports_uncertainty_assumptions(self):
        data = {"times": [q(0, "s"), q(1, "s"), q(2, "s")], "positions": [q(0, "m"), q(1, "m"), q(2, "m")]}
        out = handle({**data, "degree": 1})
        self.assertEqual(out["status"], "ok")
        self.assertIn("input quantity uncertainty not propagated", out["uncertainty"]["assumptions"])

    def test_unavailable_covariance_is_null_and_honest(self):
        data = {"times": [q(0, "s"), q(1, "s"), q(2, "s")], "positions": [q(0, "m"), q(1, "m"), q(4, "m")]}
        out = handle({**data, "degree": 2})
        self.assertEqual(out["status"], "ok")
        self.assertFalse(out["covariance"]["valid"])
        self.assertIsNone(out["gravity"])
        self.assertEqual(out["covariance"]["status"], "unavailable")


if __name__ == "__main__":
    unittest.main()

