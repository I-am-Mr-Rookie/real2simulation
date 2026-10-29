"""S13f segment + reconstruct workers for JobRunner over the EXISTING GPU entry points (unedited).

reconstruct: documented S06d command `modal run Build/gpu/scene_job.py --scene --out --manifest` (infra/modal/README.md);
its contracts/scene bundle is re-validated here. segment: the S07b SAM3.1 track Modal function; it returns
object ids/boxes + a tracking record, never masks/media (finding recorded in the S13f-orch30 REPORT).
Every paid dispatch first reserves against a JSONL ledger (job count + USD cap) and raises SPEND_PAUSED past it.
Failures become contract StageErrors: bad input -> INVALID_INPUT (never retried), runtime -> PROCESSING_FAILED (retryable).
"""
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from Build.pipeline.jobs import StageError

ROOT = Path(__file__).resolve().parents[2]
MAX_JOBS, CAP_USD = 2, 1.0  # S13f contract: <=2 Modal GPU jobs, <=$1 total, retries 0
# S06f basis: A10G x (timeout 300 + startup 240 s) x list rates = $0.199, plus image/egress margin.
RECONSTRUCT_RESERVE_USD = 0.5
SEGMENT_RESERVE_USD = 0.5  # shortcut: assumed bound (L4/A10G x 900 s timeout ~$0.30); replace with S07b billed rate
BAD_INPUT = ("not an owner-approved", "not allowlisted", "missing from clips.csv", "SHA256 mismatch",
             "need >=2 frames", "not in ")
MODAL_CMD = ["uv", "run", "--no-project", "--python", "3.11", "--with", "modal==1.6.3", "--with", "numpy",
             "--with", "jsonschema", "--env-file", "../../.env", "modal", "run", "Build/gpu/scene_job.py"]


def _now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def reserve(ledger, stage, key, usd):
    """Append a reservation row or raise SPEND_PAUSED; rows count even if the job later fails (conservative)."""
    ledger = Path(ledger)
    rows = [json.loads(x) for x in ledger.read_text(encoding="utf-8").splitlines() if x] if ledger.exists() else []
    spent = sum(r["reserved_usd"] for r in rows)
    if len(rows) >= MAX_JOBS or spent + usd > CAP_USD:
        raise StageError("SPEND_PAUSED", f"GPU budget guard: {len(rows)} jobs, reserved USD {spent:.2f}, next {usd:.2f}", False)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"utc": _now(), "stage": stage, "idempotency_key": key, "reserved_usd": usd,
                             "billed_usd": None}) + "\n")


def _write(out_dir, name, doc):
    path = Path(out_dir) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(doc, indent=1, ensure_ascii=False) + "\n").encode("utf-8")
    path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def _tail(text, n=300):
    """Last meaningful line; Rich panels from the Modal CLI wrap errors in box-drawing borders."""
    lines = [s for s in (x.strip(" \u2500\u2502\u256d\u256e\u2570\u256f+-|") for x in (text or "").splitlines()) if s]
    return (lines[-1] if lines else "no output")[-n:]


