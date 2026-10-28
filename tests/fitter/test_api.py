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
        self.assertEqual(out["covariance"]["model"], "independent_position_time_first_order")
        self.assertIn("independent observation errors", out["covariance"]["assumptions"])
        self.assertIsNone(out["covariance"]["interval"])
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
        self.assertIn("independent observation errors", out["uncertainty"]["assumptions"])

    def test_unavailable_covariance_is_null_and_honest(self):
        data = {"times": [q(0, "s"), q(1, "s"), q(2, "s")], "positions": [q(0, "m"), q(1, "m"), q(4, "m")]}
        for item in data["times"] + data["positions"]:
            item["uncertainty"] = 0
        out = handle({**data, "degree": 2})
        self.assertEqual(out["status"], "ok")
        self.assertFalse(out["covariance"]["valid"])
        self.assertIsNone(out["gravity"])
        self.assertEqual(out["covariance"]["status"], "unavailable")

    def test_declared_uncertainty_floor_and_timing_monotonicity(self):
        def result(sy, st, model="independent_position_time_first_order"):
            times = [q(i / 10, "s") for i in range(20)]
            positions = [q(1 + .4 * (i / 10) + 4.905 * (i / 10)**2, "m") for i in range(20)]
            for item in times:
                item["uncertainty"] = st
            for item in positions:
                item["uncertainty"] = sy
            out = handle({"times": times, "positions": positions, "uncertainty_model": model})
            self.assertEqual(out["status"], "ok", out)
            return out

        from Build.fitter import fit_least_squares, jacobian_covariance
        t = tuple(i / 10 for i in range(20))
        fit = fit_least_squares(t, tuple(1 + .4*x + 4.905*x*x for x in t))
        floor = 2 * jacobian_covariance(fit, sigma=.05).standard_error
        fixed = result(.05, 0)
        timed = result(.05, .01)
        self.assertAlmostEqual(fixed["gravity"]["uncertainty"], floor, places=12)
        self.assertGreater(timed["gravity"]["uncertainty"], fixed["gravity"]["uncertainty"])
        self.assertGreater(result(.1, .01)["gravity"]["uncertainty"], timed["gravity"]["uncertainty"])
        legacy = result(.05, .01, "iid_fixed_clock_scale")
        self.assertAlmostEqual(legacy["gravity"]["uncertainty"], floor, places=12)
        self.assertEqual(legacy["gravity"], result(.05, 10, "iid_fixed_clock_scale")["gravity"])
        self.assertIn("input timing uncertainty not propagated", legacy["uncertainty"]["assumptions"])
        self.assertIn("not a 95% interval", timed["uncertainty"]["quantity_uncertainty"])

    def test_known_declared_sigma_supports_zero_residual_dof(self):
        data = {"times": [q(0, "s"), q(1, "s"), q(2, "s")],
                "positions": [q(0, "m"), q(1, "m"), q(4, "m")]}
        for model in ("iid_fixed_clock_scale", "independent_position_time_first_order"):
            out = handle({**data, "uncertainty_model": model})
            self.assertTrue(out["covariance"]["valid"], out)
            self.assertGreater(out["gravity"]["uncertainty"], 0)
            self.assertIsNone(out["uncertainty"]["residual_variance_floor"])

    def test_large_declared_sigma_is_readable_and_json_safe(self):
        data = {"times": [q(i, "s") for i in range(5)],
                "positions": [q(i*i, "m") for i in range(5)]}
        data["positions"][0]["uncertainty"] = 1e308
        out = handle(data)
        self.assertEqual(out["status"], "ok", out)
        self.assertFalse(out["covariance"]["valid"])
        self.assertIsNone(out["gravity"])
        json.dumps(out, allow_nan=False)


if __name__ == "__main__":
    unittest.main()

