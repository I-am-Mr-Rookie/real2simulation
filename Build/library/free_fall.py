"""Index accepted free-fall outputs offline; no new simulation or measurements."""
import json
from pathlib import Path

from Build.library.example import build as build_example, ref, store
from Build.library.validate import ROOT, validate_file
from contracts.scene.validate_scene import load_json


ACCEPTANCE = "evidence/S10/acceptance/acceptance.json"
RUN = "S10hi-gate"
GATE = "evidence/S10/GATE-P.json"


def build(root=ROOT):
    root = Path(root)
    # Reuse the licensed descriptor builder and its current owner-grant checks.
    manifest = load_json(build_example(root))
    destination = root / "test-data/library-artifacts"
    artifact = store(destination, (root / ACCEPTANCE).read_bytes(), "simulation-record")
    acceptance = load_json(root / ACCEPTANCE)
    gate = load_json(root / GATE)
    if gate["physical_Gate_M"] != "NOT_MET_INPUT_READINESS":
        raise ValueError("review library limitations before changing physical Gate M")
    manifest["demos"][0]["title"] = "RM02 reconstruction display (NOT a measured free-fall demo)"
    manifest["demos"][0]["limitations"] += [
        "Free-fall source display only; this reconstruction is not a measured free-fall fit.",
        "Gate M: " + gate["physical_Gate_M"],
    ]
    for index, case in enumerate(acceptance["cases"]):
        if case["template"] != "free_fall":
            continue
        prefix = f"/cases/{index}"
        manifest["demos"].append({
            "id": "simulated-free-fall-" + case["case"],
            "title": "SIMULATED free fall: " + case["case"] + " (display-only)",
            "source": {
                "kind": "synthetic",
                "description": "Project-authored virtual-lab simulation; no external footage or clip-derived measurements.",
            },
            "artifact": artifact.copy(),
            "provenance": {
                "execution": "accepted-local-simulation", "run_id": RUN,
                "report": ref(root, f"Run-System/Runs/{RUN}/REPORT.md"),
                "artifact_evidence": ref(root, ACCEPTANCE),
                "record_pointer": prefix,
                "numeric": [
                    {"name": name, "value": case[name], "unit": unit,
                     "label": "simulated", "evidence": "artifact", "pointer": prefix + "/" + name}
                    for name, unit in (
                        ("gravity_m_s2", "m/s^2"), ("duration_s", "s"),
                        ("time_step_s", "s"), ("samples", "samples"),
                        ("position_error_m", "m"), ("relative_error", "1"),
                    )
                ],
            },
            "label": "simulated", "scale_verified": False, "scale_label": "SCALE_UNVERIFIED",
            "gates": {"M": "NOT_MET", "RS": "NOT_MET", "R": "NOT_RUN"},
            "availability": "metadata-only",
            "limitations": [
                "SIMULATED virtual-lab output; not measured from RM02 or any real clip.",
                "Gate M: " + gate["physical_Gate_M"],
                "SCALE_UNVERIFIED; simulated units do not calibrate any real footage.",
                "Pre-contact analytic motion only; no rebound or contact-response claim.",
                "Stored acceptance metrics and replay hashes only; no trajectory or playable assets bundled.",
                "Local processing only; no public raw-media redistribution or gate promotion.",
            ],
        })
    output = destination / "free-fall.json"
    output.write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    validate_file(output, evidence_root=root)
    return output


if __name__ == "__main__":
    print(build())
