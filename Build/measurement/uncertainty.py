"""Conditional first-order standard uncertainties; no empirical coverage claim."""
from dataclasses import dataclass
import math

from .inputs import _number, validate_input
from .free_fall import FreeFallFit, FitAbstention, fit_free_fall, _dot


@dataclass(frozen=True)
class ClockClassification:
    classification: str
    capture_seconds_per_pts_second: float | None
    # Evidence strings are declarations, not acquisition verification receipts.
    evidence: str | None


@dataclass(frozen=True)
class UncertaintyResult:
    fit: FreeFallFit
    standard_uncertainty_m_s2: float
    detection_standard_m_s2: float
    timestamp_standard_m_s2: float
    scale_sensitivity: float  # (m/s^2) / (m/px)
    clock_sensitivity: float  # (m/s^2) / (capture s / PTS s)
    scale_clock_correlation: float
    assumption_evidence: str
    method: str = "conditional first-order delta method; no coverage interval"


def classify_clock(data):
    """Classify the declared, validated constant mapping, not the actual camera."""
    parsed = validate_input(data)
    if "capture_timebase_unverified" in parsed.blockers:
        return ClockClassification("unknown", None, None)
    clock = data["timebase"]
    ratio = clock["capture_seconds_per_pts_second"]
    label = "slow_motion" if ratio < 1 else "sped_up" if ratio > 1 else "real_time"
    return ClockClassification(label, ratio, clock["evidence"])


def _precision(model, key, count):
    values = model[key]
    if not isinstance(values, (list, tuple)) or len(values) != count:
        raise ValueError(f"{key} must contain exactly one value per training frame")
    return tuple(_number(value, key) for value in values)


def _component(*factors):
    result = math.prod(factors)
    if not math.isfinite(result):
        raise FitAbstention("nonfinite_uncertainty_propagation")
    if result == 0 and all(factors):
        raise FitAbstention("unresolvable_uncertainty_component")
    return result


def propagate_uncertainty(data, assumptions):
    """Fit prefix only; propagate EXPLICIT external errors of that same OLS fit.

    No residual-derived noise, defaults, bootstrap, suffix tuning or interval.
    See UNCERTAINTY.md for independence, systematic and linearization limits.
    """
    fitted = fit_free_fall(data)
    if fitted.residual_dof <= 0:
        raise FitAbstention("insufficient_training_degrees_of_freedom")
    if not isinstance(assumptions, dict):
        raise ValueError("assumptions must be an object")
    flags = ("independent_frame_errors", "calibration_independent_of_frames",
             "small_error_linearization", "remaining_systematics_negligible")
    fields = (*flags, "detection_std_px", "timestamp_std_pts_s",
              "scale_clock_correlation", "evidence")
    if set(assumptions) - set(fields):
        raise ValueError("unsupported uncertainty fields")
    missing = tuple(key for key in fields
                    if key not in assumptions or assumptions[key] is None)
    if missing:
        raise FitAbstention(*(f"unknown_{key}" for key in missing))
    for key in flags:
        if type(assumptions[key]) is not bool:
            raise ValueError(f"{key} must be boolean")
    unsupported = tuple(key for key in flags if not assumptions[key])
    if unsupported:
        raise FitAbstention(*(f"unsupported_{key}" for key in unsupported))
    evidence = assumptions["evidence"]
    if not isinstance(evidence, str) or not evidence.strip():
        raise ValueError("nonempty assumption evidence required")
    count = len(fitted.training_frames)
    detection = _precision(assumptions, "detection_std_px", count)
    timestamps = _precision(assumptions, "timestamp_std_pts_s", count)
    rho = assumptions["scale_clock_correlation"]
    if type(rho) not in (int, float):
        raise ValueError("scale_clock_correlation must be numeric")
    _number(abs(rho), "scale_clock_correlation")
    if abs(rho) > 1:
        raise ValueError("scale_clock_correlation must lie in [-1, 1]")
    try:
        duration = fitted._duration_s
        ratio = fitted.capture_seconds_per_pts_second
        z = tuple((f.pts_s - fitted.origin_pts_s)*ratio/duration - fitted._center
                  for f in fitted.training_frames)
        # Residualize the quadratic column using the fitter's two-pass QR pattern.
        q0 = (1/math.sqrt(count),) * count
        r01 = _dot(q0, z)
        v1 = tuple(t - r01*q for t, q in zip(z, q0))
        r11 = math.sqrt(_dot(v1, v1))
        q1 = tuple(t/r11 for t in v1)
        squared = tuple(t*t for t in z)
        r02, r12 = _dot(q0, squared), _dot(q1, squared)
        v2 = tuple(t-r02*a-r12*b for t, a, b in zip(squared, q0, q1))
        c0, c1 = _dot(q0, v2), _dot(q1, v2)
        r12 += c1
        v2 = tuple(t-c0*a-c1*b for t, a, b in zip(v2, q0, q1))
        r22 = math.sqrt(_dot(v2, v2))
        if r22/math.sqrt(count) <= 1e-12:
            raise FitAbstention("ill_conditioned_time_samples")
        weights = tuple(2*(v/r22)/r22/duration/duration for v in v2)
        _, b, c = fitted._coefficients_m
        # The residual term matters for noisy OLS: differentiating only y(t)
        # would omit the derivative of the design matrix and misstate timing error.
        timing_jacobian = tuple(
            (2*((2*t-r12/r11)/r22)/r22/duration/duration*residual
             - w*(b+2*c*t))*ratio/duration
            for t, w, residual in zip(z, weights, fitted.training.residuals_m))
        detection_std = math.hypot(*(_component(w, fitted.m_per_px, s)
                                     for w, s in zip(weights, detection)))
        timestamp_std = math.hypot(*(_component(w, s) for w, s in zip(timing_jacobian, timestamps)))
        scale_sensitivity = fitted.g_m_s2/fitted.m_per_px
        clock_sensitivity = -2*(fitted.g_m_s2/ratio)
        a = _component(scale_sensitivity, data["scale"]["uncertainty_m_per_px"])
        b = _component(clock_sensitivity, data["timebase"]["uncertainty_factor"])
        # Factored PSD covariance avoids cancellation when rho is near +/-1.
        total = math.hypot(detection_std, timestamp_std, a+rho*b,
                           math.sqrt((1-rho)*(1+rho))*b)
        values = (total, detection_std, timestamp_std, scale_sensitivity, clock_sensitivity)
        if not all(math.isfinite(v) for v in values):
            raise FitAbstention("nonfinite_uncertainty_propagation")
    except (OverflowError, ZeroDivisionError) as error:
        raise FitAbstention("nonfinite_uncertainty_propagation") from error
    return UncertaintyResult(fitted, *values, rho, evidence)
