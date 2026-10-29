"""Recovery checks reuse the untouched independent R14 analytic oracles."""
from fractions import Fraction
import json
import math
import unittest

from Build.fitter.api import handle
from Build.fitter.core import fit_motion, jacobian_covariance, select_model
from test_r14_model_selection import TIMES, expected_aic, expected_rss, observations, request


class R14ModelRecoveryTests(unittest.TestCase):
    def test_subnormal_norm_rounding_cannot_erase_representable_rmse(self):
        unit = math.ulp(0.)
        times = (0., 1., 2., 3.)
        positions = (-unit, -unit, -unit, unit)
        selection = select_model(times, positions)
        for fit, score in zip(selection.candidates, selection.aic):
            # Exact integer units of the returned binary64 residuals, not another fitter.
            squared_units = sum(Fraction(r / unit)**2 for r in fit.residuals)
            self.assertGreater(squared_units, 0)
            expected_rmse = unit * math.sqrt(float(squared_units / fit.n))
            expected_aic = fit.n * (math.log(float(squared_units / fit.n)) +
                                   2 * math.log(unit)) + 2 * fit.k
            self.assertGreater(expected_rmse, 0.)
            self.assertEqual(fit.rmse, expected_rmse)
            self.assertAlmostEqual(score, expected_aic, places=10)
        output = handle(request(times, positions, degree=1, select_model=True))
        self.assertEqual(output["status"], "ok", output)
        self.assertGreater(output["fit"]["rmse"], 0.)
        self.assertEqual(output["fit"]["rss_status"], "underflow")
        json.dumps(output, allow_nan=False)

    def test_tiny_nonzero_models_are_supported_not_rejected(self):
        for exponent in (-400, -537, -540, -600, -1000):
            for curvature, degree in ((1, 1), (4, 2)):
                for sign in (-1, 1):
                    scale = sign * math.ldexp(1., exponent)
                    for order in ((0, 1, 2, 3, 4), (2, 0, 4, 1, 3)):
                        with self.subTest(exponent=exponent, curvature=curvature, sign=sign, order=order):
                            y = observations(curvature, scale)
                            selection = select_model(tuple(TIMES[i] for i in order), tuple(y[i] for i in order))
                            self.assertEqual(selection.selected_degree, degree)
                            for fit, score in zip(selection.candidates, selection.aic):
                                self.assertAlmostEqual(score, expected_aic(curvature, fit.degree, scale), places=10)
                                expected = abs(scale) * math.sqrt(expected_rss(curvature, fit.degree) / 5)
                                self.assertTrue(math.isclose(fit.rmse, expected, rel_tol=1e-12, abs_tol=0.))

    def test_representable_subnormal_rss_is_not_lost_to_individual_squares(self):
        scale = math.ldexp(1., -540)
        for degree in (1, 2):
            fit = fit_motion(TIMES, observations(4, scale), degree)
            exact = Fraction(expected_rss(4, degree)) * Fraction(scale)**2
            self.assertGreater(float(exact), 0.)
            self.assertEqual(fit.rss, float(exact))

    def test_both_api_models_keep_lost_variance_unavailable(self):
        for exponent in (-540, -600, -1000):
            data = request(TIMES, observations(4, math.ldexp(1., exponent)), select_model=True)
            for model in ("iid_fixed_clock_scale", "independent_position_time_first_order"):
                with self.subTest(exponent=exponent, model=model):
                    output = handle({**data, "uncertainty_model": model})
                    self.assertEqual(output["status"], "ok", output)
                    self.assertEqual(output["model_selection"]["selected_degree"], 2)
                    self.assertEqual(output["model_selection"]["aic_status"], ["available"] * 2)
                    self.assertGreater(output["fit"]["rmse"], 0.)
                    self.assertEqual(output["fit"]["rss_status"], "available" if exponent == -540 else "underflow")
                    self.assertIsNone(output["uncertainty"]["residual_variance_floor"])
                    self.assertFalse(output["covariance"]["valid"])
                    self.assertIsNone(output["covariance"]["variance"])
                    self.assertIsNone(output["gravity"])
                    json.dumps(output, allow_nan=False)

    def test_representable_declared_noise_can_still_support_covariance(self):
        data = request(TIMES, observations(4, math.ldexp(1., -600)))
        for position in data["positions"]:
            position["uncertainty"] = .1
        for model in ("iid_fixed_clock_scale", "independent_position_time_first_order"):
            output = handle({**data, "uncertainty_model": model})
            self.assertEqual(output["status"], "ok", output)
            self.assertTrue(output["covariance"]["valid"], output)
            self.assertGreater(output["gravity"]["uncertainty"], 0.)
            json.dumps(output, allow_nan=False)

    def test_exact_zero_and_explicit_known_zero_are_not_reclassified(self):
        fit = fit_motion(TIMES, (0.,)*5)
        self.assertTrue(jacobian_covariance(fit, sigma=0).valid)
        self.assertEqual(fit.rmse, 0.)
        for model in ("iid_fixed_clock_scale", "independent_position_time_first_order"):
            output = handle(request(TIMES, (0.,)*5, select_model=True, uncertainty_model=model))
            self.assertEqual(output["status"], "ok", output)
            self.assertEqual(output["fit"]["rss_status"], "available")
            self.assertEqual(output["model_selection"]["aic_status"], ["unavailable_exact_zero_rss"] * 2)
            self.assertEqual(output["model_selection"]["selected_degree"], 1)
            self.assertTrue(output["covariance"]["valid"])
            self.assertEqual(output["uncertainty"]["residual_variance_floor"], 0.)
            json.dumps(output, allow_nan=False)


if __name__ == "__main__":
    unittest.main()
