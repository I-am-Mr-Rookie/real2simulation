"""Offline simulator export and bounded guest-trace custody; no runtime simulation."""
import json
import math
from pathlib import Path
import subprocess

from Build.library.example import ref, store
from Build.library.validate import MANIFEST_BYTES, ROOT, bounded, checked_ref, pointer, require

MAX_SAMPLES = 4096
INDEX = "test-data/library-artifacts/playable.json"
# shortcut: three preserved setup candidates; extend only with accepted parameter pointers.
SOURCES = {
    "simulated-free-fall-baseline-short": "free_fall",
    "simulated-projectile-baseline-short": "projectile",
    "simulated-pendulum-short-small-angle": "pendulum",
}
PRODUCERS = ("Build/library/generate-trace.mjs", "Build/simulator/trajectories.mjs",
             "Build/simulator/extended-templates.mjs", "Build/simulator/rk4.mjs",
             "Build/simulator/replay.mjs")


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def validate_trace(trace):
    require(isinstance(trace, dict) and set(trace) ==
            {"kind", "source", "inputProvenance", "dt_s", "samples", "label"}, "trace fields invalid")
    require(trace["kind"] in ("free-fall", "projectile", "pendulum") and
            trace["source"] == "simulated" and trace["inputProvenance"] == "synthetic" and
            trace["label"] == "SIMULATED", "trace labels invalid")
    dt = trace["dt_s"]
    require(type(dt) in (int, float) and math.isfinite(dt) and dt > 0, "trace timestep invalid")
    samples = trace["samples"]
    require(isinstance(samples, list) and 2 <= len(samples) <= MAX_SAMPLES, "trace sample limit invalid")
    for i, sample in enumerate(samples):
        require(isinstance(sample, dict) and set(sample) == {"step", "time_s", "position_m"},
                "trace sample fields invalid")
        require(type(sample["step"]) is int and sample["step"] == i and
                type(sample["time_s"]) in (int, float) and math.isfinite(sample["time_s"]) and
                sample["time_s"] == i * dt, "trace sample timing invalid")
        xyz = sample["position_m"]
        require(isinstance(xyz, list) and len(xyz) == 3 and
                all(type(v) in (int, float) and math.isfinite(v) for v in xyz), "trace position invalid")
    require(len(encode(trace)) <= MANIFEST_BYTES, "trace byte limit exceeded")
    return trace


def input_pointers(template, record_pointer):
    parameters = ("length", "release_angle", "initial_angular_velocity") if template == "pendulum" else (
        ("drop_height", "initial_vertical_velocity") if template == "free_fall" else
        ("launch_height", "horizontal_speed"))
    return {"setup": ["/spec/placement/origin/value", "/spec/environment/gravity/value",
                      "/spec/environment/gravity_direction"] +
                     ["/spec/parameters/" + name + "/value" for name in parameters],
            "acceptance": [record_pointer + "/" + name for name in
                           ("duration_s", "time_step_s", "gravity_m_s2", "samples", "replay/traceHash")]}


def generate(root, demo):
    """No guessed case parameters: only three independently preserved accepted setups."""
    root = Path(root)
    template = SOURCES[demo["id"]]
    provenance = demo["provenance"]
    setup_ref = ref(root, f"evidence/S10/browser-simulation/{template}.artifact.json")
    _, setup_bytes = checked_ref(setup_ref, root, MANIFEST_BYTES)
    _, acceptance_bytes = checked_ref(provenance["artifact_evidence"], root, MANIFEST_BYTES)
    record = pointer(json.loads(acceptance_bytes), provenance["record_pointer"])
    payload = {"artifact": json.loads(setup_bytes), "record": record}
    process = subprocess.run(["node", str(root / "Build/library/generate-trace.mjs")],
                             input=encode(payload), capture_output=True, cwd=root, timeout=30)
    require(process.returncode == 0, "accepted trace generation failed: " + process.stderr.decode())
    require(len(process.stdout) <= MANIFEST_BYTES, "generator output exceeds byte limit")
    result = json.loads(process.stdout)
    trace = validate_trace(result["trace"])
    return trace, {"setup": setup_ref, "acceptance": provenance["artifact_evidence"],
                   "record_pointer": provenance["record_pointer"],
                   "input_pointers": input_pointers(template, provenance["record_pointer"]),
                   "accepted_trace_sha256": record["replay"]["traceHash"],
                   "produced_trace_sha256": result["traceHash"],
                   "producers": [ref(root, path) for path in PRODUCERS]}


