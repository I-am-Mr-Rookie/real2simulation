"""S13e understand stage: Muse Wonder over a clip, video once, then an explicit keyframe-image fallback.

Reuses the S14 Muse request/validator (Build.agent.muse): the reply must be a number-free agent-response,
so nothing the model says is ever a measurement. Keyframe times in the output come from the S13c manifest.
post(body, idempotency_key) -> (http_status, json_body); the S13d key is forwarded per input mode.
"""
import base64
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from Build.agent import muse
from Build.agent.record_muse import IN_USD, OUT_USD
from Build.pipeline.jobs import StageError
from Build.guardrails.admission import ReconstructionPaused
from Build.guardrails.reservations import reserve_meta, project_ledger
from Build.guardrails.accounting import liability_usd, usd
from contracts.agent.validate import AgentContractError, validate_response

MAX_FRAMES = 4  # S13c risk: PD04 gave 600 JPEGs; cap before any paid call
FRAME_WIDTH = 512
MAX_VIDEO_BYTES = 8 * 1024 * 1024  # larger clips skip the video try (recorded), keyframes only
MEDIA_NOTE = ("The JSON is followed by {what} from a real licensed video clip. Describe only what is visible. "
              "Scale and gravity are unknown; never estimate sizes, distances, times or speeds.")


def sample(keyframes, cap=MAX_FRAMES):
    """Evenly spaced keyframes incl. first and last, at most cap (>= 2)."""
    if len(keyframes) <= cap:
        return list(keyframes)
    return [keyframes[round(i * (len(keyframes) - 1) / (cap - 1))] for i in range(cap)]


def clip_context(manifest, scene_id):
    """Number-free context in the S14 scene-context shape; provenance from clips.csv, not the model."""
    return {"schema_version": "scene-context/clip", "scene_id": scene_id,
            "label": manifest["provenance"].get("title") or manifest["provenance"]["clip_id"],
            "synthetic": False, "scale_status": "unverified", "gravity_status": "unknown",
            "surfaces": [], "colliders": [], "labels": []}


def _data_url(mime, data):
    return f"data:{mime};base64," + base64.b64encode(data).decode("ascii")


def frame_jpeg(path, width=FRAME_WIDTH):
    """Downscaled JPEG bytes via ffmpeg (already the S13c dependency)."""
    return subprocess.run(["ffmpeg", "-v", "error", "-nostdin", "-i", str(path), "-vf", f"scale='min({width},iw)':-2",
                           "-frames:v", "1", "-q:v", "4", "-f", "image2pipe", "-c:v", "mjpeg", "-"],
                          capture_output=True, check=True).stdout


def build(context, parts, what):
    body = muse.build_request(context)
    body["input"] = [{"role": "user", "content": [
        {"type": "input_text", "text": body["input"] + "\n" + MEDIA_NOTE.format(what=what)}, *parts]}]
    return body


def _reply(post, body, key, scene_id):
    """One call -> (validated response or None, attempt record). Transport errors count as a failed attempt."""
    try:
        status, reply = post(body, key)
    except StageError:
        raise  # budget guard: never fall through to another paid call
    except Exception as exc:  # noqa: BLE001 - any transport failure is a recorded failed attempt
        return None, {"idempotency_key": key, "http": None, "error": type(exc).__name__}
    rec = {"idempotency_key": key, "http": status, "status": reply.get("status"), "usage": reply.get("usage")}
    if status != 200:
        rec["error"] = str(reply.get("error") or reply)[:300]
        return None, rec
    try:
        text = muse.output_text(reply)
        return validate_response(text, (), scene_id), rec
    except AgentContractError as error:
        rec["issues"] = list(error.issues)[:8]
        rec["rejected_text"] = locals().get("text", "")[:400]  # evidence of what was rejected; never used downstream
        return None, rec


