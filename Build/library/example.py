"""Derive the local S06d descriptor example from accepted evidence, without new numbers."""
import csv
import hashlib
import json
from pathlib import Path

from Build.library.validate import ROOT, validate_file


def ref(root, path):
    return {"path": path, "sha256": hashlib.sha256((root / path).read_bytes()).hexdigest()}


def build(root=ROOT):
    root = Path(root)
    destination = root / "test-data/library-artifacts"
    original = "evidence/S06/S06d/scene-RM02-gpu.json"
    ledger_ref = "evidence/S06/S06d/job-ledger.json"
    ledger = json.loads((root / ledger_ref).read_text(encoding="utf-8"))
    payload = (root / original).read_bytes()
    sha = hashlib.sha256(payload).hexdigest()
    artifact_path = f"objects/sha256/{sha}.json"
    path = destination / artifact_path
    path.parent.mkdir(parents=True, exist_ok=True)
    # Create-once; never silently replace a content-addressed object.
    if path.exists():
        if path.read_bytes() != payload:
            raise ValueError("existing immutable artifact is corrupt")
    else:
        with path.open("xb") as stream:
            stream.write(payload)
    with (root / "clips.csv").open(encoding="utf-8", newline="") as stream:
        row = next(r for r in csv.DictReader(stream) if r["clip_id"] == "RM02")
    registry = json.loads((root / "evidence/clips/S02c-acquisition.json").read_text(encoding="utf-8"))
    source_sha = next(f["sha256"] for f in registry["files"] if f["clip_id"] == "RM02")
    manifest = {"schema_version": "1.0.0", "audience": "local-processing-only", "demos": [{
        "id": "rm02-s06d-descriptor", "title": "RM02 measured reconstruction descriptor (not calibrated)",
        "source": {"clip_id": "RM02", "sha256": source_sha,
                   **{k: row[k] for k in ("source_url", "licence", "licence_url", "attribution")}},
        "artifact": {"kind": "scene-descriptor", "media_type": "application/json",
                     "path": artifact_path, "sha256": sha, "bytes": len(payload)},
        "provenance": {"run_id": ledger["run"], "report": ref(root, f"Run-System/Runs/{ledger['run']}/REPORT.md"),
                       "ledger": ref(root, ledger_ref), "app_id": ledger["jobs"][0]["app_id"],
                       "artifact_evidence": ref(root, original),
                       "numeric": [{"name": "function_elapsed_s", "value": ledger["jobs"][0]["function_elapsed_s"],
                                    "unit": "s", "label": "measured", "evidence": "ledger", "pointer": "/jobs/0/function_elapsed_s"}]},
        "label": "measured", "scale_verified": False, "scale_label": "SCALE_UNVERIFIED",
        "gates": {"M": "NOT_MET", "RS": "NOT_MET", "R": "NOT_MET"}, "availability": "metadata-only",
        "limitations": ["Measured means reconstruction/job output, not calibrated physical measurements.",
                        "PLY assets are absent; this descriptor alone is not a playable demo.",
                        "Local processing approval only; no public raw-media redistribution approval.",
                        "Nominal model scale; gravity unknown; physics disabled."]
    }]}
    output = destination / "manifest.json"
    output.write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    validate_file(output, evidence_root=root)
    return output


if __name__ == "__main__":
    print(build())