def build(root=ROOT):
    from Build.library.guest import CATALOGUES
    from Build.library.validate import validate_file
    root = Path(root)
    artifacts = root / "test-data/library-artifacts"
    entries = {}
    for name in CATALOGUES:
        for demo in validate_file(artifacts / name, artifacts, root)["demos"]:
            if demo["id"] not in SOURCES:
                continue
            trace, custody = generate(root, demo)
            entries[demo["id"]] = {"artifact": store(artifacts, encode(trace), "simulation-trace"),
                                    "samples": len(trace["samples"]), "custody": custody}
    document = {"version": "guest-traces-v1", "entries": entries}
    (root / INDEX).write_bytes(encode(document) + b"\n")
    return document


def load_trace(root, demo, index):
    """Recheck current accepted custody before exposing stored, bounded bytes."""
    item = index["entries"].get(demo["id"])
    if item is None:
        return None
    require(demo["id"] in SOURCES and demo["artifact"]["kind"] == "simulation-record",
            "trace is not a permitted demo")
    custody = item["custody"]
    provenance = demo["provenance"]
    require(custody["acceptance"] == provenance["artifact_evidence"] and
            custody["record_pointer"] == provenance["record_pointer"], "trace acceptance custody mismatch")
    expected_setup = f"evidence/S10/browser-simulation/{SOURCES[demo['id']]}.artifact.json"
    require(custody["setup"]["path"] == expected_setup, "trace setup identity mismatch")
    _, setup_bytes = checked_ref(custody["setup"], root, MANIFEST_BYTES)
    _, acceptance_bytes = checked_ref(custody["acceptance"], root, MANIFEST_BYTES)
    record = pointer(json.loads(acceptance_bytes), custody["record_pointer"])
    require(custody["input_pointers"] == input_pointers(SOURCES[demo["id"]], custody["record_pointer"]),
            "trace input pointers mismatch")
    for name, data in (("setup", json.loads(setup_bytes)), ("acceptance", json.loads(acceptance_bytes))):
        for value in custody["input_pointers"][name]:
            pointer(data, value)
    require([p["path"] for p in custody["producers"]] == list(PRODUCERS), "trace producer identity mismatch")
    for producer in custody["producers"]:
        checked_ref(producer, root, MANIFEST_BYTES)
    require(custody["accepted_trace_sha256"] == record["replay"]["traceHash"], "trace acceptance hash mismatch")
    require(isinstance(custody["produced_trace_sha256"], str) and len(custody["produced_trace_sha256"]) == 64 and
            all(c in "0123456789abcdef" for c in custody["produced_trace_sha256"]), "produced trace hash invalid")
    artifact = item["artifact"]
    require(artifact["kind"] == "simulation-trace" and artifact["media_type"] == "application/json" and
            artifact["path"] == f"objects/sha256/{artifact['sha256']}.json", "trace artifact identity invalid")
    _, data = checked_ref(artifact, Path(root) / "test-data/library-artifacts", MANIFEST_BYTES)
    require(len(data) == artifact["bytes"], "trace artifact byte mismatch")
    trace = validate_trace(json.loads(data))
    require(trace["kind"] == record["template"].replace("_", "-") and
            trace["dt_s"] == record["time_step_s"] and
            len(trace["samples"]) == record["samples"] == item["samples"], "trace record mismatch")
    return artifact, data


def load_index(root=ROOT):
    document = json.loads(bounded(Path(root) / INDEX, MANIFEST_BYTES))
    require(document["version"] == "guest-traces-v1" and isinstance(document["entries"], dict) and
            set(document["entries"]).issubset(SOURCES), "trace index invalid")
    return document


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
