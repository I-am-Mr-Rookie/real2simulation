"""Strict, provenance-carrying numeric values shared by S11 instruments/fitter.

Values produced by the simulation leaves must remain visibly simulated.  The
contract deliberately keeps instrument error separate from reported uncertainty.
"""

from dataclasses import dataclass
import math
from types import MappingProxyType
from typing import Any, Mapping


def _finite(value: Any, name: str) -> float:
    if type(value) not in (int, float):
        raise ValueError(f"{name} must be a finite number, not boolean/NaN/infinity")
    try:
        value = float(value)
    except (OverflowError, ValueError) as error:
        raise ValueError(f"{name} must be a finite number, not boolean/NaN/infinity") from error
    if not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number, not boolean/NaN/infinity")
    return value


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


_FIELDS = frozenset(("value", "unit", "uncertainty", "error", "source"))
_SOURCE_FIELDS = frozenset(("label", "evidence"))
_ALLOWED_UNITS = frozenset(("s", "m", "px", "m/s", "m/s^2"))


@dataclass(frozen=True)
class Quantity:
    """A scalar with unit, uncertainty, error semantics, and provenance.

    ``uncertainty`` is a non-negative standard uncertainty in the value's unit;
    ``error`` is an instrument perturbation or known signed offset.  Neither is
    silently inferred or calibrated by this contract.
    """

    value: float
    unit: str
    uncertainty: float
    source: Mapping[str, str]
    error: float | None = None

    def __post_init__(self) -> None:
        data = {"value": self.value, "unit": self.unit,
                "uncertainty": self.uncertainty, "source": self.source}
        if self.error is not None:
            data["error"] = self.error
        normalized = validate_quantity(data)
        object.__setattr__(self, "value", normalized["value"])
        object.__setattr__(self, "unit", normalized["unit"])
        object.__setattr__(self, "uncertainty", normalized["uncertainty"])
        object.__setattr__(self, "error", normalized.get("error"))
        object.__setattr__(self, "source", MappingProxyType(normalized["source"]))

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
    extra = set(data) - _FIELDS
    if extra:
        raise ValueError(f"quantity has unknown fields: {sorted(extra)}")
    value = _finite(data.get("value"), "value")
    unit = _text(data.get("unit"), "unit")
    if unit not in _ALLOWED_UNITS:
        raise ValueError(f"unit must be one of {sorted(_ALLOWED_UNITS)}")
    uncertainty = _finite(data.get("uncertainty"), "uncertainty")
    if uncertainty < 0:
        raise ValueError("uncertainty must be non-negative")
    source = data.get("source")
    if not isinstance(source, Mapping):
        raise ValueError("source must be an object")
    if source.get("label") != "simulated":
        raise ValueError('source.label must be "simulated" for S11 synthetic values')
    source_extra = set(source) - _SOURCE_FIELDS
    if source_extra:
        raise ValueError(f"source has unknown fields: {sorted(source_extra)}")
    evidence = _text(source.get("evidence"), "source.evidence")
    result: dict[str, Any] = {
        "value": value,
        "unit": unit,
        "uncertainty": uncertainty,
        "source": {"label": "simulated", "evidence": evidence},
    }
    if "error" in data and data["error"] is not None:
        result["error"] = _finite(data["error"], "error")
    return result
