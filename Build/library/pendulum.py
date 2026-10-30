"""Index accepted synthetic pendulum records; do not run a simulation."""
import json
from pathlib import Path

from Build.library.example import safe_defaults
from Build.library.free_fall import simulated_demos
from Build.library.validate import ROOT, validate_file


def build(root=ROOT):
    root = Path(root)
    demos = simulated_demos(root, "pendulum")
    for demo in demos:
        demo["limitations"] += [
            "SYNTHETIC pendulum; Gate RS NOT_MET; S12f fallback VIRTUAL_LAB_ONLY.",
            "Real-scene prediction WITHHELD; acceptance summaries are not playable trajectories.",
        ]
    # The shortest accepted horizon limits the initial selection, not a new run.
    first = min(demos, key=lambda d: next(n["value"] for n in d["provenance"]["numeric"]
                                        if n["name"] == "duration_s"))
    manifest = {"schema_version": "1.0.0", "audience": "local-processing-only", "demos": demos,
                "defaults": safe_defaults(root, first, ("gravity_m_s2", "duration_s", "time_step_s"))}
    output = root / "test-data/library-artifacts/pendulum.json"
    output.write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    validate_file(output, evidence_root=root)
    return output


if __name__ == "__main__":
    print(build())
