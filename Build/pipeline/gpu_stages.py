"""S13f segment + reconstruct workers for JobRunner over the existing GPU entry points.

reconstruct: documented S06d command `modal run Build/gpu/scene_job.py --scene --out --manifest` (infra/modal/README.md);
its contracts/scene bundle is re-validated here. segment: the parameterized S07b CLI
`modal run Build/measurement/runtime/modal_track.py --clip --first --last --prompt --object-id --out --masks`
(writes one raw result, never overwrites); its ids/boxes/centroids/COCO-RLE masks are validated here.
Every paid dispatch first reserves against a JSONL ledger (job count + USD cap) and raises SPEND_PAUSED past it.
Failures become contract StageErrors: bad input -> INVALID_INPUT (never retried), runtime -> PROCESSING_FAILED (retryable).
"""
import hashlib
from contextvars import ContextVar
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from Build.pipeline.jobs import StageError
from Build.guardrails.admission import ReconstructionPaused
from Build.guardrails.reservations import reserve_gpu

ROOT = Path(__file__).resolve().parents[2]
MAX_JOBS, CAP_USD = 2, 1.0  # S13f contract: <=2 Modal GPU jobs, <=$1 total, retries 0
# S06f basis: A10G x (timeout 300 + startup 240 s) x list rates = $0.199, plus image/egress margin.
RECONSTRUCT_RESERVE_USD = 0.5
SEGMENT_RESERVE_USD = 0.5  # shortcut: assumed bound (L4/A10G x 900 s timeout ~$0.30); replace with S07b billed rate
BAD_INPUT = ("not an owner-approved", "not allowlisted", "missing from clips.csv", "SHA256 mismatch",
             "need >=2 frames", "not in ")
# Relative to cwd=ROOT (main checkout vs .worktrees/<run>): uv splits --env-file values on spaces.
ENV_FILE = ".env" if (ROOT / ".env").exists() else "../../.env"
MODAL_CMD = ["uv", "run", "--no-project", "--python", "3.11", "--with", "modal==1.6.3", "--with", "numpy",
             "--with", "jsonschema", "--env-file", ENV_FILE, "modal", "run", "Build/gpu/scene_job.py"]
TRACK_CMD = ["uv", "run", "--no-project", "--python", "3.12", "--with", "modal==1.6.3", "--env-file", ENV_FILE,
             "modal", "run", "Build/measurement/runtime/modal_track.py"]
UTF8_ENV = {"PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
DISPATCH_REQUEST_ID = ContextVar("modal_request_id", default=None)


def _now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def reserve(ledger, stage, key, usd):
    """Reserve or pause; failed/unreconciled jobs retain their active slot and liability."""
    try:
        return reserve_gpu(ROOT, ledger, stage, key, usd, max_jobs=MAX_JOBS, cap_usd=CAP_USD)
    except ReconstructionPaused as exc:
        raise StageError("SPEND_PAUSED", str(exc), False) from None


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
    request_id = reserve(ledger, "reconstruct", key, RECONSTRUCT_RESERVE_USD)
    out_dir = Path(out_dir)
    bundle = out_dir / "bundle"
    cmd = MODAL_CMD + ["--scene", scene_id, "--out", str(bundle), "--manifest", str(manifest)]
    try:
        # Piped Modal CLI on Windows defaults to cp1252 and can die printing Rich glyphs (S13f-orch30 attempt 1).
        proc = run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900,
                   env={**os.environ, **UTF8_ENV, "S20_MODAL_REQUEST_ID": request_id})
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


def sam_call(clip, first, last, prompt, object_id, raw_out, run=subprocess.run, cwd=ROOT):
    """Live call() for segment: the parameterized S07b CLI with --masks; returns the raw result JSON text.
    A clean raw result already on disk is reused (no second paid dispatch); a failed one is moved aside, then retried."""
    raw_out = Path(raw_out)

    def call():
        if raw_out.exists():
            text = raw_out.read_text(encoding="utf-8")
            if not json.loads(text).get("error"):
                return text
            raw_out.rename(raw_out.with_name(f"{raw_out.stem}.failed-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"))
        cmd = TRACK_CMD + ["--clip", clip, "--first", str(first), "--last", str(last), "--prompt", prompt,
                           "--object-id", str(object_id), "--out", str(raw_out), "--masks"]
        proc = run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1500,
                   env={**os.environ, **UTF8_ENV, **({"S20_MODAL_REQUEST_ID": DISPATCH_REQUEST_ID.get()} if DISPATCH_REQUEST_ID.get() else {})})
        if proc.returncode != 0:
            text = (proc.stderr or "") + (proc.stdout or "")
            raw_out.parent.mkdir(parents=True, exist_ok=True)
            raw_out.with_name("segment-failure.log").write_text(text[-20000:], encoding="utf-8")
            bad = any(s in text for s in BAD_INPUT + ("refusing to overwrite", "required", "at least three frames"))
            raise StageError("INVALID_INPUT" if bad else "PROCESSING_FAILED",
                             f"segment rc {proc.returncode}: {_tail(proc.stderr if (proc.stderr or '').strip() else proc.stdout)}", not bad)
        return raw_out.read_text(encoding="utf-8")
    return call


def _bad(msg):
    return StageError("PROCESSING_FAILED", f"segment: {msg}"[:300], True)


