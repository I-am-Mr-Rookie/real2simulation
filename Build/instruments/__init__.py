"""Deterministic synthetic instrument models for S11."""

from .synthetic import (
    camera_observation,
    light_gate_observation,
    ruler_observation,
    stopwatch_observation,
)

__all__ = [
    "camera_observation",
    "light_gate_observation",
    "ruler_observation",
    "stopwatch_observation",
]
