"""Offline, simulation-only adapter from quantity observations to fit JSON."""
from __future__ import annotations

import json
import math
from typing import Any, Mapping

from contracts.fit.quantity import validate_quantity
from .core import FitError, fit_motion, gravity_quantity, jacobian_covariance, select_model


class ApiInputError(ValueError):
    """Readable request/observation contract failure."""


def _request_mapping(request: Any) -> Mapping[str, Any]:
    if not isinstance(request, Mapping):
        raise ApiInputError("request_must_be_an_object")
    return request


def _quantities(request: Mapping[str, Any], key: str, unit: str) -> tuple[float, ...]:
    values = request.get(key)
    if isinstance(values, (str, bytes)) or not values:
        raise ApiInputError(f"{key}_must_be_a_nonempty_sequence")
    try:
        values = tuple(values)
    except TypeError as exc:
        raise ApiInputError(f"{key}_must_be_a_sequence") from exc
    numbers = []
    for index, value in enumerate(values):
        try:
            item = validate_quantity(value)
        except (TypeError, ValueError) as exc:
            raise ApiInputError(f"{key}[{index}]_invalid_quantity: {exc}") from exc
        if item["unit"] != unit:
            raise ApiInputError(f"{key}[{index}]_unit_must_be_{unit}")
        numbers.append(item["value"])
    return tuple(numbers)


def _finite(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ApiInputError(f"{name}_must_be_finite_numeric")
    value = float(value)
    if not math.isfinite(value):
        raise ApiInputError(f"{name}_must_be_finite_numeric")
    return value


def _quantity_json(quantity: Any) -> dict[str, Any]:
    data = quantity.to_dict()
    # Quantity is the source of truth; reject accidental non-JSON numbers.
    _json_safe(data)
    return data


def _json_safe(value: Any) -> None:
    if isinstance(value, Mapping):
        for child in value.values():
            _json_safe(child)
    elif isinstance(value, (tuple, list)):
        for child in value:
            _json_safe(child)
    elif isinstance(value, float) and not math.isfinite(value):
        raise ValueError("response_contains_nonfinite_number")


def _fit_json(fit: Any) -> dict[str, Any]:
    return {
        "degree": fit.degree,
        "coefficients": list(fit.coefficients),
        "fitted": list(fit.fitted),
        "residuals": list(fit.residuals),
        "rss": fit.rss,
        "rmse": fit.rmse,
        "rank": fit.rank,
        "dof": fit.dof,
        "n": fit.n,
        "units": {"time": fit.time_unit, "position": fit.position_unit},
        "source": {"label": "simulated", "evidence": "S11 offline quantity-to-fit adapter"},
    }


def fit_observations(request: Mapping[str, Any]) -> dict[str, Any]:
    """Fit validated simulated time/position quantities; never performs I/O."""
    request = _request_mapping(request)
    unknown = set(request) - {"times", "positions", "degree", "select_model", "uncertainty_model"}
    if unknown:
        raise ApiInputError(f"unknown_request_fields: {sorted(unknown)}")
    select = request.get("select_model", False)
    if type(select) is not bool:
        raise ApiInputError("select_model_must_be_boolean")
    uncertainty_model = request.get("uncertainty_model", "iid_fixed_clock_scale")
    if uncertainty_model != "iid_fixed_clock_scale":
        raise ApiInputError("unsupported_uncertainty_model_input_uncertainty_not_propagated")
    times = _quantities(request, "times", "s")
    positions = _quantities(request, "positions", "m")
    if len(times) != len(positions):
        raise ApiInputError("times_positions_length_mismatch")
    degree = request.get("degree", 2)
    if type(degree) is not int or degree not in (1, 2):
        raise ApiInputError("degree_must_be_integer_1_or_2")
    fit = fit_motion(times, positions, degree)
    result: dict[str, Any] = {
        "status": "ok",
        "fit": _fit_json(fit),
        "uncertainty": {
            "model": uncertainty_model,
            "assumptions": [
                "iid residual noise", "clock fixed", "scale fixed",
                "input quantity uncertainty not propagated",
            ],
        },
    }
    if degree == 2:
        covariance = jacobian_covariance(fit, parameter_index=2)
        result["covariance"] = {
            "valid": covariance.valid,
            "variance": covariance.variance,
            "standard_error": covariance.standard_error,
            "status": "available" if covariance.valid else "unavailable",
            "parameter": "quadratic_position_coefficient",
            "variance_unit": "m^2/s^4",
            "standard_error_unit": "m/s^2",
            "gravity_scale_factor": 2.0,
            "assumptions": ["iid residual noise", "clock fixed", "scale fixed", "input quantity uncertainty not propagated"],
            "source": {"label": "simulated", "evidence": "S11 covariance from fitted residuals"},
        }
        if covariance.valid:
            result["gravity"] = _quantity_json(gravity_quantity(fit, covariance))
        else:
            result["gravity"] = None
    if select:
        selection = select_model(times, positions, (1, 2))
        scores = []
        for score in selection.aic:
            if math.isfinite(score):
                scores.append(score)
            else:
                # JSON cannot represent -inf; retain criterion semantics explicitly.
                scores.append(None)
        result["model_selection"] = {
            "selected_degree": selection.selected_degree,
            "criterion": selection.criterion,
            "aic": scores,
            "aic_status": ["available" if math.isfinite(v) else "unavailable_exact_zero_rss" for v in selection.aic],
            "source": {"label": "simulated", "evidence": "S11 offline model selection"},
        }
    _json_safe(result)
    json.dumps(result, allow_nan=False)
    return result


def handle(request: Any) -> dict[str, Any]:
    """Total adapter: return readable errors instead of leaking tracebacks."""
    try:
        return fit_observations(request)
    except (ApiInputError, FitError, TypeError, ValueError) as exc:
        return {"status": "error", "error": {"code": str(exc)}}

