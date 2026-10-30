"""Index accepted projectile outputs offline; bounce has no accepted source."""
import json
from pathlib import Path

from Build.library.free_fall import simulated_demos
from Build.library.validate import ROOT, validate_file


def build(root=ROOT):
    root = Path(root)
    manifest = {"schema_version": "1.0.0", "audience": "local-processing-only",
                "demos": simulated_demos(root, "projectile")}
    output = root / "test-data/library-artifacts/projectile.json"
    output.write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    validate_file(output, evidence_root=root)
    return output


if __name__ == "__main__":
    print(build())