def reconstruct(key, scene_id, manifest, out_dir, ledger, run=subprocess.run, cwd=ROOT):
    """reconstruct worker: run scene_job, validate its bundle, write reconstruction.json; returns its sha256."""
    reserve(ledger, "reconstruct", key, RECONSTRUCT_RESERVE_USD)
    out_dir = Path(out_dir)
    bundle = out_dir / "bundle"
    cmd = MODAL_CMD + ["--scene", scene_id, "--out", str(bundle), "--manifest", str(manifest)]
    try:
        # Piped Modal CLI on Windows defaults to cp1252 and can die printing Rich glyphs (S13f-orch30 attempt 1).
        proc = run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900,
                   env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"})
    except Exception as exc:  # noqa: BLE001 - launcher/timeout failure is a retryable stage failure
        raise StageError("PROCESSING_FAILED", f"reconstruct: launcher {type(exc).__name__}: {exc}"[:300], True)
    if proc.returncode != 0:
        text = (proc.stderr or "") + (proc.stdout or "")
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "reconstruct-failure.log").write_text(text[-20000:], encoding="utf-8")  # full detail for the retry decision
        bad = any(s in text for s in BAD_INPUT)
        msg = _tail(proc.stderr if (proc.stderr or "").strip() else proc.stdout)
        raise StageError("INVALID_INPUT" if bad else "PROCESSING_FAILED", f"reconstruct rc {proc.returncode}: {msg}", not bad)
    sys.path.insert(0, str(ROOT / "contracts/scene"))
    from validate_scene import load_json, validate
    try:
        scene = validate(load_json(bundle / "scene.json"), bundle)
        log = json.loads((bundle / f"{scene_id}-scene-log.json").read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        raise StageError("PROCESSING_FAILED", f"reconstruct: invalid bundle: {exc}"[:300], True)
    return _write(out_dir, "reconstruction.json", {
        "contract_version": "1.0.0", "kind": "reconstruction", "stage": "reconstruct", "idempotency_key": key,
        "scene_id": scene["id"], "synthetic": scene["synthetic"],
        "scene_sha256": hashlib.sha256((bundle / "scene.json").read_bytes()).hexdigest(),
        "point_count": scene["render"]["point_count"], "app_id": log.get("app_id"), "timing_s": log.get("timing_s"),
        "estimated_usd": ((log.get("cost") or {}).get("estimated") or {}).get("total_usd"),
        "note": "MapAnything nominal scale, gravity unknown; validated contracts/scene bundle. Not Gate R/physical evidence."})


def sam_call(frames, metadata, frame_map, prompt):
    """Live call() for segment: the S07b track function in an ephemeral app, bypassing its ST03 local entrypoint
    (which writes evidence/S07/S07b/orch14/result.json). Needs a modal client.
    shortcut: modal_track hardcodes OBJECT_ID 2 (ST03 apple) inside track; parameterize in the S07 lane before room clips."""
    def call():
        sys.path.insert(0, str(ROOT / "Build/measurement/runtime"))
        import modal_track
        with modal_track.app.run():
            return modal_track.track.remote(frames, metadata, frame_map, prompt)
    return call


def segment(key, call, out_dir, ledger, prompt):
    """segment worker: call() runs the SAM3.1 track function, returns its JSON text; returns segmentation.json sha256."""
    reserve(ledger, "segment", key, SEGMENT_RESERVE_USD)
    try:
        raw = call()
    except Exception as exc:  # noqa: BLE001 - Modal/transport failure is retryable
        raise StageError("PROCESSING_FAILED", f"segment: {type(exc).__name__}: {exc}"[:300], True)
    try:
        out = json.loads(raw)
    except (TypeError, ValueError):
        raise StageError("PROCESSING_FAILED", "segment: reply is not JSON", True)
    if out.get("error"):
        raise StageError("PROCESSING_FAILED", f"segment: {_tail(out['error'])}", True)
    missing = [s for s in ("checkpoint", "model_loaded", "tracked") if s not in out.get("stages", [])]
    ckpt = out.get("checkpoint") or {}
    if missing or not out.get("stream") or not isinstance(out.get("record"), dict) or len(ckpt.get("sha256") or "") != 64:
        raise StageError("PROCESSING_FAILED", f"segment: incomplete SAM output (missing stages {missing})", True)
    return _write(out_dir, "segmentation.json", {
        "contract_version": "1.0.0", "kind": "segmentation", "stage": "segment", "idempotency_key": key,
        "prompt": prompt, "checkpoint": ckpt, "gpu": out.get("gpu"), "frames": len(out["stream"]),
        "objects": out["stream"], "record": out["record"],
        "note": "SAM3.1 object ids/boxes per frame (entry point returns no masks). Not calibration/physical evidence."})


if __name__ == "__main__":  # live reconstruct only: python -m Build.pipeline.gpu_stages <scene> <manifest> <out> <ledger>
    scene_id, manifest, out_dir, ledger = sys.argv[1:]
    key = "reconstruct:" + hashlib.sha256(Path(manifest).read_bytes()).hexdigest()
    try:
        print(reconstruct(key, scene_id, Path(manifest).resolve(), Path(out_dir).resolve(), ledger))
    except StageError as e:
        sys.exit(f"{e.code} retryable={e.retryable}: {e.message}")
