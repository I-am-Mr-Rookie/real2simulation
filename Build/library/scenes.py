"""Index accepted MapAnything descriptors, with no assets or physics claims."""
import json
from pathlib import Path

from Build.library.example import descriptor_demo, safe_defaults
from Build.library.validate import ROOT, validate_file


def build(root=ROOT):
    root = Path(root)
    demos = [
        descriptor_demo(root, "RM02", "evidence/S06/S06d/scene-RM02-gpu.json",
                        "evidence/S06/S06d/job-ledger.json"),
        descriptor_demo(root, "RM04", "evidence/S06/S06f/scene-RM04-gpu.json",
                        "evidence/S06/S06f/job-ledger.json", "whole_command_wall_s"),
    ]
    for demo in demos:
        demo["title"] = demo["source"]["clip_id"] + " MapAnything scene (display-only, SCALE_UNVERIFIED)"
        demo["limitations"] += [
            "Display-only descriptor; no physical fit, calibrated dimensions or real-scene prediction.",
            "S12f fallback VIRTUAL_LAB_ONLY; real-scene prediction WITHHELD.",
        ]
    manifest = {"schema_version": "1.0.0", "audience": "local-processing-only", "demos": demos,
                "defaults": safe_defaults(root, demos[0])}
    output = root / "test-data/library-artifacts/scenes.json"
    output.write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    validate_file(output, evidence_root=root)
    return output


if __name__ == "__main__":
    print(build())
