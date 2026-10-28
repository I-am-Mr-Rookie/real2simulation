"""Pure-stdlib polynomial fitting for synthetic virtual-lab observations.

The fitter uses re-centred modified Gram--Schmidt QR rather than normal
equations.  Values are ordinary floats with caller-declared units; the
returned provenance is explicitly ``simulated`` and is not a measurement
approval or a physical Gate M result.
"""

from dataclasses import dataclass
import math
import random


class FitError(ValueError):
    """Input cannot support a finite, identifiable least-squares fit."""


def _finite(values, label):
    values = tuple(float(v) for v in values)
    if not values or not all(math.isfinite(v) for v in values):
        raise FitError(f"{label}_must_be_finite")
    return values


def _solve_qr(x, y, degree):
    n, p = len(x), degree + 1
    center = math.fsum(x) / n
    z = tuple(t - center for t in x)
    columns = [tuple(t ** j for t in z) for j in range(p)]
    q, r = [], [[0.0] * p for _ in range(p)]
    scale = max(math.sqrt(math.fsum(v * v for v in col)) for col in columns)
    tol = max(1e-14, scale * 1e-12)
    for j, col in enumerate(columns):
        v = list(col)
        for i in range(j):
            r[i][j] = math.fsum(a * b for a, b in zip(q[i], v))
            v = [a - r[i][j] * b for a, b in zip(v, q[i])]
        r[j][j] = math.sqrt(math.fsum(a * a for a in v))
        if r[j][j] <= tol:
            raise FitError("rank_deficient_design")
        q.append(tuple(a / r[j][j] for a in v))
    qt_y = [math.fsum(a * b for a, b in zip(qi, y)) for qi in q]
    c = [0.0] * p
    for i in range(p - 1, -1, -1):
        c[i] = (qt_y[i] - math.fsum(r[i][j] * c[j] for j in range(i + 1, p))) / r[i][i]
    # c is in centred time; return coefficients in the declared time origin.
    coefficients = [0.0] * p
    for j, value in enumerate(c):
        for k in range(j + 1):
            coefficients[k] += value * math.comb(j, k) * ((-center) ** (j - k))
    return tuple(coefficients), center, tuple(tuple(row) for row in r)


@dataclass(frozen=True)
class FitResult:
    degree: int
    coefficients: tuple[float, ...]
    fitted: tuple[float, ...]
    residuals: tuple[float, ...]  # observed minus fitted, in position units
    rss: float
    rmse: float
    rank: int
    dof: int
    n: int
    time_unit: str = "s"
    position_unit: str = "m"
    provenance: str = "simulated"
    design_times: tuple[float, ...] = ()

    @property
    def k(self):
        return self.rank

    def predict(self, times):
        return tuple(math.fsum(c * float(t) ** j for j, c in enumerate(self.coefficients)) for t in times)


def fit_least_squares(times, positions, degree=2, *, time_unit="s", position_unit="m"):
    if time_unit != "s" or position_unit != "m":
        raise FitError("only_seconds_and_metres_are_supported")
    x, y = _finite(times, "times"), _finite(positions, "positions")
    if len(x) != len(y):
        raise FitError("times_positions_length_mismatch")
    if degree not in (1, 2) or len(x) <= degree:
        raise FitError("insufficient_observations_or_unsupported_degree")
    coefficients, _center, _r = _solve_qr(x, y, degree)
    fitted = tuple(math.fsum(c * t ** j for j, c in enumerate(coefficients)) for t in x)
    residuals = tuple(obs - pred for obs, pred in zip(y, fitted))
    rss = math.fsum(e * e for e in residuals)
    return FitResult(degree, coefficients, fitted, residuals, rss, math.sqrt(rss / len(x)),
                     degree + 1, len(x) - degree - 1, len(x), time_unit, position_unit,
                     "simulated", x)


def fit_motion(times, positions, degree=2, **kwargs):
    """Named virtual-lab entry point; equivalent to :func:`fit_least_squares`."""
    return fit_least_squares(times, positions, degree, **kwargs)


@dataclass(frozen=True)
class ModelSelection:
    candidates: tuple[FitResult, ...]
    aic: tuple[float, ...]
    selected_degree: int
    criterion: str = "AIC"


def _aic(fit):
    # Floating-point exact polynomials can leave roundoff-only RSS; treat it
    # as a perfect fit at the scale of the observations, not as evidence of a
    # finite noise estimate.
    if fit.rss <= 1e-24:
        return float("-inf")
    return fit.n * math.log(fit.rss / fit.n) + 2 * fit.k


