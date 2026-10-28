"""Dependency-free, simulation-only least-squares virtual-lab core."""
from dataclasses import dataclass
import math
import random

class FitError(ValueError):
    """Invalid input or an unidentifiable requested quantity."""

def _number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise FitError(f"{label}_must_be_numeric_not_bool_or_string")
    try:
        value = float(value)
    except (OverflowError, ValueError) as exc:
        raise FitError(f"{label}_must_be_finite") from exc
    if not math.isfinite(value):
        raise FitError(f"{label}_must_be_finite")
    return value

def _finite(values, label):
    if isinstance(values, (str, bytes)):
        raise FitError(f"{label}_must_be_a_sequence")
    try:
        values = tuple(_number(v, label) for v in values)
    except TypeError as exc:
        raise FitError(f"{label}_must_be_a_sequence") from exc
    if not values:
        raise FitError(f"{label}_must_not_be_empty")
    return values

def _degree(degree):
    if type(degree) is not int or degree not in (1, 2):
        raise FitError("degree_must_be_integer_1_or_2")

def _solve_qr(x, y, degree):
    n, p = len(x), degree + 1
    try:
        center = math.fsum(x) / n
        span = max(x) - min(x)
    except (OverflowError, ValueError) as exc:
        raise FitError("time_arithmetic_overflow") from exc
    if not math.isfinite(center) or not math.isfinite(span) or span == 0:
        raise FitError("time_span_must_be_finite_and_nonzero")
    scale = span / 2.0
    try:
        z = tuple((t - center) / scale for t in x)
    except (OverflowError, ZeroDivisionError, ValueError) as exc:
        raise FitError("time_scaling_overflow") from exc
    if not all(math.isfinite(t) for t in z):
        raise FitError("scaled_times_must_be_finite")
    columns = [tuple(t ** j for t in z) for j in range(p)]
    q, r = [], [[0.0] * p for _ in range(p)]
    for j, col in enumerate(columns):
        v = list(col)
        for _pass in range(2):
            for i in range(j):
                try:
                    correction = math.fsum(a * b for a, b in zip(q[i], v))
                except (OverflowError, ValueError) as exc:
                    raise FitError("qr_projection_overflow") from exc
                r[i][j] += correction
                v = [a - correction * b for a, b in zip(v, q[i])]
        try:
            norm = math.sqrt(math.fsum(a * a for a in v))
        except (OverflowError, ValueError) as exc:
            raise FitError("qr_norm_overflow") from exc
        if not math.isfinite(norm) or norm <= 64 * math.ulp(1.0):
            raise FitError("rank_deficient_design")
        r[j][j] = norm
        q.append(tuple(a / norm for a in v))
    qt_y = [math.fsum(a * b for a, b in zip(qi, y)) for qi in q]
    local = [0.0] * p
    for i in range(p - 1, -1, -1):
        try:
            local[i] = (qt_y[i] - math.fsum(r[i][j] * local[j] for j in range(i + 1, p))) / r[i][i]
        except (OverflowError, ValueError, ZeroDivisionError) as exc:
            raise FitError("qr_solve_overflow") from exc
    coefficients = [0.0] * p
    try:
        for j, value in enumerate(local):
            for k in range(j + 1):
                coefficients[k] += value * math.comb(j, k) * ((-center) ** (j - k)) / (scale ** j)
    except (OverflowError, ZeroDivisionError) as exc:
        raise FitError("physical_coefficients_overflow") from exc
    if not all(math.isfinite(v) for v in coefficients):
        raise FitError("physical_coefficients_nonfinite")
    return tuple(coefficients), tuple(local), center, scale, tuple(tuple(row) for row in r)

def _predict_local(local, times, center, scale):
    result = []
    for raw in times:
        t = _number(raw, "prediction_time")
        z = (t - center) / scale
        if not math.isfinite(z):
            raise FitError("prediction_time_scaling_nonfinite")
        value = math.fsum(c * z ** j for j, c in enumerate(local))
        if not math.isfinite(value):
            raise FitError("prediction_nonfinite")
        result.append(value)
    return tuple(result)

