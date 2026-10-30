"""Derive the local S06d descriptor example from accepted evidence, without new numbers."""
import csv
import hashlib
import json
from pathlib import Path

from Build.library.validate import ROOT, validate_file


def ref(root, path):
    return {"path": path, "sha256": hashlib.sha256((root / path).read_bytes()).hexdigest()}


def store(destination, payload, kind):
    """Reuse exact evidence bytes; never overwrite a content-addressed object."""
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
    return {"kind": kind, "media_type": "application/json", "path": artifact_path,
            "sha256": sha, "bytes": len(payload)}


def safe_defaults(root, demo, parameters=()):
    """Select metadata only; parameter values keep their original evidence pointers."""
    return {"demo_id": demo["id"], "autoplay": False, "physics_enabled": False,
            "real_scene_prediction": "WITHHELD",
            "parameters": [n.copy() for n in demo["provenance"]["numeric"] if n["name"] in parameters],
            "fallback_evidence": ref(root, "evidence/S12/S12f-fallback.json")}


def descriptor_demo(root, clip_id, original, ledger_ref, metric="function_elapsed_s"):
    """Reuse one successful accepted scene job, not its failed preflight attempts."""
    root = Path(root)
    destination = root / "test-data/library-artifacts"
    ledger = json.loads((root / ledger_ref).read_text(encoding="utf-8"))
    jobs = [(i, job) for i, job in enumerate(ledger["jobs"]) if job.get("rc") == 0]
    if len(jobs) != 1:
        raise ValueError("expected one successful accepted scene job")
    job_index, job = jobs[0]
    artifact = store(destination, (root / original).read_bytes(), "scene-descriptor")
    with (root / "clips.csv").open(encoding="utf-8", newline="") as stream:
        row = next(r for r in csv.DictReader(stream) if r["clip_id"] == clip_id)
    registry = json.loads((root / "evidence/clips/S02c-acquisition.json").read_text(encoding="utf-8"))
    source_sha = next(f["sha256"] for f in registry["files"] if f["clip_id"] == clip_id)
    return {
        "id": clip_id.lower() + "-" + ledger["run"].split("-")[0].lower() + "-descriptor",
        "title": clip_id + " measured reconstruction descriptor (not calibrated)",
        "source": {"clip_id": clip_id, "sha256": source_sha,
                   **{k: row[k] for k in ("source_url", "licence", "licence_url", "attribution")}},
        "artifact": artifact,
        "provenance": {"run_id": ledger["run"], "report": ref(root, f"Run-System/Runs/{ledger['run']}/REPORT.md"),
                       "ledger": ref(root, ledger_ref), "app_id": job["app_id"],
                       "artifact_evidence": ref(root, original),
                       "numeric": [{"name": metric, "value": job[metric],
                                    "unit": "s", "label": "measured", "evidence": "ledger",
                                    "pointer": f"/jobs/{job_index}/{metric}"}]},
        "label": "measured", "scale_verified": False, "scale_label": "SCALE_UNVERIFIED",
        "gates": {"M": "NOT_MET", "RS": "NOT_MET", "R": "NOT_MET"}, "availability": "metadata-only",
        "limitations": ["Measured means reconstruction/job output, not calibrated physical measurements.",
                        "PLY assets are absent; this descriptor alone is not a playable demo.",
                        "Local processing approval only; no public raw-media redistribution approval.",
                        "Nominal model scale; gravity unknown; physics disabled."]
    }


def build(root=ROOT):
    root = Path(root)
    destination = root / "test-data/library-artifacts"
    manifest = {"schema_version": "1.0.0", "audience": "local-processing-only", "demos": [
        descriptor_demo(root, "RM02", "evidence/S06/S06d/scene-RM02-gpu.json",
                        "evidence/S06/S06d/job-ledger.json")
    ]}
    output = destination / "manifest.json"
    output.write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    validate_file(output, evidence_root=root)
    return output


if __name__ == "__main__":
    print(build())
