"""Visibly synthetic per-template fitter requests + full-coverage reports (no real-scene/physical evidence).

Each template gets its own seeded stopwatch noise and its own position model; the fitter is the same polynomial fit for all.
"""
import math

from Build.fitter.api import handle
from Build.instruments.synthetic import ruler_observation, stopwatch_observation
from Build.reports import number_entry

from .fixture import synthetic_report

# template -> (samples, seed offset, position model of time t [m])
MODELS = {
    "free_fall": (8, 0, lambda t: 1 + 0.04 * t + 4.905 * t * t),
    "pendulum": (9, 100, lambda t: 1.0 * (1 - math.cos(0.3 * math.sin(math.sqrt(9.81) * t)))),  # bob drop, L = 1 m
    "projectile": (8, 200, lambda t: 2.0 + 1.5 * t + 4.905 * t * t),  # downward distance
    "ramp": (10, 300, lambda t: 0.1 * t + 0.5 * 9.81 * math.sin(0.3) * t * t),
}
# every reportable path in the closed contract list (indexed ones at a few indices)
PATHS = {"g": ("gravity.value", "gravity.uncertainty"), "n": ("fit.n", None), "rmse": ("fit.rmse", None), "rss": ("fit.rss", None),
         "dof": ("fit.dof", None), "rank": ("fit.rank", None), "var": ("covariance.variance", None),
         "se": ("covariance.standard_error", None), "floor": ("uncertainty.residual_variance_floor", None),
         "aic_a": ("model_selection.aic[0]", None), "aic_b": ("model_selection.aic[1]", None),
         "degree": ("model_selection.selected_degree", None), "fit_last": ("fit.fitted[3]", None), "res_last": ("fit.residuals[3]", None)}


def request(template):
    n, seed, model = MODELS[template]
    # t starts at 0.1 s: a stopwatch reading cannot be negative, so noise at t=0 would be refused for some seeds
    ts = [stopwatch_observation((i + 1) * 0.1, seed=seed + i, bias_s=0, noise_std_s=0.001, resolution_s=1e-3, uncertainty_s=1e-3) for i in range(n)]
    ps = [ruler_observation(model((i + 1) * 0.1), resolution_m=1e-3, uncertainty_m=1e-3, bias_m=0) for i in range(n)]
    return {"times": ts, "positions": ps, "degree": 2, "select_model": True}


def report(template):
    fitter = handle(request(template))
    assert fitter["status"] == "ok", fitter
    r = synthetic_report(fitter, template)
    r["numbers"] = {k: number_entry(fitter, p, u) for k, (p, u) in PATHS.items()}
    return r