@dataclass(frozen=True)
class FitResult:
    degree: int
    coefficients: tuple[float, ...]
    fitted: tuple[float, ...]
    residuals: tuple[float, ...]
    rss: float
    rmse: float
    rank: int
    dof: int
    n: int
    time_unit: str = "s"
    position_unit: str = "m"
    provenance: str = "simulated"
    design_times: tuple[float, ...] = ()
    _local_coefficients: tuple[float, ...] = ()
    _center: float = 0.0
    _scale: float = 1.0
    _r: tuple[tuple[float, ...], ...] = ()
    _y_scale: float = 1.0
    @property
    def k(self):
        return self.rank
    def predict(self, times):
        return _predict_local(self._local_coefficients, times, self._center, self._scale)

def fit_least_squares(times, positions, degree=2, *, time_unit="s", position_unit="m"):
    _degree(degree)
    if time_unit != "s" or position_unit != "m":
        raise FitError("only_seconds_and_metres_are_supported")
    x, y = _finite(times, "times"), _finite(positions, "positions")
    if len(x) != len(y):
        raise FitError("times_positions_length_mismatch")
    if len(x) <= degree:
        raise FitError("insufficient_observations")
    coefficients, local, center, scale, r = _solve_qr(x, y, degree)
    fitted = _predict_local(local, x, center, scale)
    residuals = tuple(obs - pred for obs, pred in zip(y, fitted))
    try:
        rss = math.fsum(e * e for e in residuals)
    except (OverflowError, ValueError) as exc:
        raise FitError("rss_overflow") from exc
    if not math.isfinite(rss):
        raise FitError("rss_nonfinite")
    return FitResult(degree, coefficients, fitted, residuals, rss, math.sqrt(rss / len(x)),
        degree + 1, len(x) - degree - 1, len(x), time_unit, position_unit, "simulated", x,
        local, center, scale, r, _safe_y_scale(y))

def _safe_y_scale(values):
    try:
        result = math.sqrt(math.fsum(v * v for v in values))
    except (OverflowError, ValueError) as exc:
        raise FitError("position_scale_overflow") from exc
    if not math.isfinite(result):
        raise FitError("position_scale_nonfinite")
    return max(1.0, result)

def fit_motion(times, positions, degree=2, **kwargs):
    return fit_least_squares(times, positions, degree, **kwargs)

@dataclass(frozen=True)
class ModelSelection:
    candidates: tuple[FitResult, ...]
    aic: tuple[float, ...]
    selected_degree: int
    criterion: str = "AIC"

def _aic(fit):
    if fit.rss == 0.0:
        return float("-inf")
    return fit.n * math.log(fit.rss / fit.n) + 2 * fit.k

def select_model(times, positions, degrees=(1, 2), **kwargs):
    if isinstance(degrees, (str, bytes)):
        raise FitError("degrees_must_be_a_nonempty_sequence")
    try:
        degrees = tuple(degrees)
    except TypeError as exc:
        raise FitError("degrees_must_be_a_nonempty_sequence") from exc
    if not degrees:
        raise FitError("degrees_must_be_a_nonempty_sequence")
    candidates = tuple(fit_least_squares(times, positions, d, **kwargs) for d in degrees)
    scores = tuple(_aic(fit) for fit in candidates)
    best = min(range(len(scores)), key=lambda i: scores[i])
    return ModelSelection(candidates, scores, candidates[best].degree)

def _invert(matrix):
    n = len(matrix)
    a = [list(row) + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda i: abs(a[i][col]))
        if not math.isfinite(a[pivot][col]) or abs(a[pivot][col]) <= 64 * math.ulp(1.0):
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

def _sigma2(fit, sigma):
    if sigma is None:
        if fit.dof <= 0:
            return None
        return fit.rss / fit.dof
    value = _number(sigma, "sigma")
    if value < 0:
        raise FitError("sigma_must_be_nonnegative")
    return value * value

