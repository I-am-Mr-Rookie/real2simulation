"""Independent exact-arithmetic / metamorphic audit; inputs remain seconds/metres."""
from fractions import Fraction as F
import math
import unittest

from Build.fitter.core import FitError, fit_least_squares, jacobian_covariance


def reference(times, positions, degree=2, *, sigma=None, sy=None, st=None):
    """Exact rational normal equations, independent of the production float QR.

    The sandwich is the covariance of the OLS linear map under independent
    first-order perturbations, not an errors-in-variables correction.
    """
    x = [[F(t) ** j for j in range(degree + 1)] for t in times]
    y = list(map(F, positions))
    p = degree + 1
    gram = [[sum(row[i] * row[j] for row in x) for j in range(p)] for i in range(p)]
    augmented = [row + [F(i == j) for j in range(p)] for i, row in enumerate(gram)]
    for j in range(p):
        pivot = next(i for i in range(j, p) if augmented[i][j])
        augmented[j], augmented[pivot] = augmented[pivot], augmented[j]
        divisor = augmented[j][j]
        augmented[j] = [v / divisor for v in augmented[j]]
        for i in range(p):
            if i != j:
                factor = augmented[i][j]
                augmented[i] = [a - factor * b for a, b in zip(augmented[i], augmented[j])]
    inverse = [row[p:] for row in augmented]
    weights = [[sum(inverse[i][j] * row[j] for j in range(p)) for row in x] for i in range(p)]
    coefficients = [sum(w * v for w, v in zip(row, y)) for row in weights]
    residuals = [v - sum(c * a for c, a in zip(coefficients, row)) for row, v in zip(x, y)]
    floor = sum(r * r for r in residuals) / (len(times) - p) if len(times) > p else F(0)
    if sigma is not None:
        variances = [F(sigma) ** 2] * len(times)
    elif sy is not None or st is not None:
        sy = sy if sy is not None else [0] * len(times)
        st = st if st is not None else [0] * len(times)
        velocity = [sum(j * coefficients[j] * F(t) ** (j - 1) for j in range(1, p)) for t in times]
        variances = [max(floor, F(a) ** 2 + (v * F(b)) ** 2) for a, b, v in zip(sy, st, velocity)]
    else:
        variances = [floor] * len(times)
    covariance = [[sum(a * b * v for a, b, v in zip(weights[i], weights[j], variances))
                   for j in range(p)] for i in range(p)]
    return coefficients, covariance, residuals


TIMES = (-1.5, -1., -.5, 0., .5, 1., 1.5)
POSITIONS = tuple(3 + .5*t + 4*t*t + e/64 for t, e in zip(TIMES, (1, -2, 3, -1, 2, -3, 1)))
SY = tuple(i / 128 for i in (4, 8, 6, 3, 7, 5, 9))
ST = tuple(i / 4096 for i in (1, 2, 3, 2, 1, 3, 2))


