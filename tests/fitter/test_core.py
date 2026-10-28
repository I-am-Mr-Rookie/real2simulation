import math
import unittest

from Build.fitter import (
    FitError, coverage_regression, fit_least_squares, jacobian_covariance,
    select_model, gravity_quantity,
)


class FitterCoreTests(unittest.TestCase):
    def test_quadratic_recovery_and_residuals(self):
        t = (0., .1, .2, .3, .4, .5)
        y = tuple(2.0 + 1.5*x + 4.0*x*x for x in t)
        fit = fit_least_squares(t, y, 2)
        for actual, expected in zip(fit.coefficients, (2.0, 1.5, 4.0)):
            self.assertAlmostEqual(actual, expected, places=12)
        self.assertTrue(all(abs(v) < 1e-14 for v in fit.residuals))
        self.assertEqual(fit.dof, 3)

    def test_rank_and_input_rejection(self):
        with self.assertRaises(FitError):
            fit_least_squares((1., 1., 1.), (1., 2., 3.), 2)
        with self.assertRaises(FitError):
            fit_least_squares((0., 1.), (0., 1.), 2)
        with self.assertRaises(FitError):
            fit_least_squares((0., math.nan), (0., 1.), 1)
        with self.assertRaises(FitError):
            fit_least_squares((0., 1., 2.), (0., 1., 4.), 2, time_unit="frames")

    def test_aic_selects_quadratic_and_perfect_fit_is_finite_handled(self):
        t = tuple(i / 10 for i in range(8))
        y = tuple(1 + 2*x + 3*x*x for x in t)
        selected = select_model(t, y)
        self.assertEqual(selected.selected_degree, 2)
        self.assertEqual(selected.selected_degree, 2)
        self.assertTrue(math.isfinite(selected.aic[1]))

    def test_covariance_and_g_jacobian(self):
        t = tuple(i / 10 for i in range(8))
        y = tuple(1 + 2*x + 4.905*x*x + .01*((-1)**i) for i, x in enumerate(t))
        fit = fit_least_squares(t, y, 2)
        cov = jacobian_covariance(fit, parameter_index=2)
        self.assertTrue(cov.valid)
        self.assertGreater(cov.standard_error, 0)
        self.assertEqual(cov.noise_model, "Gaussian iid residuals; clock and scale held fixed")

    def test_quantity_uses_shared_instrument_contract(self):
        t = tuple(i / 10 for i in range(8))
        fit = fit_least_squares(t, tuple(1 + 2*x + 4.905*x*x for x in t), 2)
        quantity = gravity_quantity(fit)
        self.assertEqual(quantity.to_dict()["source"]["label"], "simulated")
        self.assertEqual(quantity.unit, "m/s^2")

    def test_seeded_coverage_is_observed_not_tuned(self):
        result = coverage_regression()
        self.assertEqual(result.seeds, 100)
        self.assertGreaterEqual(result.coverage, .90)
        self.assertEqual(result.provenance, "simulated")

    def test_large_time_origin_uses_scaled_prediction(self):
        t = tuple(1_000_000_000.0 + i * 0.1 for i in range(12))
        y = tuple(3.0 + 1.5*(x - 1_000_000_000.0) + 0.5*9.81*(x - 1_000_000_000.0)**2 for x in t)
        fit = fit_least_squares(t, y, 2)
        self.assertAlmostEqual(2 * fit.coefficients[2], 9.81, places=7)
        self.assertLess(abs(fit.predict(t)[-1] - y[-1]), 1e-10)

    def test_invalid_scalars_degrees_and_empty_models_are_readable(self):
        for bad in (True, "1", 10**10000, float("nan")):
            with self.assertRaises(FitError):
                fit_least_squares((0., 1., 2.), (0., bad, 2.), 2)
        with self.assertRaises(FitError):
            fit_least_squares((0., 1., 2.), (0., 1., 2.), True)
        with self.assertRaises(FitError):
            select_model((0., 1., 2.), (0., 1., 2.), degrees=())
        with self.assertRaises(FitError):
            select_model((0., 1., 2.), (0., 1., 2.), degrees=(True,))
        with self.assertRaises(FitError):
            fit_least_squares((0., 0., 0.), (1., 2., 3.), 2)

    def test_aic_distinguishes_tiny_real_noise_and_exact_fit(self):
        t = tuple(i / 10 for i in range(8))
        exact = select_model((0., 1., 2., 3.), (1., 3., 5., 7.), degrees=(1,))
        noisy = select_model(t, tuple(1 + 2*x + 3*x*x + 1e-12*((-1)**i) for i, x in enumerate(t)))
        self.assertEqual(exact.aic[0], float('-inf'))
        self.assertTrue(math.isfinite(noisy.aic[1]))

    def test_finite_huge_input_overflow_abstains_with_fit_error(self):
        with self.assertRaises(FitError):
            fit_least_squares((1e308, 1e308 - 1e292, 1e308 - 2e292), (1., 2., 3.), 2)

    def test_covariance_requires_dof_or_explicit_sigma_and_validates_sigma(self):
        fit = fit_least_squares((0., 1., 2.), (1., 2., 5.), 2)
        self.assertFalse(jacobian_covariance(fit).valid)
        self.assertTrue(jacobian_covariance(fit, sigma=0).valid)
        for bad in (True, "0", -1, float("nan")):
            with self.assertRaises(FitError):
                jacobian_covariance(fit, sigma=bad)
        with self.assertRaises(FitError):
            jacobian_covariance(fit, parameter_index=True)


if __name__ == "__main__":
    unittest.main()
