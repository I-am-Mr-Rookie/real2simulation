"""Read-only guest metadata API; no inference, raw media, or challenge answers."""
import hashlib
import json
from pathlib import Path
import re

from fastapi import FastAPI
from fastapi.responses import Response

from Build.library.example import safe_defaults
from Build.library.playable import load_index, load_trace
from Build.library.validate import (
    ARTIFACT_BYTES, MANIFEST_BYTES, ROOT, checked_ref, file_under,
    require, validate_file,
)

CATALOGUES = ("free-fall.json", "projectile.json", "pendulum.json", "scenes.json", "mystery-g.json")
PREFIX = "/api/library"


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def load_guest(root=ROOT):
    """Validate current custody and project only guest-safe, selected object bytes.

    Do not cache authority: revocation/corruption must affect the next request.
    Raw simulation objects contain answers shared across local catalogues.
    """
    root = Path(root)
    artifacts = root / "test-data/library-artifacts"
    index = load_index(root)
    demos, objects = {}, {}
    catalogues = [validate_file(file_under(artifacts, name), artifacts, root) for name in CATALOGUES]
    challenge_records = {(d["provenance"]["artifact_evidence"]["sha256"], d["provenance"]["record_pointer"])
                         for c in catalogues for d in c["demos"] if "challenge" in d}
    for catalogue in catalogues:
        for demo in catalogue["demos"]:
            artifact = demo["artifact"]
            _, data = checked_ref(artifact, artifacts)
            require(len(data) == artifact["bytes"], "artifact byte count mismatch")
            kind = artifact["kind"]
            if kind == "simulation-record":
                provenance = demo["provenance"]
                if (provenance["artifact_evidence"]["sha256"], provenance["record_pointer"]) in challenge_records:
                    demos[demo["id"]] = unavailable(demo,
                        "Trace withheld: this accepted record also supplies the Mystery-g challenge answer.")
                    continue
                loaded = load_trace(root, demo, index)
                if loaded is None:
                    demos[demo["id"]] = unavailable(demo,
                        "No complete preserved accepted setup with parameter JSON pointers for this case.")
                    continue
                artifact, data = loaded
                kind = "simulation-trace"
            if kind == "scene-descriptor":
                # shortcut: S18k has no accepted local PLY bytes; revalidate a bundle before enabling scenes.
                demos[demo["id"]] = unavailable(demo,
                    "Declared PLY bytes are absent from accepted local evidence; no verified render bundle.")
                continue
            require(kind in ("simulation-trace", "challenge-record"),
                    "unsupported guest artifact")
            require(len(data) <= ARTIFACT_BYTES, "guest artifact exceeds byte limit")
            sha = hashlib.sha256(data).hexdigest()
            objects[sha] = data
            defaults = safe_defaults(root, demo)
            defaults.pop("fallback_evidence")  # Offline audit references are not guest routes.
            entry = {key: demo[key] for key in
                     ("id", "title", "source", "scale_verified", "scale_label", "gates", "limitations")}
            entry.update({"label": "SIMULATED" if demo["source"].get("kind") == "synthetic"
                          else "SCALE_UNVERIFIED", "display_only": True,
                          "availability": "playable" if kind == "simulation-trace" else "metadata-only", "defaults": defaults,
                          "artifact": {"kind": kind, "media_type": "application/json", "sha256": sha,
                                       "bytes": len(data), "href": f"{PREFIX}/artifacts/{sha}"}})
            if kind == "simulation-trace":
                entry["limitations"] = [
                    "Bounded accepted synthetic trajectory only; no scene-v1 geometry or real-scene physics."
                    if text == "Stored acceptance metrics and replay hashes only; no trajectory or playable assets bundled."
                    else text for text in entry["limitations"]]
                custody = index["entries"][demo["id"]]["custody"]
                if custody["produced_trace_sha256"] != custody["accepted_trace_sha256"]:
                    entry["limitations"].append(
                        "Regenerated with current accepted simulator; historical trace differs after model update. "
                        "No historical acceptance error/accuracy claim is inherited.")
            if "challenge" in demo:
                entry["challenge"] = demo["challenge"].copy()
            if demo["id"] in demos:
                require(demos[demo["id"]]["artifact"] == entry["artifact"], "conflicting guest demo id")
            demos[demo["id"]] = entry
    for demo_id, title, reason in (
        ("apollo", "Apollo 15", "Moon result not measured; no approved trackable demo."),
        ("bounce", "Bounce", "No accepted complete bounce record."),
        ("rm05-scene", "RM05 scene", "No accepted scene-v1 viewer descriptor."),
    ):
        demos[demo_id] = {"id": demo_id, "title": title, "label": "UNAVAILABLE",
                          "availability": "unavailable", "reason": reason, "artifact": None}
    selected = demos["simulated-mystery-g"]["defaults"]
    manifest = {"schema_version": "guest-1.0.0", "audience": "anonymous-guest",
                "scope": "accepted synthetic traces and answer-free challenge metadata; no raw media or real-scene physics",
                "defaults": selected, "demos": list(demos.values())}
    require(len(encode(manifest)) <= MANIFEST_BYTES, "guest manifest exceeds byte limit")
    return manifest, objects


def unavailable(demo, reason):
    return {"id": demo["id"], "title": demo["title"], "label": "UNAVAILABLE",
            "availability": "unavailable", "reason": reason, "artifact": None}


def artifact_response(artifact_id, objects):
    """No path construction from user input; only guest projection hashes are addressable."""
    if re.fullmatch(r"[a-f0-9]{64}", artifact_id) is None:
        return error(400, "invalid_artifact_id")
    data = objects.get(artifact_id)
    if data is None:
        return error(404, "artifact_not_found")
    if len(data) > ARTIFACT_BYTES or hashlib.sha256(data).hexdigest() != artifact_id:
        return error(503, "artifact_unavailable")
    return Response(data, media_type="application/json", headers={
        "Cache-Control": "public, max-age=31536000, immutable",
        "ETag": f'"{artifact_id}"', "X-Content-Type-Options": "nosniff",
    })


def error(status, code):
    return Response(encode({"error": code}), status_code=status, media_type="application/json",
                    headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"})


def create_app(root=ROOT):
    """Mount/serve this factory from S18g; no auth middleware or external services needed."""
    app = FastAPI(title="Real2Simulation guest library", docs_url=None, redoc_url=None, openapi_url=None)

    @app.get(f"{PREFIX}/manifest")
    def manifest():
        try:
            document, _ = load_guest(root)
        except (OSError, ValueError, KeyError, TypeError):
            return error(503, "library_unavailable")
        return Response(encode(document), media_type="application/json",
                        headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"})

    @app.get(f"{PREFIX}/artifacts/{{artifact_id:path}}")
    def artifact(artifact_id: str):
        if re.fullmatch(r"[a-f0-9]{64}", artifact_id) is None:
            return error(400, "invalid_artifact_id")
        try:
            _, objects = load_guest(root)
        except (OSError, ValueError, KeyError, TypeError):
            return error(503, "library_unavailable")
        return artifact_response(artifact_id, objects)

    return app
