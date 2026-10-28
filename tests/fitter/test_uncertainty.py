"""Independent references for synthetic uncertainty, without runtime dependencies."""
import math
import unittest

from Build.fitter import FitError, coverage_regression, fit_least_squares, jacobian_covariance


class UncertaintyTests(unittest.TestCase):
    def test_student_t_quantile_against_integrated_density(self):
        result = coverage_regression(seeds=1)
        df, upper = result.degrees_of_freedom, result.interval_z
        self.assertEqual(df, 17)
        # Independent Simpson integration of the Student-t density, not a copied quantile.
        steps = 4096
        h = upper / steps
        normalizer = math.exp(math.lgamma((df + 1) / 2) - math.lgamma(df / 2)) / math.sqrt(df * math.pi)
        def density(x):
            return normalizer * (1 + x*x / df) ** (-(df + 1) / 2)
        integral = h / 3 * (density(0) + density(upper) +
                            sum((4 if i % 2 else 2) * density(i*h) for i in range(1, steps)))
        self.assertAlmostEqual(.5 + integral, .975, places=12)
        self.assertEqual(result.nominal_coverage, .95)
        self.assertEqual(result.interval_method, "Student-t residual interval")
        custom = coverage_regression(seeds=1, interval_z=1.96)
        self.assertIsNone(custom.nominal_coverage)
        self.assertEqual(custom.interval_method, "custom SE multiplier")
        zero = coverage_regression(seeds=1, noise_sigma=0)
        self.assertIsNone(zero.nominal_coverage)
        self.assertIn("no stochastic coverage claim", zero.interval_method)

    def test_aggregate_coverage_not_each_random_batch(self):
        batches = [coverage_regression(seed=seed) for seed in range(200)]
        fraction = sum(b.covered for b in batches) / sum(b.seeds for b in batches)
        # Fixed audit population; no seed search and no change to the .90 gate.
        self.assertLess(abs(fraction - .95), .01)
        for batch in batches:
            self.assertEqual(batch.status, "PASS" if batch.coverage >= .90 else "FAIL")

    def test_heteroscedastic_sandwich_against_closed_form_weights(self):
        times = (-2., -1., 0., 1., 2.)
        fit = fit_least_squares(times, tuple(1 + .4*t + 4.905*t*t for t in times))
        sy, st = (.01, .02, .03, .04, .05), (.001, .003, .002, .004, .005)
        cov = jacobian_covariance(fit, position_sigmas=sy, time_sigmas=st)
        # Quadratic OLS coefficient weights on this symmetric design: (t^2-2)/14.
        expected = sum(((t*t - 2) / 14)**2 * (y*y + (.4 + 9.81*t)**2 * s*s)
                       for t, y, s in zip(times, sy, st))
        self.assertTrue(cov.valid)
        self.assertAlmostEqual(cov.variance, expected, places=15)
        self.assertIn("first-order timing", cov.noise_model)

    def test_residual_floor_preserves_conditional_ols(self):
        times = tuple(i / 10 for i in range(10))
        fit = fit_least_squares(times, tuple(1 + t + 4*t*t + .02*(-1)**i for i, t in enumerate(times)))
        conditional = jacobian_covariance(fit)
        declared = jacobian_covariance(fit, position_sigmas=(1e-6,)*len(times))
        self.assertAlmostEqual(declared.variance, conditional.variance, places=12)

    def test_each_declared_sigma_is_monotone_for_fixed_data(self):
        times = (-2., -1., 0., 1., 2.)
        fit = fit_least_squares(times, tuple(1 + .4*t + 4.905*t*t for t in times))
        base = jacobian_covariance(fit, position_sigmas=(.05,)*5, time_sigmas=(.01,)*5)
        for field, default in (("position_sigmas", .05), ("time_sigmas", .01)):
            for i in range(5):
                arguments = {"position_sigmas": [.05]*5, "time_sigmas": [.01]*5}
                arguments[field][i] = 2*default
                increased = jacobian_covariance(fit, **arguments)
                for j in range(3):
                    self.assertGreaterEqual(increased.covariance[j][j] + 1e-16, base.covariance[j][j])

    def test_declared_sigma_boundary_validation_and_overrides(self):
        fit = fit_least_squares((0., 1., 2., 3., 4.), (1., 2., 5., 10., 17.))
        for key in ("position_sigmas", "time_sigmas"):
            for bad in ((.1,), (-1.,)*5, (math.inf,)*5, (math.nan,)*5, (True,)*5, "bad"):
                with self.subTest(key=key, bad=bad), self.assertRaises(FitError):
                    jacobian_covariance(fit, **{key: bad})
        with self.assertRaises(FitError):
            jacobian_covariance(fit, sigma=.1, position_sigmas=(.1,)*5)
        self.assertTrue(jacobian_covariance(fit, sigma=0).valid)
        self.assertEqual(jacobian_covariance(fit, sigma=0).standard_error, 0)
        self.assertFalse(jacobian_covariance(fit, sigma=1e308).valid)
        exact = fit_least_squares((0., 1., 2.), (0., 1., 4.))
        self.assertFalse(jacobian_covariance(exact, position_sigmas=(0.,)*3).valid)
        self.assertTrue(jacobian_covariance(exact, position_sigmas=(.1,)*3).valid)

    def test_clustered_design_abstains_before_losing_covariance_precision(self):
        fit = fit_least_squares((0., 2.**-46, 1.), (0., 0., 0.))
        for kwargs in ({"sigma": .125}, {"position_sigmas": (.125,)*3}):
            result = jacobian_covariance(fit, **kwargs)
            self.assertFalse(result.valid)
            self.assertIsNone(result.covariance)
        self.assertTrue(jacobian_covariance(fit, sigma=0).valid)

    def test_timing_only_stationary_fit_cannot_hide_residual_underflow(self):
        fit = fit_least_squares((-1., 0., 1.), (1e-165, 0., 1e-165), degree=1)
        self.assertEqual(fit._local_coefficients[1], 0)
        self.assertEqual(fit.rss, 0)
        self.assertTrue(any(v != 0 for v in fit.residuals))
        self.assertFalse(jacobian_covariance(fit, time_sigmas=(.1,)*3).valid)
        self.assertTrue(jacobian_covariance(fit, sigma=0).valid)

    def test_positive_sigma_underflow_does_not_report_zero_uncertainty(self):
        fit = fit_least_squares((0., 1., 2., 3., 4.), (0.,)*5)
        self.assertEqual(fit.rss, 0)
        self.assertTrue(jacobian_covariance(fit, sigma=0).valid)
        self.assertFalse(jacobian_covariance(fit, sigma=1e-300).valid)
        self.assertFalse(jacobian_covariance(fit, position_sigmas=(1e-300,)*5).valid)


if __name__ == "__main__":
    unittest.main()
