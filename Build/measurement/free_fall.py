"""Deterministic prefix-only quadratic fit; no calibrated uncertainty or Gate M."""
from dataclasses import dataclass
import math

from .inputs import Frame, validate_input


class FitAbstention(ValueError):
    """Well-formed input cannot support this metric fit."""

    def __init__(self, *blockers):
        self.blockers = tuple(blockers)
        super().__init__(", ".join(blockers))


@dataclass(frozen=True)
class Residuals:
    frame_indices: tuple[int, ...]
    residuals_m: tuple[float, ...]  # observed minus predicted, positive down
    rmse_m: float
    max_abs_m: float


@dataclass(frozen=True)
class FreeFallFit:
    origin_pts_s: float
    capture_seconds_per_pts_second: float
    m_per_px: float
    initial_y_m: float
    initial_velocity_m_s: float
    g_m_s2: float
    training: Residuals
    residual_dof: int
    quadratic_rank_ratio: float
    training_frames: tuple[Frame, ...]
    input_identity: tuple
    # Retain the local polynomial to avoid subtracting large image/time origins.
    _pixel_origin: float
    _duration_s: float
    _center: float
    _coefficients_m: tuple[float, float, float]
    sign_convention: str = "source image y down positive"


def _identity(data):
    scale, clock = data["scale"], data["timebase"]
    return tuple(data[key] for key in (
        "clip_id", "source_sha256", "licence", "provenance", "motion",
        "width_px", "height_px", "continuous_segment_evidence", "last_training_frame"
    )) + tuple(data["approval"][key] for key in ("scope", "evidence")) + tuple(
        scale[key] for key in (
            "method", "m_per_px", "uncertainty_m_per_px", "plane_verified", "evidence"
        )
    ) + tuple(clock[key] for key in (
        "capture_seconds_per_pts_second", "uncertainty_factor", "verified", "evidence"
    ))


def _dot(a, b):
    return math.fsum(x * y for x, y in zip(a, b))


def _finite(*values):
    if not all(math.isfinite(value) for value in values):
        raise FitAbstention("nonfinite_metric_conversion")


def _quadratic(times, positions):
    """Three-column reorthogonalized QR, not unstable normal equations."""
    center = math.fsum(times) / len(times)
    z = tuple(t - center for t in times)
    q0 = (1 / math.sqrt(len(z)),) * len(z)
    r01 = _dot(q0, z)
    v1 = tuple(t - r01*q for t, q in zip(z, q0))
    r11 = math.sqrt(_dot(v1, v1))
    if r11 <= 1e-12:
        raise FitAbstention("ill_conditioned_time_samples")
    q1 = tuple(t / r11 for t in v1)
    squared = tuple(t*t for t in z)
    r02, r12 = _dot(q0, squared), _dot(q1, squared)
    v2 = tuple(t - r02*a - r12*b for t, a, b in zip(squared, q0, q1))
    # A second pass keeps nearly dependent columns from appearing full rank.
    correction0, correction1 = _dot(q0, v2), _dot(q1, v2)
    r02 += correction0
    r12 += correction1
    v2 = tuple(t - correction0*a - correction1*b for t, a, b in zip(v2, q0, q1))
    r22 = math.sqrt(_dot(v2, v2))
    rank_ratio = r22 / math.sqrt(len(z))
    if rank_ratio <= 1e-12:
        raise FitAbstention("ill_conditioned_time_samples")
    q2 = tuple(t / r22 for t in v2)
    c = _dot(q2, positions) / r22
    b = (_dot(q1, positions) - r12*c) / r11
    a = (_dot(q0, positions) - r01*b - r02*c) / math.sqrt(len(z))
    return center, (a, b, c), rank_ratio


def _residuals(frames, *, origin_pts, ratio, scale, pixel_origin,
               duration, center, coefficients):
    a, b, c = coefficients
    residuals = []
    for frame in frames:
        z = (frame.pts_s - origin_pts) * ratio / duration - center
        predicted = (c*z + b)*z + a
        residual = (frame.y_px - pixel_origin)*scale - predicted
        _finite(z, predicted, residual)
        residuals.append(residual)
    maximum = max(abs(r) for r in residuals)
    # Scaling avoids overflow in sum(r*r) even for finite large residuals.
    rmse = maximum * math.sqrt(math.fsum((r/maximum)**2 for r in residuals)
                               / len(residuals)) if maximum else 0.
    return Residuals(tuple(f.frame_index for f in frames), tuple(residuals), rmse, maximum)


def fit_free_fall(data):
    """Validate S07a record, fit ONLY training prefix; malformed => ValueError.

    Scientific/numerical ineligibility => FitAbstention with explicit blockers.
    Source y is down-positive: y(t)=y0+v0*t+g*t²/2, t in capture seconds.
    Calibration/approval evidence is declared, not authenticated by this module.
    """
    validated = validate_input(data)
    if not validated.metric_eligible:
        raise FitAbstention(*validated.blockers)
    frames = validated.training
    origin, pixel_origin = frames[0].pts_s, frames[0].y_px
    ratio = data["timebase"]["capture_seconds_per_pts_second"]
    scale = data["scale"]["m_per_px"]
    try:
        duration = (frames[-1].pts_s - origin) * ratio
        _finite(duration)
        if duration <= 0:
            raise FitAbstention("unresolvable_capture_duration")
        times = tuple((f.pts_s - origin)*ratio / duration for f in frames)
        positions = tuple((f.y_px - pixel_origin)*scale for f in frames)
        _finite(*times, *positions)
        center, coefficients, rank_ratio = _quadratic(times, positions)
        a, b, c = coefficients
        initial_y = pixel_origin*scale + (c*center - b)*center + a
        initial_velocity = (b - 2*c*center) / duration
        g = 2 * (c / duration) / duration
        _finite(*coefficients, initial_y, initial_velocity, g)
        # Numerical zero curvature is not evidence of downward acceleration.
        curvature_floor = 64*math.ulp(max(abs(v) for v in positions))
        if c <= curvature_floor or g <= 0:
            raise FitAbstention("nonpositive_or_unresolved_downward_acceleration")
        training = _residuals(
            frames, origin_pts=origin, ratio=ratio, scale=scale, pixel_origin=pixel_origin,
            duration=duration, center=center, coefficients=coefficients)
    except (OverflowError, ZeroDivisionError) as error:
        raise FitAbstention("nonfinite_metric_conversion") from error
    return FreeFallFit(origin, ratio, scale, initial_y, initial_velocity, g,
                       training, len(frames)-3, rank_ratio, frames, _identity(data),
                       pixel_origin, duration, center, coefficients)


def evaluate_held_out(fitted, data):
    """Evaluate immutable validated suffix separately; never refit/tune anything.

    Caller owns custody of the original precommitted suffix; this function cannot
    authenticate or prevent replacement of held-out observations by that caller.
    """
    validated = validate_input(data)
    if not validated.metric_eligible:
        raise FitAbstention(*validated.blockers)
    if (validated.training != fitted.training_frames
            or _identity(data) != fitted.input_identity):
        raise ValueError("evaluation must use the original training prefix and calibration/provenance")
    try:
        return _residuals(
            validated.held_out, origin_pts=fitted.origin_pts_s,
            ratio=fitted.capture_seconds_per_pts_second, scale=fitted.m_per_px,
            pixel_origin=fitted._pixel_origin, duration=fitted._duration_s,
            center=fitted._center, coefficients=fitted._coefficients_m)
    except (OverflowError, ZeroDivisionError) as error:
        raise FitAbstention("nonfinite_metric_conversion") from error
