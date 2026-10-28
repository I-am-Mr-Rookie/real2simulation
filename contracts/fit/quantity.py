"""Strict, provenance-carrying numeric values shared by S11 instruments/fitter.

Values produced by the simulation leaves must remain visibly simulated.  The
contract deliberately keeps instrument error separate from reported uncertainty.
"""

from dataclasses import dataclass
import math
from typing import Any, Mapping


def _finite(value: Any, name: str) -> float:
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number, not boolean/NaN/infinity")
    return float(value)


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


@dataclass(frozen=True)
class Quantity:
    """A scalar with unit, uncertainty, error semantics, and provenance.

    ``uncertainty`` is the stated interval/standard uncertainty of the value;
    ``error`` is an instrument perturbation or known signed offset.  Neither is
    silently inferred or calibrated by this contract.
    """

    value: float
    unit: str
    uncertainty: float
    source: Mapping[str, Any]
    error: float | None = None

    def __post_init__(self) -> None:
        validate_quantity(self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "value": self.value,
            "unit": self.unit,
            "uncertainty": self.uncertainty,
            "source": dict(self.source),
        }
        if self.error is not None:
            data["error"] = self.error
        return data


def validate_quantity(data: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and return a shallow normalized copy; reject malformed input."""
    if not isinstance(data, Mapping):
        raise ValueError("quantity must be an object")
    value = _finite(data.get("value"), "value")
    unit = _text(data.get("unit"), "unit")
    uncertainty = _finite(data.get("uncertainty"), "uncertainty")
    if uncertainty < 0:
        raise ValueError("uncertainty must be non-negative")
    source = data.get("source")
    if not isinstance(source, Mapping):
        raise ValueError("source must be an object")
    if source.get("label") != "simulated":
        raise ValueError('source.label must be "simulated" for S11 synthetic values')
    provenance = _text(source.get("provenance"), "source.provenance")
    result: dict[str, Any] = {
        "value": value,
        "unit": unit,
        "uncertainty": uncertainty,
        "source": {**source, "label": "simulated", "provenance": provenance},
    }
    if "error" in data and data["error"] is not None:
        result["error"] = _finite(data["error"], "error")
    return result