class FitterInvariantTests(unittest.TestCase):
    def test_exact_reference_obeys_interpolation_and_normal_equations(self):
        # A quadratic through (0,y0),(e,y1),(1,y2) has intercept y0 exactly.
        e = 2.**-28
        coefficients, covariance, residuals = reference((0., e, 1.), (0., 0., 0.), sigma=.125)
        self.assertEqual(coefficients, [0, 0, 0])
        self.assertEqual(residuals, [0, 0, 0])
        self.assertEqual(covariance[0][0], F(1, 64))
        self.assertEqual(covariance[0][1], -F(1, 64) * (1 + F(e)) / F(e))
        self.assertEqual(covariance[0][2], F(1, 64) / F(e))
        for degree in (1, 2):
            _, _, residuals = reference(TIMES, POSITIONS, degree)
            for j in range(degree + 1):
                self.assertEqual(sum(F(t)**j * r for t, r in zip(TIMES, residuals)), 0)

    def assert_matrix_close(self, actual, expected, rtol=3e-11):
        for i, row in enumerate(expected):
            for j, value in enumerate(row):
                # Covariance off-diagonals may be exactly zero; normalize by
                # the corresponding marginal scales, never a fixed metre floor.
                scale = math.sqrt(float(expected[i][i])) * math.sqrt(float(expected[j][j]))
                tolerance = rtol * max(abs(float(value)), scale)
                self.assertLessEqual(abs(actual[i][j] - float(value)), tolerance,
                                     (i, j, actual[i][j], float(value), tolerance))

    def assert_reference(self, times, positions, degree=2, *, sigma=None, sy=None, st=None, rtol=3e-11):
        fit = fit_least_squares(times, positions, degree)
        options = {"sigma": sigma} if sigma is not None else {}
        if sy is not None:
            options["position_sigmas"] = sy
        if st is not None:
            options["time_sigmas"] = st
        result = jacobian_covariance(fit, **options)
        expected, covariance, _ = reference(times, positions, degree, sigma=sigma, sy=sy, st=st)
        self.assertTrue(result.valid)
        self.assert_matrix_close(result.covariance, covariance, rtol)
        for actual, value in zip(fit.coefficients, expected):
            self.assertTrue(math.isclose(actual, float(value), rel_tol=rtol, abs_tol=rtol),
                            (actual, float(value)))
        return fit, result

    def test_row_permutations_preserve_full_covariance_with_paired_sigmas(self):
        for degree in (1, 2):
            base, cov = self.assert_reference(TIMES, POSITIONS, degree, sy=SY, st=ST)
            for order in (tuple(reversed(range(7))), (3, 0, 6, 1, 5, 2, 4), (1, 4, 0, 5, 2, 6, 3)):
                with self.subTest(degree=degree, order=order):
                    args = [tuple(v[i] for i in order) for v in (TIMES, POSITIONS, SY, ST)]
                    fit, result = self.assert_reference(*args[:2], degree, sy=args[2], st=args[3])
                    self.assert_matrix_close(result.covariance, cov.covariance)
                    self.assertTrue(math.isclose(fit.rss, base.rss, rel_tol=1e-11))

    def test_first_order_timing_sandwich_and_fit_differential_agree_on_exact_motion(self):
        positions = tuple(3 + .5*t + 4*t*t for t in TIMES)
        fit = fit_least_squares(TIMES, positions)
        result = jacobian_covariance(fit, position_sigmas=SY, time_sigmas=ST)
        self.assertTrue(result.valid)
        # Symmetric 7-point half-second design has sum(t^2)=7, sum(t^4)=49/4.
        # Invert its even 2x2 block analytically, not from production QR state.
        weights = [((7-4*t*t)/21, t/7, 4*(t*t-1)/21) for t in TIMES]
        expected = [[sum(w[i]*w[j]*(sy*sy + (.5+8*t)**2*st*st)
                         for w, t, sy, st in zip(weights, TIMES, SY, ST))
                     for j in range(3)] for i in range(3)]
        self.assert_matrix_close(result.covariance, expected)
        # Separate metamorphic check: perturb one recorded time, holding its
        # recorded position fixed. At zero residual, d(beta)/dt_i=-L_i*v_i.
        h = 2.**-18
        for i, (t, w) in enumerate(zip(TIMES, weights)):
            plus, minus = list(TIMES), list(TIMES)
            plus[i] += h
            minus[i] -= h
            forward = fit_least_squares(plus, positions)
            backward = fit_least_squares(minus, positions)
            for j in range(3):
                derivative = (forward.coefficients[j] - backward.coefficients[j])/(2*h)
                self.assertTrue(math.isclose(derivative, -w[j]*(.5+8*t), rel_tol=1e-7, abs_tol=1e-8))

    def test_time_origin_shift_checks_new_declared_covariance_not_only_coefficients(self):
        for offset in (32., 1024., 2.**30, 2.**45):
            with self.subTest(offset=offset):
                shifted = tuple(t + offset for t in TIMES)
                # Dyadic times remain exactly representable even at 2**45.
                self.assertEqual(tuple(t - offset for t in shifted), TIMES)
                self.assert_reference(shifted, POSITIONS, sy=SY, st=ST)

    def test_huge_time_origin_that_erases_spacing_is_not_an_invariance_claim(self):
        collapsed = tuple(2.**60 + t for t in TIMES)
        self.assertEqual(len(set(collapsed)), 1)
        with self.assertRaises(FitError):
            fit_least_squares(collapsed, POSITIONS)

    def test_position_origin_shift_preserves_declared_covariance(self):
        for offset in (-32., 1024., 2.**20):
            with self.subTest(offset=offset):
                positions = tuple(y + offset for y in POSITIONS)
                self.assertEqual(tuple(y - offset for y in positions), POSITIONS)
                # QR does not centre y: allow roundoff proportional to this
                # moderate exactly-representable offset, not unresolved signals.
                self.assert_reference(TIMES, positions, sy=SY, st=ST, rtol=2e-8)

    def test_scaled_physical_problems_still_use_seconds_and_metres(self):
        base, cov = self.assert_reference(TIMES, POSITIONS, sy=SY, st=ST)
        for time_factor, length_factor in ((8., 32.), (.125, .03125), (1024., 1/1024)):
            with self.subTest(time_factor=time_factor, length_factor=length_factor):
                fit, result = self.assert_reference(
                    tuple(t*time_factor for t in TIMES), tuple(y*length_factor for y in POSITIONS),
                    sy=tuple(s*length_factor for s in SY), st=tuple(s*time_factor for s in ST))
                multipliers = [length_factor / time_factor**j for j in range(3)]
                conserved = [[cov.covariance[i][j]*multipliers[i]*multipliers[j]
                              for j in range(3)] for i in range(3)]
                self.assert_matrix_close(result.covariance, conserved)
                for j in range(3):
                    self.assertTrue(math.isclose(fit.coefficients[j], base.coefficients[j]*multipliers[j], rel_tol=1e-11))
                self.assertEqual((fit.time_unit, fit.position_unit), ("s", "m"))

    def test_known_sigma_override_is_not_the_residual_floor(self):
        fit, conditional = self.assert_reference(TIMES, POSITIONS)
        _, known = self.assert_reference(TIMES, POSITIONS, sigma=1/4096)
        _, declared = self.assert_reference(TIMES, POSITIONS, sy=(1/4096,)*7)
        self.assertLess(known.variance, conditional.variance / 100)
        self.assert_matrix_close(declared.covariance, conditional.covariance)
        zero = jacobian_covariance(fit, sigma=0)
        self.assertTrue(zero.valid)
        self.assertEqual(zero.standard_error, 0)

    def test_nearly_rank_deficient_full_rank_data_against_exact_reference(self):
        for exponent in (12, 20, 28, 36, 40):
            with self.subTest(exponent=exponent):
                epsilon = 2.**-exponent
                times = (0., epsilon, 2*epsilon, 1.)
                # All-zero observations avoid any ambiguity from position
                # subtraction or representation; known sigma defines the noise.
                positions = (0.,)*4
                try:
                    fit = fit_least_squares(times, positions)
                except FitError:
                    continue  # Conservative rejection is honest near lost rank.
                result = jacobian_covariance(fit, sigma=.125)
                _, expected, _ = reference(times, positions, sigma=.125)
                # Conditioning of the clustered rows worsens as epsilon shrinks;
                # an unavailable result is honest, a materially wrong valid one is not.
                if result.valid:
                    self.assert_matrix_close(result.covariance, expected, rtol=.001)
                else:
                    self.assertIsNone(result.covariance)

    def test_minimal_known_noise_covariance_cannot_have_negative_diagonal(self):
        try:
            fit = fit_least_squares((0., 2.**-28, 1.), (0., 0., 0.))
        except FitError:
            return  # Rejecting an unresolved design is not false precision.
        result = jacobian_covariance(fit, sigma=.125)
        if result.valid:
            # Lagrange interpolation gives c0=y0 and Var(c0)=sigma**2,
            # regardless of the ill-conditioned velocity/curvature pair.
            self.assertGreaterEqual(min(result.covariance[i][i] for i in range(3)), 0)
            self.assertTrue(math.isclose(result.covariance[0][0], .125**2, rel_tol=.001))
        else:
            self.assertIsNone(result.covariance)

    def test_minimal_declared_noise_covariance_respects_known_intercept_variance(self):
        try:
            fit = fit_least_squares((0., 2.**-28, 1.), (0., 0., 0.))
        except FitError:
            return
        result = jacobian_covariance(fit, position_sigmas=(.125,)*3)
        if result.valid:
            self.assertTrue(math.isclose(result.covariance[0][0], .125**2, rel_tol=.001),
                            (result.covariance[0][0], .125**2))
        else:
            self.assertIsNone(result.covariance)

    def test_residual_square_underflow_is_unavailable_not_known_zero_noise(self):
        times = (0., 1., 2., 3.)
        positions = (0., 0., 1e-165, 0.)
        _, exact_covariance, exact_residuals = reference(times, positions)
        self.assertTrue(any(r != 0 for r in exact_residuals))
        self.assertGreater(exact_covariance[2][2], 0)
        self.assertEqual(float(exact_covariance[2][2]), 0)
        try:
            fit = fit_least_squares(times, positions)
        except FitError:
            return  # Rejection is acceptable when covariance is unrepresentable.
        for options in ({}, {"position_sigmas": (0.,)*4}):
            with self.subTest(options=options):
                result = jacobian_covariance(fit, **options)
                # The true covariance is below binary64 range. Do not demand
                # impossible positive values, just honest unavailability.
                self.assertFalse(result.valid)
                self.assertIsNone(result.covariance)
        self.assertTrue(jacobian_covariance(fit, sigma=0).valid)

    def test_truly_rank_deficient_design_is_rejected(self):
        with self.assertRaises(FitError):
            fit_least_squares((0., 0., 1., 1.), (1., 1., 3., 3.))


if __name__ == "__main__":
    unittest.main()
