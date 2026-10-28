"""Fixed-action, bounded local bridge for the S10 synthetic lab service."""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
MAX_SAMPLES = 2_000
INSTRUMENTS = {
    "time_resolution_s": 1e-6, "time_uncertainty_s": 1e-6, "time_bias_s": 0.0,
    "distance_resolution_m": 1e-6, "distance_uncertainty_m": 1e-6, "distance_bias_m": 0.0,
}


def error(code: str) -> dict:
    return {"status": "error", "error": {"code": code}}


def _finite(value: object) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


def _start(template: str) -> dict:
    if template not in {"free_fall", "projectile", "ramp", "pendulum"}:
        return error("unsupported_template")
    from Build.lab.regression import regression_case
    from Build.simulator.export_validated_setup import export
    with tempfile.TemporaryDirectory(prefix="s10-lab-") as tmp:
        folder = Path(tmp)
        spec_path, scene_path, _ = regression_case(folder, template)
        artifact = export(spec_path, scene_path)
        encoded = json.dumps(artifact, allow_nan=False)
        process = subprocess.run(
            ["node", str(ROOT / "Build/lab/simulate.mjs")], input=encoded,
            text=True, capture_output=True, encoding="utf-8", cwd=ROOT,
            timeout=20, env={"PATH": os.environ.get("PATH", ""), "SystemRoot": os.environ.get("SystemRoot", ""),
                             "PYTHONPATH": os.environ.get("PYTHONPATH", ""), "PYTHONIOENCODING": "utf-8"},
        )
        if process.returncode or not process.stdout:
            return error("synthetic_simulator_failed")
        trajectory = json.loads(process.stdout)
        samples = trajectory.get("samples")
        if not isinstance(samples, list) or not samples or len(samples) > MAX_SAMPLES:
            return error("invalid_trajectory")
        origin_y = samples[0]["position_m"][1]
        observations = []
        for sample in samples:
            time_s = sample.get("time_s")
            position_m = origin_y - sample["position_m"][1]
            if not _finite(time_s) or not _finite(position_m):
                return error("invalid_observation")
            observations.append({"time_s": time_s, "position_m": position_m})
        result = {
            "status": "ok", "template": template,
            "observations": observations, "source": "simulated",
            "units": {"time": "s", "position": "m"},
            "limitations": ["synthetic authored instrument settings", "uncertainty model does not propagate input instrument uncertainty"],
        }
        if template in {"free_fall", "projectile"}:
            result["gravity"] = {"value": 9.81, "unit": "m/s^2", "source": "synthetic authored setup"}
        return result


def _fit(observations: object) -> dict:
    if not isinstance(observations, list) or not observations or len(observations) > MAX_SAMPLES:
        return error("invalid_observations")
    times, positions = [], []
    for sample in observations:
        if not isinstance(sample, dict) or set(sample) != {"time_s", "position_m"}:
            return error("invalid_observation_shape")
        if not _finite(sample["time_s"]) or not _finite(sample["position_m"]):
            return error("nonfinite_observation")
        times.append({"value": sample["time_s"], "unit": "s", "uncertainty": 1e-6, "source": {"label": "simulated", "evidence": "S10 synthetic lab instrument"}})
        positions.append({"value": sample["position_m"], "unit": "m", "uncertainty": 1e-6, "source": {"label": "simulated", "evidence": "S10 synthetic lab instrument"}})
    from Build.fitter.api import handle
    return handle({"times": times, "positions": positions, "degree": 2, "select_model": True,
                   "uncertainty_model": "iid_fixed_clock_scale"})


def handle(request: object) -> dict:
    try:
        action = request.get("action") if isinstance(request, dict) else None
        if action == "start":
            template = request.get("template")
            if type(template) is not str or set(request) - {"action", "template"}:
                return error("invalid_start_request")
            return _start(template)
        if action == "fit":
            if set(request) - {"action", "observations"} or "observations" not in request:
                return error("invalid_fit_request")
            return _fit(request["observations"])
        return error("unsupported_action")
    except (TimeoutError, subprocess.SubprocessError, ValueError, TypeError, KeyError, json.JSONDecodeError):
        return error("lab_bridge_failed")


def main() -> None:
    try:
        raw = sys.stdin.read(1_000_001)
        if len(raw) > 1_000_000:
            response = error("request_too_large")
        else:
            response = handle(json.loads(raw))
    except Exception:
        response = error("invalid_json")
    sys.stdout.write(json.dumps(response, allow_nan=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