def validate_segment(raw, prompt, object_id, frame_map=None):
    """Check one raw S07b result (JSON text) for object_id; frame_map overrides the recorded one (e.g. PTS errata).
    Returns per-frame index/pts/box/centroid/mask for the tracked object; raises a retryable StageError if invalid."""
    try:
        out = json.loads(raw)
    except (TypeError, ValueError):
        raise _bad("reply is not JSON")
    if out.get("error"):
        raise _bad(_tail(out["error"]))
    missing = [s for s in ("checkpoint", "model_loaded", "tracked") if s not in out.get("stages", [])]
    ckpt, rec = out.get("checkpoint") or {}, out.get("record") or {}
    if missing or not out.get("stream") or len(ckpt.get("sha256") or "") != 64:
        raise _bad(f"incomplete SAM output (missing stages {missing})")
    if (rec.get("tracking") or {}).get("object_id") != object_id:
        raise _bad(f"record tracks object {(rec.get('tracking') or {}).get('object_id')}, expected {object_id}")
    fmap = [tuple(x) for x in (frame_map or out.get("frame_map") or [])]
    idx = [s[0] for s in out["stream"]]
    if [i for i, _ in fmap] != idx or any(a[1] >= b[1] for a, b in zip(fmap, fmap[1:])):
        raise _bad("frame_map does not match stream frames or PTS not increasing")
    pts, centroid = dict(fmap), {f["frame_index"]: (f["x_px"], f["y_px"]) for f in rec.get("frames", [])}
    masks = {m[0]: m[1].get(str(object_id)) for m in out.get("masks") or []}
    h, w = rec.get("height_px"), rec.get("width_px")
    frames = []
    for i, ids, boxes in out["stream"]:
        m = masks.get(i)
        if object_id not in ids or i not in centroid or m is None:
            raise _bad(f"frame {i}: object {object_id} has no box, centroid or mask")
        if m["size"] != [h, w] or sum(m["counts"]) != h * w:
            raise _bad(f"frame {i}: RLE mask is not {h}x{w}")
        frames.append({"frame_index": i, "pts_s": pts[i], "box_xywh_norm": boxes[ids.index(object_id)],
                       "centroid_px": list(centroid[i]), "mask_rle": m})
    return {"prompt": prompt, "object_id": object_id, "clip_id": rec.get("clip_id"), "source_sha256": rec.get("source_sha256"),
            "checkpoint": ckpt, "gpu": out.get("gpu"), "frame_sha256": out.get("frame_sha256"), "frames": frames}


def _seg_doc(key, seg, source):
    return {"contract_version": "1.0.0", "kind": "segmentation", "stage": "segment", "idempotency_key": key,
            "source": source, **seg,
            "note": "SAM3.1 box/centroid/COCO-RLE mask per frame for one object. Not calibration/physical evidence."}


def segment(key, call, out_dir, ledger, prompt, object_id, frame_map=None):
    """segment worker: call() returns raw S07b result JSON text; writes validated segmentation.json, returns its sha256."""
    request_id = reserve(ledger, "segment", key, SEGMENT_RESERVE_USD)
    token = DISPATCH_REQUEST_ID.set(request_id)
    try:
        raw = call()
    except StageError:
        raise
    except Exception as exc:  # noqa: BLE001 - Modal/transport failure is retryable
        raise StageError("PROCESSING_FAILED", f"segment: {type(exc).__name__}: {exc}"[:300], True)
    finally:
        DISPATCH_REQUEST_ID.reset(token)
    return _write(out_dir, "segmentation.json", _seg_doc(key, validate_segment(raw, prompt, object_id, frame_map), "live"))


def _main(argv):
    """reconstruct: <scene> <manifest> <out> <ledger> | segment <clip> <first> <last> <prompt> <object_id> <out> <ledger>
    | replay <result.json> <prompt> <object_id> <out> [errata frame_map.json]  (offline, no spend)"""
    if argv[0] == "replay":
        raw = Path(argv[1]).read_text(encoding="utf-8")
        fmap = json.loads(Path(argv[5]).read_text(encoding="utf-8"))["frame_map"] if len(argv) > 5 else None
        key = "segment:" + hashlib.sha256(raw.encode()).hexdigest()
        return _write(argv[4], "segmentation.json", _seg_doc(key, validate_segment(raw, argv[2], int(argv[3]), fmap),
                                                            f"replay of {argv[1]}" + (f" + frame_map {argv[5]}" if fmap else "")))
    if argv[0] == "segment":
        clip, first, last, prompt, oid, out_dir, ledger = argv[1:]
        out_dir = Path(out_dir).resolve()
        key = f"segment:{clip}:{first}-{last}:{prompt}:{oid}"
        return segment(key, sam_call(clip, int(first), int(last), prompt, int(oid), out_dir / "raw-result.json"),
                       out_dir, ledger, prompt, int(oid))
    scene_id, manifest, out_dir, ledger = argv
    key = "reconstruct:" + hashlib.sha256(Path(manifest).read_bytes()).hexdigest()
    return reconstruct(key, scene_id, Path(manifest).resolve(), Path(out_dir).resolve(), ledger)


if __name__ == "__main__":
    try:
        print(_main(sys.argv[1:]))
    except StageError as e:
        sys.exit(f"{e.code} retryable={e.retryable}: {e.message}")
