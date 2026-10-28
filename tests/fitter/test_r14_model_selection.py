"""Frozen independent model-selection/residual oracles; no product implementation copy."""
from fractions import Fraction
import json
import math
import unittest

from Build.fitter.api import handle
from Build.fitter.core import FitError, fit_motion, select_model


TIMES = (-2., -1., 0., 1., 2.)
NOISE = (1, -4, 6, -4, 1)


def observations(curvature=4, scale=1.):
    return tuple(scale * (curvature * (t*t - 2) + e) for t, e in zip(TIMES, NOISE))


def request(times, positions, **options):
    def q(value, unit):
        return {"value": value, "unit": unit, "uncertainty": 0.,
                "source": {"label": "simulated", "evidence": "R14 analytic synthetic fixture"}}
    return {"times": [q(t, "s") for t in times],
            "positions": [q(y, "m") for y in positions], **options}


def expected_rss(curvature, degree):
    # NOISE is orthogonal to 1,t,t²; (t²-2) has squared norm 14.
    return 70 + (14 * curvature**2 if degree == 1 else 0)


def expected_aic(curvature, degree, scale=1.):
    # Log scaling avoids creating an unrepresentable RSS, independent of production.
    return 5 * (math.log(expected_rss(curvature, degree) / 5) + 2 * math.log(abs(scale))) + 2 * (degree + 1)


