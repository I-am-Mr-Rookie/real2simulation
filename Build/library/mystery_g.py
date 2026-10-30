"""Prepare answer-free challenge metadata from accepted records; no simulation."""
import json
from pathlib import Path

from Build.library.example import safe_defaults, store
from Build.library.free_fall import ACCEPTANCE, simulated_demos
from Build.library.validate import (CHALLENGE_LIMITATION, CHALLENGE_TITLE, ROOT, challenge_payload,
                                    pointer, validate_file)
from contracts.scene.validate_scene import load_json


def build(root=ROOT):
    root = Path(root)
    demo = simulated_demos(root, "free_fall")[0]
    record = pointer(load_json(root / ACCEPTANCE), demo["provenance"]["record_pointer"])
    payload = json.dumps(challenge_payload(record), indent=2, allow_nan=False) + "\n"
    demo["artifact"] = store(root / "test-data/library-artifacts", payload.encode("utf-8"), "challenge-record")
    demo["id"] = "simulated-mystery-g"
    demo["title"] = CHALLENGE_TITLE
    demo["challenge"] = {"mode": "mystery-g", "answer_visibility": "withheld-until-fit", "target": "/lab"}
    demo["provenance"]["numeric"] = [
        {"name": name, "value": record[name], "unit": "s", "label": "simulated",
         "evidence": "artifact", "pointer": "/" + name}
        for name in ("duration_s", "time_step_s")]
    demo["limitations"] = [line for line in demo["limitations"]
                           if not line.startswith("Stored acceptance metrics")]
    demo["limitations"] += [
        "Challenge setup projection only; no new Mystery-g session or replay was executed.",
        CHALLENGE_LIMITATION,
        "The blind challenge is /lab Mystery-g: the server draws a hidden g per session and reveals it only after its server-owned fit.",
        "Offline provenance references are audit-only, not guest artifact endpoints.",
        "Gate RS NOT_MET; S12f VIRTUAL_LAB_ONLY; real-scene prediction WITHHELD.",
    ]
    manifest = {"schema_version": "1.0.0", "audience": "local-processing-only", "demos": [demo],
                "defaults": safe_defaults(root, demo)}
    output = root / "test-data/library-artifacts/mystery-g.json"
    output.write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    validate_file(output, evidence_root=root)
    return output


if __name__ == "__main__":
    print(build())
