"""Visibly synthetic fixture: fitter output from seeded simulated instruments (no real-scene/physical evidence)."""
import json
import sys
from pathlib import Path

from Build.fitter.api import handle
from Build.instruments.synthetic import ruler_observation, stopwatch_observation
from Build.reports import SCHEMA, digest, number_entry

REF = {"g": ("gravity.value", "gravity.uncertainty"), "rmse": ("fit.rmse", None), "n": ("fit.n", None)}


def synthetic_fitter_result():
    ts = [stopwatch_observation(i * 0.1, seed=i, bias_s=0, noise_std_s=0.001, resolution_s=1e-3, uncertainty_s=1e-3)
          for i in range(8)]
    ps = [ruler_observation(1 + 0.04 * i + 4.905 * (i * 0.1) ** 2, resolution_m=1e-3, uncertainty_m=1e-3, bias_m=0)
          for i in range(8)]
    out = handle({"times": ts, "positions": ps, "degree": 2, "select_model": True})
    assert out["status"] == "ok", out
    return out


def synthetic_report(fitter=None, template="free_fall"):
    fitter = fitter or synthetic_fitter_result()
    return {
        "schema": SCHEMA, "template": template, "fitter_digest": digest(fitter),
        "title": "Synthetic fixture report",
        "sections": [{"id": "results", "title": "Results", "text": [
            "Fitted g is {{g}} from {{n}} samples; residual RMS is {{rmse}}.",
            "This is a simulated fixture, not a physical measurement."]}],
        "numbers": {k: number_entry(fitter, v, u) for k, (v, u) in REF.items()},
    }


if __name__ == "__main__":  # python -m tests.reports.fixture <evidence dir>
    f = synthetic_fitter_result()
    d = Path(sys.argv[1])
    (d / "synthetic_fitter_result.json").write_text(json.dumps(f, indent=1, sort_keys=True))
    (d / "synthetic_report.json").write_text(json.dumps(synthetic_report(f), indent=1, sort_keys=True))
