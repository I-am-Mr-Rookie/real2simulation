"""Reproduce the frozen R14 analytic counterexample; standard library only."""
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests" / "fitter"))
from test_r14_model_selection import TIMES, observations, request, expected_aic, expected_rss
from Build.fitter.api import handle
from Build.fitter.core import select_model


def score_json(score):
    return score if math.isfinite(score) else str(score)


cases = []
for curvature, exponent in ((1, 0), (4, 0), (4, -600), (4, -540)):
    scale = math.ldexp(1., exponent)
    positions = observations(curvature, scale)
    expected = [expected_aic(curvature, degree, scale) for degree in (1, 2)]
    actual = None
    error = None
    try:
        selected = select_model(TIMES, positions)
        actual = {"degree": selected.selected_degree,
                  "aic": list(map(score_json, selected.aic)),
                  "rss": [fit.rss for fit in selected.candidates],
                  "rmse": [fit.rmse for fit in selected.candidates],
                  "residuals": [fit.residuals for fit in selected.candidates]}
    except (ValueError, OverflowError) as exc:
        error = {"type": type(exc).__name__, "message": str(exc)}
    exact_rss = [Fraction(expected_rss(curvature, d)) * Fraction(scale)**2 for d in (1, 2)]
    cases.append({"curvature": curvature, "scale_exponent": exponent,
                  "times": TIMES, "positions": positions,
                  "expected": {"selected_degree": (1, 2)[expected[1] < expected[0]],
                               "aic": expected, "exact_rss": list(map(str, exact_rss)),
                               "rmse": [scale * math.sqrt(expected_rss(curvature, d) / 5) for d in (1, 2)]},
                  "actual": actual, "error": error,
                  "api": handle(request(TIMES, positions, select_model=True))})

times = tuple(1+i/10 for i in range(6))
positions = tuple(1+2*t for t in times)
selected = select_model(times, positions)
linear_hazard = {"times": times, "positions": positions,
                 "exact_fraction_linear_relation": all(Fraction(y) == 1+2*Fraction(t) for t, y in zip(times, positions)),
                 "selected_degree": selected.selected_degree, "aic": selected.aic,
                 "rss": [fit.rss for fit in selected.candidates],
                 "classification": "precision hazard; no specified exact-fit tie/precision policy"}
files = ("Build/fitter/api.py", "Build/fitter/core.py", "contracts/fit/quantity.py",
         "tests/fitter/test_r14_model_selection.py")
result = {"python": platform.python_version(), "simulation_only": True,
          "source_sha256": {file: hashlib.sha256((ROOT/file).read_bytes()).hexdigest() for file in files},
          "cases": cases, "additional_precision_hazard": linear_hazard}
print(json.dumps(result, indent=2, allow_nan=False))
