"""S15g: build/check tests/workspace/fixtures/instrument-readings.json from the REAL Build/instruments synthetic models.
Every number in the file is instrument output (the instruments quantize, bias and label it). Only the instrument SETTINGS and the
true inputs below are SYNTHETIC fixture choices (non-physical stand-in trace a=2 m/s^2, same as the S15f fixture runner); they are
not calibration, physics or gate evidence. Usage (repo root): python evidence/S15/instrument_fixtures.py [--check]"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from Build.instruments import camera_observation, light_gate_observation, ruler_observation, stopwatch_observation  # noqa: E402

OUT = ROOT / "tests/workspace/fixtures/instrument-readings.json"
TRIALS = [(2.0, 4.0), (1.5, 2.25), (1.0, 1.0)]  # SYNTHETIC (time_s, position_m) stand-ins


def build():
    sw = [stopwatch_observation(t, seed=seed, bias_s=0.01, noise_std_s=0.05, resolution_s=0.01, uncertainty_s=0.05)
          for seed, (t, _) in enumerate(TRIALS, start=1)]
    ruler = [ruler_observation(x, resolution_m=0.001, uncertainty_m=0.0005, bias_m=0.0003) for _, x in TRIALS]
    gate = [light_gate_observation(t, resolution_s=0.001, uncertainty_s=0.0005, bias_s=0.0002) for t, _ in TRIALS]
    cam = [camera_observation(i, t, 0.0, x * 100, time_resolution_s=1 / 30, pixel_resolution_px=1, time_uncertainty_s=1 / 60,
                              pixel_uncertainty_px=0.5, time_bias_s=0.001, pixel_bias_px=0.2) for i, (t, x) in enumerate(TRIALS)]
    return {"provenance": "SYNTHETIC settings and inputs; every value is Build/instruments output. Not calibration, physics, "
                          "Gate P/A, real-scene or physical evidence.",
            "readings": {"stopwatch": sw, "ruler": ruler, "light_gate": gate, "camera": cam}}


if __name__ == "__main__":
    text = json.dumps(build(), indent=1, sort_keys=True) + "\n"
    if "--check" in sys.argv:
        sys.exit(0 if OUT.read_text(encoding="utf-8") == text else "instrument fixtures drifted: rerun without --check")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print("wrote", OUT.relative_to(ROOT))
