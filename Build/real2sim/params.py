"""S12b parameter transfer: fitted values -> existing simulator, provenance kept.

Gate M is NOT_MET: 'g' is an image-height/s^2 fitted acceleration, never m/s^2.
Missing or abstained parameters are refused, never defaulted.
"""
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

from Build.fitter import jacobian_covariance
from Build.real2sim.boundary import GATE_M, LIMITS, _sha, fit_prefix

ROOT = Path(__file__).resolve().parents[2]
# Scale-free units only; a metric unit needs a calibrated source (Gate M MET), which does not exist.
UNITS = {"g": "image-height/s^2", "speed": "image-height/s",
         "friction": "dimensionless", "restitution": "dimensionless"}
PROVENANCE = ("input_provenance", "method", "source_sha256")


def parameter(name, value, uncertainty, provenance):
    """Validated record: value, unit, 1-sigma uncertainty, provenance, gate_m."""
    if name not in UNITS:
        raise ValueError(f"unknown parameter {name!r}")
    for label, v in (("value", value), ("uncertainty", uncertainty)):
        if type(v) not in (int, float) or not math.isfinite(v):
            raise ValueError(f"{name}: finite {label} required (no default)")
    if uncertainty < 0:
        raise ValueError(f"{name}: uncertainty must be non-negative")
    if not isinstance(provenance, dict) or any(
            not isinstance(provenance.get(k), str) or not provenance[k] for k in PROVENANCE):
        raise ValueError(f"{name}: provenance needs {PROVENANCE}")
    return {"name": name, "value": float(value), "unit": UNITS[name],
            "uncertainty": float(uncertainty), "uncertainty_kind": "1-sigma standard",
            "provenance": dict(provenance), "gate_m": GATE_M}


def abstain(name, reason):
    return {"name": name, "abstained": reason, "gate_m": GATE_M}


def from_fit(boundary, input_provenance):
    """g and speed from the S12a prefix fit; abstain unless AIC selects quadratic."""
    selection = fit_prefix(boundary)
    if selection.selected_degree != 2:
        reason = f"AIC selected degree {selection.selected_degree}; no acceleration measured"
        return [abstain("g", reason), abstain("speed", reason)]
    fit = next(c for c in selection.candidates if c.degree == 2)
    base = {"input_provenance": input_provenance, "source_sha256": boundary.source_sha256,
            "clip_id": boundary.clip_id, "boundary_training_sha256": boundary.training_sha256,
            "boundary_suffix_identity_sha256": boundary.suffix_identity_sha256,
            "fit_sha256": _sha([fit.degree, list(fit.coefficients), list(fit.residuals)]),
            "time_origin": "first training PTS"}
    out = []
    # y is image-down: g = 2*c2 (downward), speed = c1 (downward velocity at time origin).
    for name, index, factor in (("g", 2, 2.0), ("speed", 1, 1.0)):
        cov = jacobian_covariance(fit, parameter_index=index)
        if not cov.valid:
            out.append(abstain(name, "fit covariance unavailable"))
            continue
        out.append(parameter(name, factor * fit.coefficients[index], factor * cov.standard_error,
                             base | {"method": f"S12a prefix quadratic fit, coefficient {index}"}))
    return out


def transfer(records):
    """Exactly one valid record per parameter; anything missing/abstained is refused."""
    by_name = {}
    for r in records:
        if r.get("name") in by_name:
            raise ValueError(f"duplicate parameter {r.get('name')!r}")
        by_name[r.get("name")] = r
    refused = [n for n in UNITS if n not in by_name or "abstained" in by_name[n]]
    if refused:
        raise ValueError(f"refused (missing/abstained, no default): {refused}")
    if set(by_name) - set(UNITS):
        raise ValueError(f"unknown parameters {sorted(set(by_name) - set(UNITS))}")
    return {n: parameter(n, by_name[n]["value"], by_name[n]["uncertainty"], by_name[n]["provenance"])
            for n in UNITS}


