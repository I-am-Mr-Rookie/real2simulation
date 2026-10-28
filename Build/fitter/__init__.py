"""Small, dependency-free numerical core for the virtual laboratory.

Inputs are simulated observations in declared units.  This package never
converts a result into live calibration or Gate M evidence.
"""

from .core import (
    FitError, FitResult, ModelSelection, CovarianceResult, CoverageResult,
    fit_least_squares, fit_motion, select_model, jacobian_covariance,
    coverage_regression, gravity_quantity,
)

__all__ = [
    "FitError", "FitResult", "ModelSelection", "CovarianceResult",
    "CoverageResult", "fit_least_squares", "fit_motion", "select_model",
    "jacobian_covariance", "coverage_regression", "gravity_quantity",
]
