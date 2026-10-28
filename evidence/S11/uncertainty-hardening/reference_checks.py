"""Installed NumPy/SciPy are independent test references, not fitter dependencies."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import scipy
from scipy.stats import t as student_t

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from Build.fitter import coverage_regression, fit_least_squares, jacobian_covariance


def main():
    result = coverage_regression(seeds=1)
    reference = float(student_t.ppf(.975, result.degrees_of_freedom))
    assert abs(result.interval_z - reference) < 2e-12
    cases = []
    for origin in (0., 1e9):
        times = np.array([origin + i / 10 for i in range(20)])
        relative = times - origin
        positions = 1 + .4*relative + 4.905*relative**2
        sy = np.linspace(.01, .05, len(times))
        st = np.linspace(.001, .01, len(times))
        fit = fit_least_squares(tuple(times), tuple(positions))
        actual = jacobian_covariance(fit, position_sigmas=tuple(sy), time_sigmas=tuple(st))
        design = np.stack([np.ones(len(times)), relative, relative**2], axis=1)
        influence = np.linalg.pinv(design)
        variance = np.maximum(fit.rss / fit.dof, sy**2 + (.4 + 9.81*relative)**2 * st**2)
        shifted = (influence * variance) @ influence.T
        transform = np.array([[1, -origin, origin**2], [0, 1, -2*origin], [0, 0, 1]])
        expected = transform @ shifted @ transform.T
        got = np.array(actual.covariance)
        assert actual.valid and np.allclose(got, expected, rtol=1e-9, atol=1e-12)
        cases.append({"time_origin": origin, "actual_covariance": got.tolist(),
                      "numpy_reference_covariance": expected.tolist(),
                      "relative_frobenius_error": float(np.linalg.norm(got-expected) / np.linalg.norm(expected))})

    times = np.array([-2., -1., 0., 1., 2.])
    positions = 1 + .4*times + 4.905*times**2
    influence = np.linalg.pinv(np.stack([np.ones(5), times, times**2], axis=1))
    analytic = -influence[2] * (.4 + 9.81*times)
    finite_difference = []
    for i in range(len(times)):
        plus, minus = times.copy(), times.copy()
        plus[i] += 1e-5
        minus[i] -= 1e-5
        a = fit_least_squares(tuple(plus), tuple(positions)).coefficients[2]
        b = fit_least_squares(tuple(minus), tuple(positions)).coefficients[2]
        finite_difference.append((a-b) / 2e-5)
    assert np.allclose(analytic, finite_difference, rtol=1e-8, atol=1e-9)
    print(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "provenance": "simulation-only numerical references",
        "numpy_version": np.__version__, "scipy_version": scipy.__version__,
        "critical_value": result.interval_z, "scipy_student_t_reference": reference,
        "normal_1_96_actual_coverage_at_dof17": float(2*student_t.cdf(1.96, 17)-1),
        "student_t_actual_coverage_at_dof17": float(2*student_t.cdf(result.interval_z, 17)-1),
        "covariance_cases": cases, "timing_derivative_analytic": analytic.tolist(),
        "timing_derivative_finite_difference": finite_difference,
    }, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