class R14ModelSelectionTests(unittest.TestCase):
    def test_analytic_oracle_self_check_exact_orthogonality(self):
        for degree in range(3):
            self.assertEqual(sum(Fraction(t)**degree * e for t, e in zip(TIMES, NOISE)), 0)
        self.assertEqual(sum(e*e for e in NOISE), 70)
        self.assertEqual(sum((t*t-2)**2 for t in TIMES), 14)
        for curvature in (1, 4):
            self.assertEqual(sum(y*y for y in observations(curvature)), expected_rss(curvature, 1))
        self.assertLess(expected_aic(1, 1), expected_aic(1, 2))
        self.assertLess(expected_aic(4, 2), expected_aic(4, 1))

    def test_ordinary_aic_scores_and_choices_have_independent_expected_values(self):
        for curvature, expected_degree in ((1, 1), (4, 2)):
            with self.subTest(curvature=curvature):
                model = select_model(TIMES, observations(curvature))
                self.assertEqual(model.criterion, "AIC")
                self.assertEqual(model.selected_degree, expected_degree)
                for fit, score in zip(model.candidates, model.aic):
                    self.assertEqual(fit.rss, expected_rss(curvature, fit.degree))
                    self.assertAlmostEqual(score, expected_aic(curvature, fit.degree), places=12)

    def test_selection_invariant_under_common_dyadic_scale_and_row_permutation(self):
        for curvature, expected_degree in ((1, 1), (4, 2)):
            for exponent in (-400, -200, 0, 200, 400):
                scale = math.ldexp(1., exponent)
                positions = observations(curvature, scale)
                for order in ((0, 1, 2, 3, 4), (4, 3, 2, 1, 0), (2, 0, 4, 1, 3)):
                    with self.subTest(curvature=curvature, exponent=exponent, order=order):
                        model = select_model(tuple(TIMES[i] for i in order), tuple(positions[i] for i in order))
                        self.assertEqual(model.selected_degree, expected_degree)
                        for fit, score in zip(model.candidates, model.aic):
                            self.assertAlmostEqual(score, expected_aic(curvature, fit.degree, scale), places=10)

    def test_residual_sign_rss_rmse_and_sample_metadata(self):
        for curvature in (1, 4):
            for degree in (1, 2):
                with self.subTest(curvature=curvature, degree=degree):
                    fit = fit_motion(TIMES, observations(curvature), degree)
                    expected = NOISE if degree == 2 else observations(curvature)
                    self.assertEqual(fit.n, 5)
                    self.assertEqual(fit.rank, degree + 1)
                    self.assertEqual(fit.dof, 5 - degree - 1)
                    for actual, residual in zip(fit.residuals, expected):
                        self.assertAlmostEqual(actual, residual, places=12)
                    for observed, fitted, residual in zip(observations(curvature), fit.fitted, fit.residuals):
                        self.assertEqual(observed - fitted, residual)
                    self.assertAlmostEqual(fit.rss, expected_rss(curvature, degree), places=12)
                    self.assertAlmostEqual(fit.rmse, math.sqrt(expected_rss(curvature, degree) / 5), places=12)

    def test_supported_degree_and_minimum_sample_count_matrix(self):
        for degree in (1, 2):
            for n in range(6):
                with self.subTest(degree=degree, n=n):
                    times = tuple(map(float, range(n)))
                    positions = tuple(t*t+t+1 for t in times)
                    output = handle(request(times, positions, degree=degree))
                    if n <= degree:
                        self.assertEqual(output["status"], "error")
                        continue
                    self.assertEqual(output["status"], "ok"), output
                    self.assertEqual(output["fit"]["n"], n)
                    self.assertEqual(output["fit"]["degree"], degree)
                    self.assertEqual(output["fit"]["rank"], degree+1)
                    self.assertEqual(output["fit"]["dof"], n-degree-1)
                    json.dumps(output, allow_nan=False)

    def test_unsupported_degrees_and_options_fail_closed(self):
        for degree in (False, True, 0, 3, -1, 1., "2", None):
            with self.subTest(degree=degree):
                output = handle(request(TIMES, observations(), degree=degree))
                self.assertEqual(output["status"], "error")
                self.assertNotIn("fit", output)
        for select in (0, 1, "yes", None, []):
            with self.subTest(select=select):
                self.assertEqual(handle(request(TIMES, observations(), select_model=select))["status"], "error")

    def test_rank_deficient_candidate_set_fails_closed(self):
        for times in ((0., 0., 0., 0.), (0., 0., 1., 1.)):
            with self.subTest(times=times):
                output = handle(request(times, (1., 2., 3., 4.), select_model=True))
                self.assertEqual(output["status"], "error")
                self.assertNotIn("model_selection", output)

    def test_core_candidate_degrees_are_strict_and_nonempty(self):
        for degrees in (None, False, 1, "12", (), (0,), (3,), (1, True), (1, 2.)):
            with self.subTest(degrees=degrees):
                with self.assertRaises(FitError):
                    select_model(TIMES, observations(), degrees)

    def test_two_point_line_selection_rejects_inadmissible_quadratic_candidate(self):
        data = request((0., 1.), (1., 3.), degree=1)
        self.assertEqual(handle(data)["status"], "ok")
        output = handle({**data, "select_model": True})
        self.assertEqual(output["status"], "error")
        self.assertIn("insufficient_observations", output["error"]["code"])

    def test_selection_is_diagnostic_and_does_not_silently_replace_requested_fit(self):
        output = handle(request(TIMES, observations(1), degree=2, select_model=True))
        self.assertEqual(output["status"], "ok")
        self.assertEqual(output["model_selection"]["selected_degree"], 1)
        self.assertEqual(output["fit"]["degree"], 2)
        self.assertEqual(output["gravity"]["value"], 2.)
        self.assertEqual(output["uncertainty"]["residual_degrees_of_freedom"], 2)

    def test_exact_zero_residual_keeps_existing_explicit_json_status(self):
        output = handle(request((-2., -1., 0., 1., 2.), (0., 0., 0., 0., 0.), select_model=True))
        self.assertEqual(output["status"], "ok")
        self.assertEqual(output["model_selection"]["aic"], [None, None])
        self.assertEqual(output["model_selection"]["aic_status"], ["unavailable_exact_zero_rss"] * 2)
        self.assertEqual(output["fit"]["residuals"], [0.] * 5)
        json.dumps(output, allow_nan=False)

    def test_nonzero_underflow_residuals_do_not_choose_the_wrong_model(self):
        scale = math.ldexp(1., -600)
        self.assertLess(expected_aic(4, 2, scale), expected_aic(4, 1, scale))
        try:
            model = select_model(TIMES, observations(4, scale))
        except FitError:
            return  # Explicit abstention is acceptable; an unjustified selection is not.
        self.assertEqual(model.selected_degree, 2)
        self.assertTrue(all(math.isfinite(score) for score in model.aic))

    def test_api_does_not_mislabel_nonzero_residuals_as_exact_zero(self):
        output = handle(request(TIMES, observations(4, math.ldexp(1., -600)), select_model=True))
        if output["status"] == "error":
            return
        self.assertTrue(any(output["fit"]["residuals"]))
        self.assertNotIn("unavailable_exact_zero_rss", output["model_selection"]["aic_status"])
        self.assertEqual(output["model_selection"]["selected_degree"], 2)
        json.dumps(output, allow_nan=False)

    def test_representable_tiny_rmse_is_not_reported_as_zero(self):
        scale = math.ldexp(1., -600)
        for degree in (1, 2):
            with self.subTest(degree=degree):
                try:
                    fit = fit_motion(TIMES, observations(4, scale), degree)
                except FitError:
                    continue
                expected = scale * math.sqrt(expected_rss(4, degree) / 5)
                self.assertGreater(expected, 0.)
                self.assertTrue(math.isclose(fit.rmse, expected, rel_tol=1e-12, abs_tol=0.))


if __name__ == "__main__":
    unittest.main()