def select_model(times, positions, degrees=(1, 2), **kwargs):
    candidates = tuple(fit_least_squares(times, positions, d, **kwargs) for d in degrees)
    scores = tuple(_aic(fit) for fit in candidates)
    if not all(math.isfinite(s) or s == float("-inf") for s in scores):
        raise FitError("nonfinite_aic")
    best = min(range(len(scores)), key=lambda i: scores[i])
    return ModelSelection(candidates, scores, candidates[best].degree)


def _invert(matrix):
    n = len(matrix)
    a = [list(row) + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda i: abs(a[i][col]))
        if abs(a[pivot][col]) <= 1e-14:
            return None
        a[col], a[pivot] = a[pivot], a[col]
        div = a[col][col]
        a[col] = [v / div for v in a[col]]
        for i in range(n):
            if i != col:
                factor = a[i][col]
                a[i] = [u - factor * v for u, v in zip(a[i], a[col])]
    return tuple(tuple(row[n:]) for row in a)


@dataclass(frozen=True)
class CovarianceResult:
    covariance: tuple[tuple[float, ...], ...] | None
    variance: float | None
    standard_error: float | None
    valid: bool
    noise_model: str = "Gaussian iid residuals; clock and scale held fixed"
    provenance: str = "simulated"


def jacobian_covariance(fit, *, sigma=None, parameter_index=None, times=None):
    """Return conditional covariance; absent dof or rank deficiency is honest."""
    if fit.dof <= 0:
        return CovarianceResult(None, None, None, False)
    if sigma is None:
        sigma2 = fit.rss / fit.dof
    else:
        sigma = float(sigma)
        if not math.isfinite(sigma) or sigma < 0:
            raise FitError("sigma_must_be_finite_nonnegative")
        sigma2 = sigma * sigma
    design = fit.design_times if times is None else times
    if not design:
        return CovarianceResult(None, None, None, False,
                                "Gaussian iid residuals; original design unavailable")
    return covariance_for_observations(design, fit, sigma=sigma,
                                       parameter_index=parameter_index)


def gravity_quantity(fit, covariance=None, *, provenance="synthetic virtual-lab fit"):
    """Adapt quadratic motion output to the shared simulation-only Quantity.

    The contract is imported from ``contracts.fit``; its implementation is
    deliberately owned by the instruments lane and is not duplicated here.
    """
    if fit.degree != 2:
        raise FitError("gravity_quantity_requires_quadratic_fit")
    from contracts.fit.quantity import Quantity
    cov = covariance or jacobian_covariance(fit, parameter_index=2)
    uncertainty = 2.0 * (cov.standard_error or 0.0)
    return Quantity(value=2.0 * fit.coefficients[2], unit="m/s^2",
                    uncertainty=uncertainty,
                    source={"label": "simulated", "provenance": provenance})


def covariance_for_observations(times, fit, *, sigma=None, parameter_index=None):
    """Internal/public companion retaining the actual Jacobian columns."""
    x = _finite(times, "times")
    if len(x) != fit.n or fit.dof <= 0:
        return CovarianceResult(None, None, None, False)
    gram = tuple(tuple(math.fsum(t ** (i + j) for t in x) for j in range(fit.degree + 1))
                 for i in range(fit.degree + 1))
    inverse = _invert(gram)
    if inverse is None:
        return CovarianceResult(None, None, None, False)
    sigma2 = fit.rss / fit.dof if sigma is None else float(sigma) ** 2
    covariance = tuple(tuple(sigma2 * v for v in row) for row in inverse)
    idx = fit.degree if parameter_index is None else parameter_index
    variance = covariance[idx][idx]
    return CovarianceResult(covariance, variance, math.sqrt(max(0.0, variance)), True)


@dataclass(frozen=True)
class CoverageResult:
    seeds: int
    covered: int
    coverage: float
    interval_z: float
    true_value: float
    status: str
    provenance: str = "simulated"


def coverage_regression(*, seeds=100, seed=0, true_g=9.81, noise_sigma=0.02,
                        interval_z=1.96):
    if seeds <= 0 or noise_sigma < 0 or not all(math.isfinite(v) for v in (true_g, noise_sigma, interval_z)):
        raise FitError("invalid_coverage_configuration")
    rng = random.Random(seed)
    times = tuple(i * 0.1 for i in range(20))
    covered = 0
    for _ in range(seeds):
        y = tuple(1.0 + 0.4 * t + 0.5 * true_g * t * t + rng.gauss(0.0, noise_sigma) for t in times)
        fit = fit_least_squares(times, y, 2)
        cov = covariance_for_observations(times, fit, parameter_index=2)
        estimate, se = 2.0 * fit.coefficients[2], 2.0 * (cov.standard_error or float("nan"))
        if math.isfinite(se) and abs(estimate - true_g) <= interval_z * se:
            covered += 1
    return CoverageResult(seeds, covered, covered / seeds, interval_z, true_g,
                          "PASS" if covered / seeds >= 0.90 else "FAIL")
