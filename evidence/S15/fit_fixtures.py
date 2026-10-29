"""S15h: build/check tests/workspace/fixtures/fit-output.json = REAL Build/fitter.handle output on observations made by the REAL
Build/instruments models. Only the settings and true inputs below are SYNTHETIC fixture choices (non-physical a=2 m/s^2 stand-in
trace, as the S15f runner); not calibration, physics, Gate P/A, real-scene or physical evidence.
Usage (repo root): python evidence/S15/fit_fixtures.py [--check]"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from Build.fitter.api import handle  # noqa: E402
from Build.instruments import ruler_observation, stopwatch_observation  # noqa: E402

OUT = ROOT / "tests/workspace/fixtures/fit-output.json"
TRUE = [((i + 1) / 4, 0.5 * 2.0 * ((i + 1) / 4) ** 2) for i in range(8)]  # SYNTHETIC (time_s, position_m)


def build():
    times = [stopwatch_observation(t, seed=s, bias_s=0.0, noise_std_s=0.02, resolution_s=0.01, uncertainty_s=0.02)
             for s, (t, _) in enumerate(TRUE, start=1)]
    positions = [ruler_observation(x, resolution_m=0.01, uncertainty_m=0.005, bias_m=0.0) for _, x in TRUE]
    for q in times + positions:
        q.pop("error", None)  # signed error = distance to hidden truth; never a fitter input or display
    request = {"times": times, "positions": positions, "degree": 2, "select_model": True}
    return {"provenance": "SYNTHETIC settings and inputs; observations are Build/instruments output and 'output' is Build/fitter.handle "
                          "output. Not calibration, physics, Gate P/A, real-scene or physical evidence.",
            "request": request, "output": handle(request)}


if __name__ == "__main__":
    text = json.dumps(build(), indent=1, sort_keys=True) + "\n"
    if "--check" in sys.argv:
        sys.exit(0 if OUT.read_text(encoding="utf-8") == text else "fit fixture drifted: rerun without --check")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print("wrote", OUT.relative_to(ROOT))
