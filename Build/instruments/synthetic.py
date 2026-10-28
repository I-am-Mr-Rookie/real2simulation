"""Small, explicit simulation-only instrument models.

These functions do not select calibration values. Every bias, resolution and
reported uncertainty is caller supplied, and every output is labelled simulated.
"""

from __future__ import annotations

import math
import random
from typing import Any

from contracts.fit.quantity import validate_quantity


def _number(value: Any, name: str, *, nonnegative: bool = False) -> float:
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number, not boolean/NaN/infinity")
    value = float(value)
    if nonnegative and value < 0:
        raise ValueError(f"{name} must be non-negative")
    return value


def _resolution(value: Any, name: str) -> float:
    value = _number(value, name)
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


def _quantity(value: float, unit: str, uncertainty: float, provenance: str, *, error=None):
    payload = {"value": value, "unit": unit, "uncertainty": uncertainty,
               "source": {"label": "simulated", "provenance": provenance}}
    if error is not None:
        payload["error"] = error
    return validate_quantity(payload)


def _quantize(value: float, resolution: float) -> float:
    """Round to nearest resolution, with half-away-from-zero ties."""
    magnitude = math.floor(abs(value) / resolution + 0.5) * resolution
    return math.copysign(magnitude, value) if value else 0.0


def stopwatch_observation(true_seconds: float, *, seed: int, bias_s: float,
                          noise_std_s: float, resolution_s: float,
                          uncertainty_s: float) -> dict[str, Any]:
    """Apply seeded reaction noise, signed bias, then stopwatch quantization."""
    true_seconds = _number(true_seconds, "true_seconds", nonnegative=True)
    if type(seed) is not int:
        raise ValueError("seed must be an integer, not boolean")
    bias_s = _number(bias_s, "bias_s")
    noise_std_s = _number(noise_std_s, "noise_std_s", nonnegative=True)
    resolution_s = _resolution(resolution_s, "resolution_s")
    uncertainty_s = _number(uncertainty_s, "uncertainty_s", nonnegative=True)
    noise = random.Random(seed).gauss(0.0, noise_std_s)
    error = bias_s + noise
    observed = _quantize(true_seconds + error, resolution_s)
    return _quantity(observed, "s", uncertainty_s,
                     f"synthetic stopwatch; seed={seed}; resolution_s={resolution_s}",
                     error=observed - true_seconds)


def camera_observation(frame_index: int, time_s: float, x_px: float, y_px: float,
                       *, time_resolution_s: float, pixel_resolution_px: float,
                       time_uncertainty_s: float, pixel_uncertainty_px: float,
                       time_bias_s: float, pixel_bias_px: float) -> dict[str, Any]:
    """Quantize frame time and image coordinates; no unrequested sensor model."""
    if type(frame_index) is not int or frame_index < 0:
        raise ValueError("frame_index must be a non-negative integer")
    time_s = _number(time_s, "time_s", nonnegative=True)
    x_px, y_px = _number(x_px, "x_px"), _number(y_px, "y_px")
    time_resolution_s = _resolution(time_resolution_s, "time_resolution_s")
    pixel_resolution_px = _resolution(pixel_resolution_px, "pixel_resolution_px")
    time_uncertainty_s = _number(time_uncertainty_s, "time_uncertainty_s", nonnegative=True)
    pixel_uncertainty_px = _number(pixel_uncertainty_px, "pixel_uncertainty_px", nonnegative=True)
    time_bias_s = _number(time_bias_s, "time_bias_s")
    pixel_bias_px = _number(pixel_bias_px, "pixel_bias_px")
    provenance = f"synthetic camera; frame={frame_index}; resolutions={time_resolution_s},{pixel_resolution_px}"
    return {"frame_index": frame_index,
            "time": _quantity(_quantize(time_s + time_bias_s, time_resolution_s), "s",
                               time_uncertainty_s, provenance, error=time_bias_s),
            "x": _quantity(_quantize(x_px + pixel_bias_px, pixel_resolution_px), "px",
                           pixel_uncertainty_px, provenance, error=pixel_bias_px),
            "y": _quantity(_quantize(y_px + pixel_bias_px, pixel_resolution_px), "px",
                           pixel_uncertainty_px, provenance, error=pixel_bias_px)}


def ruler_observation(true_distance_m: float, *, resolution_m: float,
                      uncertainty_m: float, bias_m: float) -> dict[str, Any]:
    true_distance_m = _number(true_distance_m, "true_distance_m", nonnegative=True)
    resolution_m = _resolution(resolution_m, "resolution_m")
    uncertainty_m = _number(uncertainty_m, "uncertainty_m", nonnegative=True)
    bias_m = _number(bias_m, "bias_m")
    return _quantity(_quantize(true_distance_m + bias_m, resolution_m), "m", uncertainty_m,
                     f"synthetic ruler; resolution_m={resolution_m}", error=bias_m)


def light_gate_observation(true_seconds: float, *, resolution_s: float,
                           uncertainty_s: float, bias_s: float) -> dict[str, Any]:
    true_seconds = _number(true_seconds, "true_seconds", nonnegative=True)
    resolution_s = _resolution(resolution_s, "resolution_s")
    uncertainty_s = _number(uncertainty_s, "uncertainty_s", nonnegative=True)
    bias_s = _number(bias_s, "bias_s")
    return _quantity(_quantize(true_seconds + bias_s, resolution_s), "s", uncertainty_s,
                     f"synthetic light gate; resolution_s={resolution_s}", error=bias_s)
