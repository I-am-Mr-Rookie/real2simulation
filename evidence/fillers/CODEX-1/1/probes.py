"""Offline review probes, NOT product tests, measurements, simulation or gate evidence.

Run from event root: python -B evidence/fillers/CODEX-1/1/probes.py
No writes; imports only finished CODEX-1-owned helpers/modules and synthetic fixture.
Exit 0 means review observations reproduced, not that the reviewed behavior is good.
"""
import copy
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT), str(ROOT / "tests/spec")]
from test_setup_validation import setup, BUNDLE
from test_experiment_validation import validator
from Build.templates.free_fall import analytic_free_fall
from Build.templates.projectile import analytic_projectile
from Build.templates.ramp import analytic_ramp
from Build.templates.pendulum import analytic_pendulum

records = []

def record(id, **values):
    records.append(dict(id=id, **values))

# P1: same invalid time has a different error class for free fall.
for kind, api in [("free_fall", analytic_free_fall), ("projectile", analytic_projectile),
                  ("ramp", analytic_ramp), ("pendulum", analytic_pendulum)]:
    spec, scene = setup(kind)
    try:
        api(spec, scene, BUNDLE, times=[10**1000])
    except Exception as error:
        record("P1-" + kind, exception=type(error).__name__, message=str(error))
    else:
        raise AssertionError("Invalid huge sample time was accepted")

# P2: endpoint displacement can disappear at world-coordinate precision.
spec, scene = setup()
spec["parameters"]["drop_height"]["value"] = 1e-20
validator.validate_setup(spec, scene, BUNDLE)
result = analytic_free_fall(spec, scene, BUNDLE)
t = result["impact_time"]["value"]
sampled = analytic_free_fall(spec, scene, BUNDLE, times=[0, t])
record("P2", setup_accepted=True, requested_height=1e-20,
       impact_time=t, origin=spec["placement"]["origin"]["value"],
       impact=result["impact_position"]["value"],
       sample_positions=[s["position"]["value"] for s in sampled["samples"]])

# P3: documented general setup versus oracle-domain split.
for kind, api, field, value in [("ramp", analytic_ramp, "friction_coefficient", 10),
                                 ("pendulum", analytic_pendulum, "release_angle", .2)]:
    spec, scene = setup(kind)
    spec["parameters"][field]["value"] = value
    spec["simulation"]["time_step"]["value"] = .0001
    validator.validate_setup(spec, scene, BUNDLE)
    try:
        api(spec, scene, BUNDLE)
    except ValueError as error:
        record("P3-" + kind, setup_accepted=True, exception=type(error).__name__, message=str(error))
    else:
        raise AssertionError("Expected documented oracle domain rejection")

# P4: result evidence has no input-content/version binding beyond method + id.
a, scene = setup()
b = copy.deepcopy(a)
b["parameters"]["drop_height"]["value"] = .5
ra = analytic_free_fall(a, scene, BUNDLE)
rb = analytic_free_fall(b, scene, BUNDLE)
record("P4", same_experiment_id=a["experiment_id"] == b["experiment_id"],
       same_evidence=ra["impact_time"]["source"]["evidence"] == rb["impact_time"]["source"]["evidence"],
       different_impact_times=ra["impact_time"]["value"] != rb["impact_time"]["value"],
       evidence=ra["impact_time"]["source"]["evidence"])

assert records[0]["exception"] == "OverflowError"
assert all(r["exception"] == "ValueError" for r in records[1:4])
assert records[4]["impact"] == records[4]["origin"]
assert records[-1]["same_evidence"] and records[-1]["different_impact_times"]
sources = ["contracts/experiment/validate_experiment.py", "contracts/experiment/experiment.schema.json",
           "contracts/scene/validate_scene.py", "contracts/scene/scene.schema.json",
           *[f"Build/templates/{name}.py" for name in ("free_fall", "projectile", "ramp", "pendulum")]]
print(json.dumps({"scope": "synthetic review observations only; not physics/simulator/gate evidence",
                  "records": records,
                  "source_sha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in sources}}, indent=2))
