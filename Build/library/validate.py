"""Offline local library custody checks; no routes, downloads, or gate promotion."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

from jsonschema import Draft202012Validator
from contracts.scene.validate_scene import load_json
from Build.real2sim.score import APPROVAL, REGISTRY, LICENCES, approved

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = Path(__file__).with_name("manifest.schema.json")
MANIFEST_BYTES = 256 * 1024  # same as viewer artifact-loader.mjs
ARTIFACT_BYTES = 64 * 1024 * 1024


def require(ok, message):
    if not ok:
        raise ValueError(message)


def file_under(root, relative):
    root = Path(root).resolve()
    require(isinstance(relative, str) and "\\" not in relative and
            ":" not in relative and not relative.startswith("/") and
            all(p not in ("", ".", "..") for p in relative.split("/")), "unsafe path")
    path = (root / relative).resolve()
    require(path.is_relative_to(root) and path.is_file(), "missing or escaped file")
    return path


def bounded(path, limit):
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    require(len(data) <= limit, "file exceeds byte limit")
    return data


def checked_ref(ref, root, limit=ARTIFACT_BYTES):
    path = file_under(root, ref["path"])
    data = bounded(path, limit)
    require(hashlib.sha256(data).hexdigest() == ref["sha256"], "evidence sha256 mismatch")
    return path, data


def pointer(document, value):
    """Resolve an RFC6901 JSON pointer; schema requires a non-root pointer."""
    for token in value[1:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        if isinstance(document, list):
            require(token.isdecimal() and (token == "0" or not token.startswith("0")), "bad array pointer")
            document = document[int(token)]
        else:
            document = document[token]
    return document


def validate(manifest, artifact_root, evidence_root=ROOT):
    """Validate structure + current owner grant + bytes + run/ledger/numeric custody.

    Local processing approval is NOT public redistribution approval. v1 deliberately
    cannot express calibrated scale or passing gates until a reviewed successor.
    """
    require(len(json.dumps(manifest, ensure_ascii=False, allow_nan=False).encode("utf-8")) <= MANIFEST_BYTES,
            "manifest exceeds byte limit")
    schema = load_json(SCHEMA)
    Draft202012Validator.check_schema(schema)
    errors = list(Draft202012Validator(schema).iter_errors(manifest))
    require(not errors, "; ".join(f"{list(e.path)}: {e.message}" for e in errors))
    root = Path(evidence_root)
    with (root / "clips.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    approval = (root / APPROVAL).read_text(encoding="utf-8")
    registry = load_json(root / REGISTRY)
    ids = set()
    for demo in manifest["demos"]:
        require(demo["id"] not in ids, "duplicate demo id")
        ids.add(demo["id"])
        source = demo["source"]
        if source.get("kind") == "synthetic":
            validate_local_simulation(demo, artifact_root, root)
            continue
        require("ledger" in demo["provenance"] and "app_id" in demo["provenance"],
                "clip source requires job provenance")
        matches = [r for r in rows if r["clip_id"] == source["clip_id"]]
        require(len(matches) == 1 and approved(source["clip_id"], approval), "clip not approved")
        row = matches[0]
        require(row["licence"].strip().lower() in LICENCES, "licence not allowed")
        for key in ("source_url", "licence", "licence_url", "attribution"):
            require(source[key] == row[key], f"source {key} mismatch")
        hashes = [f["sha256"] for f in registry["files"] if f["clip_id"] == source["clip_id"]]
        require(hashes == [source["sha256"]], "source hash not in acquisition registry")

        artifact = demo["artifact"]
        expected = f"objects/sha256/{artifact['sha256']}.json"
        require(artifact["path"] == expected, "artifact path is not content-addressed")
        path, data = checked_ref(artifact, artifact_root)
        require(len(data) == artifact["bytes"], "artifact byte count mismatch")
        payload = load_json(path)
        provenance = demo["provenance"]
        for key in ("artifact_evidence", "ledger"):
            require(provenance[key]["path"].startswith("evidence/") and
                    provenance[key]["path"].endswith(".json"), "expected JSON run evidence")
        _, original = checked_ref(provenance["artifact_evidence"], root)
        require(data == original, "artifact differs from accepted evidence")
        require(provenance["report"]["path"] == f"Run-System/Runs/{provenance['run_id']}/REPORT.md", "run report path mismatch")
        checked_ref(provenance["report"], root)
        ledger_path, _ = checked_ref(provenance["ledger"], root)
        ledger = load_json(ledger_path)
        require(ledger.get("run") == provenance["run_id"], "ledger run mismatch")
        jobs = [j for j in ledger.get("jobs", []) if j.get("app_id") == provenance["app_id"]]
        require(len(jobs) == 1 and jobs[0].get("rc") == 0, "successful ledger app missing")
        job_index = ledger["jobs"].index(jobs[0])
        for numeric in provenance["numeric"]:
            require(type(numeric["value"]) in (int, float) and math.isfinite(numeric["value"]), "non-finite numeric value")
            target = payload if numeric["evidence"] == "artifact" else ledger
            if numeric["evidence"] == "ledger":
                require(numeric["pointer"].startswith(f"/jobs/{job_index}/"), "numeric ledger pointer must identify the declared app")
            try:
                actual = pointer(target, numeric["pointer"])
            except (KeyError, IndexError, TypeError, ValueError) as exc:
                raise ValueError("numeric pointer not found") from exc
            require(type(actual) in (int, float) and math.isfinite(actual) and actual == numeric["value"], "numeric evidence mismatch")
            require(numeric["label"] == demo["label"], "numeric label mismatch")
        if artifact["kind"] == "scene-descriptor":
            scene_schema = load_json(ROOT / "contracts/scene/scene.schema.json")
            scene_errors = list(Draft202012Validator(scene_schema).iter_errors(payload))
            require(not scene_errors, "artifact is not a scene-v1 descriptor")
            require(demo["label"] == "measured" and payload.get("synthetic") is False, "scene label mismatch")
            sources = [s for s in payload.get("provenance", {}).get("sources", [])
                       if s.get("clip_id", "").upper() == source["clip_id"]]
            require(len(sources) == 1, "artifact clip mismatch")
            # scene_job uses the contract spelling; CSV credit remains verbatim.
            scene_licence = {"Pexels License": "Pexels"}.get(source["licence"], source["licence"])
            require(sources[0].get("license") == scene_licence and
                    all(sources[0].get(k) == source[k] for k in ("source_url", "attribution")),
                    "artifact source metadata mismatch")
            require(payload.get("scale", {}).get("status") != "verified", "v1 only accepts unverified scale")
            require(payload.get("render", {}).get("point_count", 0) <= 2_000_000, "viewer point limit")
            require(all(0 < a.get("bytes", 0) <= ARTIFACT_BYTES for a in payload.get("assets", [])), "viewer asset limit")
        else:
            require(demo["label"] == {"simulation-record": "simulated", "fixture-record": "fixture"}[artifact["kind"]], "artifact kind/label mismatch")
            require(payload.get("label") == demo["label"] and payload.get("clip_id") == source["clip_id"], "simulation/fixture identity mismatch")
        require(demo["scale_verified"] is False, "scale verification unsupported by v1")
    if "defaults" in manifest:
        defaults = manifest["defaults"]
        selected = next((d for d in manifest["demos"] if d["id"] == defaults["demo_id"]), None)
        require(selected is not None, "default demo not found")
        require(all(p in selected["provenance"]["numeric"] for p in defaults["parameters"]),
                "default parameters must match selected demo numeric evidence")
        require(selected["source"].get("kind") == "synthetic" or not defaults["parameters"],
                "display-only scene defaults cannot expose physics parameters")
        require(defaults["fallback_evidence"]["path"] == "evidence/S12/S12f-fallback.json",
                "expected S12f fallback evidence")
        fallback_path, _ = checked_ref(defaults["fallback_evidence"], root)
        fallback = load_json(fallback_path)
        require(fallback["decision"]["tier"] == "VIRTUAL_LAB_ONLY" and
                fallback["decision"]["real_scene_prediction"] == "WITHHELD" and
                fallback["gate_rs"]["status"] == "NOT_MET", "review S12f fallback before changing defaults")
        gate_path, _ = checked_ref(fallback["gate_rs"], root)
        require(load_json(gate_path)["result"]["status"] == "NOT_MET", "Gate RS must remain NOT_MET")
    return manifest


def validate_local_simulation(demo, artifact_root, root):
    """Check original local acceptance bytes, without inventing clip/job custody."""
    artifact, provenance = demo["artifact"], demo["provenance"]
    require(demo["label"] == "simulated" and artifact["kind"] == "simulation-record",
            "synthetic source requires simulated record")
    require(provenance.get("execution") == "accepted-local-simulation",
            "synthetic source requires local simulation provenance")
    require(artifact["path"] == f"objects/sha256/{artifact['sha256']}.json",
            "artifact path is not content-addressed")
    path, data = checked_ref(artifact, artifact_root)
    require(len(data) == artifact["bytes"], "artifact byte count mismatch")
    evidence = provenance["artifact_evidence"]
    require(evidence["path"].startswith("evidence/") and evidence["path"].endswith(".json"),
            "expected JSON run evidence")
    _, original = checked_ref(evidence, root)
    require(data == original, "artifact differs from accepted evidence")
    require(provenance["report"]["path"] == f"Run-System/Runs/{provenance['run_id']}/REPORT.md",
            "run report path mismatch")
    _, report = checked_ref(provenance["report"], root)
    require(evidence["path"] in report.decode("utf-8"), "run report does not identify simulation evidence")
    payload = load_json(path)
    require(payload.get("source") == "simulated" and
            payload.get("scope") == "synthetic four-template acceptance only",
            "not a synthetic lab acceptance record")
    record_pointer = provenance["record_pointer"]
    try:
        record = pointer(payload, record_pointer)
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise ValueError("simulation record pointer not found") from exc
    require(isinstance(record, dict) and record.get("template") in ("free_fall", "projectile", "pendulum") and
            record.get("status") == "passed" and record.get("deterministic") is True,
            "expected passed deterministic free-fall, projectile or pendulum simulation")
    require(demo["id"] == "simulated-" + record["template"].replace("_", "-") + "-" + record["case"],
            "simulation identity does not match selected case")
    for numeric in provenance["numeric"]:
        require(numeric["evidence"] == "artifact" and numeric["label"] == "simulated" and
                numeric["pointer"].startswith(record_pointer + "/"),
                "numeric pointer must identify the selected simulated case")
        try:
            actual = pointer(payload, numeric["pointer"])
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise ValueError("numeric pointer not found") from exc
        require(type(actual) in (int, float) and math.isfinite(actual) and
                type(numeric["value"]) in (int, float) and
                math.isfinite(numeric["value"]) and actual == numeric["value"],
                "numeric evidence mismatch")


def validate_file(path, artifact_root=None, evidence_root=ROOT):
    path = Path(path)
    bounded(path, MANIFEST_BYTES)
    return validate(load_json(path), artifact_root or path.parent, evidence_root)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--evidence-root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        value = validate_file(args.manifest, evidence_root=args.evidence_root)
        print(f"VALID: {len(value['demos'])} local-only demos; no publication/gate assertion")
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(1, f"INVALID: {exc}\n")