def jacobian_covariance(fit, *, sigma=None, parameter_index=None, times=None):
    if not isinstance(fit, FitResult):
        raise FitError("fit_must_be_fit_result")
    if parameter_index is None:
        parameter_index = fit.degree
    if type(parameter_index) is not int or not 0 <= parameter_index <= fit.degree:
        raise FitError("parameter_index_out_of_range")
    if times is not None:
        supplied_times = _finite(times, "times")
        if supplied_times != fit.design_times:
            raise FitError("covariance_times_must_match_fit_design")
    sigma2 = _sigma2(fit, sigma)
    if sigma2 is None:
        return CovarianceResult(None, None, None, False)
    rinv = _invert(fit._r)
    if rinv is None:
        return CovarianceResult(None, None, None, False)
    local_cov = tuple(tuple(sigma2 * math.fsum(rinv[i][k] * rinv[j][k] for k in range(fit.rank))
        for j in range(fit.rank)) for i in range(fit.rank))
    scale = fit._scale
    transform = [[0.0] * fit.rank for _ in range(fit.rank)]
    try:
        for j in range(fit.rank):
            for k in range(j + 1):
                transform[k][j] = math.comb(j, k) * ((-fit._center) ** (j - k)) / scale ** j
        covariance = tuple(tuple(math.fsum(transform[i][a] * local_cov[a][b] * transform[j][b]
            for a in range(fit.rank) for b in range(fit.rank)) for j in range(fit.rank)) for i in range(fit.rank))
    except (OverflowError, ZeroDivisionError):
        return CovarianceResult(None, None, None, False)
    variance = covariance[parameter_index][parameter_index]
    if (not math.isfinite(variance) or variance < 0
            or not all(math.isfinite(v) for row in covariance for v in row)):
        return CovarianceResult(None, None, None, False)
    # A finite local covariance that transforms to zero has lost scale
    # information through floating-point underflow; do not report certainty.
    if variance == 0.0 and local_cov[parameter_index][parameter_index] > 0.0:
        return CovarianceResult(None, None, None, False)
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

def coverage_regression(*, seeds=100, seed=0, true_g=9.81, noise_sigma=0.02, interval_z=1.96):
    if type(seeds) is not int or seeds <= 0 or type(seed) is not int:
        raise FitError("seeds_and_seed_must_be_integers")
    true_g, noise_sigma, interval_z = (_number(true_g, "true_g"), _number(noise_sigma, "noise_sigma"), _number(interval_z, "interval_z"))
    if noise_sigma < 0 or interval_z <= 0:
        raise FitError("noise_sigma_nonnegative_interval_z_positive")
    rng = random.Random(seed)
    times = tuple(i * 0.1 for i in range(20))
    covered = 0
    for _ in range(seeds):
        y = tuple(1.0 + 0.4 * t + 0.5 * true_g * t * t + rng.gauss(0.0, noise_sigma) for t in times)
        fit = fit_least_squares(times, y, 2)
        cov = jacobian_covariance(fit, parameter_index=2)
        estimate = 2.0 * fit.coefficients[2]
        se = 2.0 * cov.standard_error if cov.standard_error is not None else float("nan")
        if math.isfinite(se) and abs(estimate - true_g) <= interval_z * se:
            covered += 1
    fraction = covered / seeds
    return CoverageResult(seeds, covered, fraction, interval_z, true_g, "PASS" if fraction >= 0.90 else "FAIL")

def gravity_quantity(fit, covariance=None, *, provenance="synthetic virtual-lab fit"):
    if fit.degree != 2:
        raise FitError("gravity_quantity_requires_quadratic_fit")
    from contracts.fit.quantity import Quantity
    cov = covariance if covariance is not None else jacobian_covariance(fit, parameter_index=2)
    if not isinstance(cov, CovarianceResult) or not cov.valid or cov.standard_error is None:
        raise FitError("gravity_uncertainty_unavailable")
    uncertainty = 2.0 * cov.standard_error
    if not math.isfinite(uncertainty):
        raise FitError("gravity_uncertainty_nonfinite")
    return Quantity(value=2.0 * fit.coefficients[2], unit="m/s^2", uncertainty=uncertainty,
        source={"label": "simulated", "evidence": provenance})