_RUN = ("const {runContactAwareTrajectory} = await import(process.argv[1]);"
        "const {readFileSync} = await import('node:fs');"
        "const r = await runContactAwareTrajectory(JSON.parse(readFileSync(0,'utf8')));"
        "process.stdout.write(JSON.stringify(r));")


def simulate(records, setup):
    """Run the existing RK4 + Rapier contact simulator on transferred values.

    setup: explicit initial_height, dt, steps, floorY, floorHalfExtents, sphereRadius, density.
    """
    params = transfer(records)
    kinds = {p["provenance"]["input_provenance"] for p in params.values()}
    # shortcut: simulator contract only labels inputProvenance 'synthetic'; real params need a Build/simulator label first.
    if kinds != {"synthetic"}:
        raise ValueError(f"simulator accepts only synthetic-provenance inputs, got {sorted(kinds)}")
    need = ("initial_height", "dt", "steps", "floorY", "floorHalfExtents", "sphereRadius", "density")
    if set(setup) != set(need):
        raise ValueError(f"setup needs exactly {need}")
    value = {n: p["value"] for n, p in params.items()}
    sim_input = {"template": "free_fall", "kind": "free-fall", "source": "simulated",
                 "inputProvenance": "synthetic", "gravity": value["g"],
                 "initialPosition": [0, setup["initial_height"], 0],
                 "initialVelocity": [0, -value["speed"], 0],  # image-down speed -> simulator y-up
                 "dt": setup["dt"], "steps": setup["steps"],
                 "geometry": {k: setup[k] for k in ("floorY", "floorHalfExtents", "sphereRadius")},
                 "physics": {"friction": value["friction"], "restitution": value["restitution"],
                             "density": setup["density"]}}
    runner = (ROOT / "Build/simulator/contact-runs.mjs").as_uri()
    proc = subprocess.run(["node", "--input-type=module", "-e", _RUN, runner],
                          input=json.dumps(sim_input, allow_nan=False), capture_output=True,
                          text=True, encoding="utf-8", timeout=60, cwd=ROOT)
    if proc.returncode:
        lines = proc.stderr.strip().splitlines() or ["no stderr"]
        raise ValueError("simulator rejected transfer: " + next((l for l in lines if "Error: INVALID_" in l), lines[-1]))
    return {"parameters": params, "parameter_set_sha256": _sha(params),
            "simulator_input": sim_input, "simulation": json.loads(proc.stdout),
            "gate_m": GATE_M, "units": "image-height fraction (scale-free); simulator *_m fields are image heights",
            "limitations": list(LIMITS) + ["uncertainty carried, not propagated through the simulation"]}


def main(root=ROOT):
    """Real ST03: S12a withheld the prefix fit, so every parameter abstains (no transfer)."""
    rel = "evidence/S12/boundary-ST03.json"
    raw = (root / rel).read_bytes()
    record = json.loads(raw)
    fit_reason = (None if record.get("fit_run") else
                  "S12a withheld ST03 prefix fit (S07 frame_map PTS conflict, frame 77 quarantined)")
    if fit_reason is None:
        raise SystemExit("ST03 boundary now allows a fit; rerun from_fit on the verified prefix")
    records = [abstain("g", fit_reason), abstain("speed", fit_reason),
               abstain("friction", "no bounce/slide observation measured for ST03"),
               abstain("restitution", "no bounce observation measured for ST03")]
    try:
        transfer(records)
        refusal = None
    except ValueError as error:
        refusal = str(error)
    out = {"clip_id": "ST03", "boundary_source": {"path": rel, "sha256": hashlib.sha256(raw).hexdigest()},
           "parameters": records, "transfer_refused": refusal, "simulated": False,
           "gate_m": GATE_M, "limitations": list(LIMITS)}
    path = root / "evidence/S12/params-ST03.json"
    path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"{rel} -> evidence/S12/params-ST03.json gate_m={GATE_M} refused={refusal is not None}")


if __name__ == "__main__":
    sys.exit(main())