def run(key, manifest_path, scene_id, post, out_dir, video_path=None, cap=MAX_FRAMES):
    """understand worker for JobRunner: writes understanding.json, returns its sha256."""
    manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    context = clip_context(manifest, scene_id)
    attempts, response, mode, frames = [], None, None, []
    if video_path is None or Path(video_path).stat().st_size > MAX_VIDEO_BYTES:
        attempts.append({"mode": "video", "skipped": "no video path" if video_path is None else "over MAX_VIDEO_BYTES"})
    else:
        mime = "video/webm" if str(video_path).endswith(".webm") else "video/mp4"
        part = {"type": "input_video", "video_url": _data_url(mime, Path(video_path).read_bytes())}
        response, rec = _reply(post, build(context, [part], "the video"), key + "#video", scene_id)
        attempts.append({"mode": "video", **rec})
        mode = "video" if response else None
    if response is None:  # explicit fallback: sampled keyframe images
        frames = sample(manifest["keyframes"], cap)
        parts = [{"type": "input_image", "image_url": _data_url("image/jpeg", frame_jpeg(manifest_path.parent / f["file"]))}
                 for f in frames]
        response, rec = _reply(post, build(context, parts, "keyframe images in time order"), key + "#keyframes", scene_id)
        attempts.append({"mode": "keyframes", "frames": len(frames), **rec})
        if response is None:
            raise StageError("PROCESSING_FAILED", f"understand: no valid Muse reply ({rec.get('error') or rec.get('issues')})", True)
        mode = "keyframes"
    out = {"contract_version": "1.0.0", "kind": "understanding", "stage": "understand", "idempotency_key": key,
           "clip_id": manifest["provenance"]["clip_id"],
           "keyframe_manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
           "input_mode": mode, "fallback_used": mode == "keyframes", "attempts": attempts,
           "frames": [{"index": f["index"], "time_s": f["time_s"], "time_source": f["time_source"]} for f in frames],
           "response": response,
           "note": "Model description only (validated number-free agent-response); not a measurement."}
    path = Path(out_dir) / "understanding.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    return hashlib.sha256(path.read_bytes()).hexdigest()


# --- live: python -m Build.pipeline.understand KEY MANIFEST SCENE_ID OUT_DIR LEDGER [VIDEO] ---------------
ENV = Path(r"C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.env")
ROOT = Path(__file__).resolve().parents[2]
MAX_CALLS, MAX_USD = 6, 1.0  # S13e contract cap, counted over the whole ledger file
# shortcut: assumed worst-case tokens per media item (provider tokenization unknown); replace with billed usage.
IMAGE_TOKENS, VIDEO_TOKENS = 3000, 60000


def reserve(body, ledger):
    ledger = Path(ledger)
    try:
        rows = project_ledger(ledger, str(ledger.resolve())) if ledger.exists() else []
    except (OSError, ValueError, KeyError, TypeError):
        raise StageError("SPEND_PAUSED", "Invalid Meta ledger", False) from None
    parts = body["input"][0]["content"]
    media = sum(IMAGE_TOKENS if p["type"] == "input_image" else VIDEO_TOKENS for p in parts if p["type"] != "input_text")
    worst = (len(parts[0]["text"]) // 2 + media) * IN_USD + muse.MAX_OUTPUT_TOKENS * OUT_USD
    spent = sum(liability_usd(r) for r in rows)
    if len(rows) >= MAX_CALLS or spent + usd(worst) > usd(MAX_USD):
        raise StageError("SPEND_PAUSED", f"budget guard: {len(rows)} calls, USD {spent:.4f}, next worst USD {worst:.4f}", False)
    return worst


def live_post(ledger, rid="S13e-orch27"):
    import httpx
    from dotenv import dotenv_values

    def post(body, key):
        try:
            worst = reserve(body, ledger)
            request_id = reserve_meta(ROOT, ledger, "understand", key, worst,
                                      max_calls=MAX_CALLS, cap_usd=MAX_USD)
        except (ReconstructionPaused, OSError, ValueError, KeyError, TypeError):
            raise StageError("SPEND_PAUSED", "Meta admission unavailable or budget paused", False) from None
        env = dotenv_values(ENV)  # key by NAME only; never printed or stored
        started = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        r = httpx.post(env["MODEL_API_BASE_URL"].rstrip("/") + "/responses", json=body, timeout=180,
                       headers={"Authorization": "Bearer " + env["MODEL_API_KEY"], "Idempotency-Key": key})
        ok_json = r.headers.get("content-type", "").startswith("application/json")
        reply = r.json() if ok_json else {"error": r.text[:300]}
        u = reply.get("usage") or {}
        tin, tout = u.get("input_tokens"), u.get("output_tokens")
        est = tin * IN_USD + tout * OUT_USD if tin is not None and tout is not None else worst
        row = {"request_id": request_id, "stage": "understand", "utc": started, "rid": rid, "idempotency_key": key, "provider": "Meta Model API",
               "model": reply.get("model", body["model"]), "http": r.status_code, "input_tokens": tin,
               "output_tokens": tout, "reserved_usd": round(worst, 6), "est_usd": round(est, 6), "billed_usd": None}
        with ledger.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")
        return r.status_code, reply
    return post


if __name__ == "__main__":
    key, manifest, scene_id, out_dir, ledger, *video = sys.argv[1:]
    print(run(key, manifest, scene_id, live_post(Path(ledger)), out_dir, video[0] if video else None))

