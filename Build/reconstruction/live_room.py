"""N08 Mode A live pipeline: room video -> sampled frames -> on-demand MapAnything (Modal r2s-ondemand.reconstruct)
-> floor plane + gravity (S05d RANSAC) -> scale (MEASURED reference, else MODEL-ESTIMATED, else scale unverified)
-> lab-scene-v1 scene.json + gravity-aligned room.ply + room.json in the job folder.

Paid call: L4, then at most one A10G retry for OOM/no capacity, each reserved/settled in daily_cap and queued in the N04 GPU job
table (status dot + queue position). Cost from Build/gpu/cost_log.py rates (estimate, not billed).
"""
import io
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT / "Build/reconstruction/spike", ROOT / "Build/gpu", ROOT):
    sys.path.insert(0, str(_p))
import scene_frame as sf  # noqa: E402  S05d floor RANSAC + known-object scale
from cost_log import cost, scene_log  # noqa: E402
from Build.gpu.image_spec import GPU  # noqa: E402

from Build.api import gpu as gpu_jobs  # noqa: E402
from Build.guardrails import daily_cap  # noqa: E402

APP, FALLBACK_GPU, CPU, MEM_GIB, IDLE_S = "r2s-ondemand", "A10G", 2, 16, 900  # ondemand.py + scene_job resources
# get() timeout covers queue wait + cold start + inference (A10G room jobs measured 31 to 77 s end to end),
# so 120 s would cancel healthy cold L4 starts; 240 s still keeps a capacity stall bounded.
ROOM_START_BUDGET_S = 240
FRAMES, FRAME_W, MAX_POINTS = 8, 512, 20000
A4_LONG_M, A4_SD_M = 0.297, 0.002  # ISO 216 A4 long edge 297 mm, +-2 mm tolerance
# MapAnything output is nominally metric, so a real A4 edge rescales it by about 1. Outside 0.5 to 2 the clicks are not
# on one A4 edge (a 210 mm short-edge click gives 1.41, still inside), so the clicked scale is rejected, not applied.
A4_FACTOR_RANGE = (0.5, 2.0)
CLICK_SD_PX = 2.0  # assumed 1-sigma click error per reference endpoint, on the model grid
ESTIMATE_USD = cost(300 + 240 + IDLE_S, GPU, CPU, MEM_GIB)["total_usd"]  # timeout + startup + idle: worst case


def sample_frames(video, duration_s, n=FRAMES):
    """n evenly spaced PNG frames (bytes), width FRAME_W."""
    out = []
    for i in range(n):
        cmd = ["ffmpeg", "-v", "error", "-ss", f"{duration_s * (i + 0.5) / n:.3f}", "-i", str(video), "-frames:v", "1",
               "-vf", f"scale={FRAME_W}:-2", "-f", "image2pipe", "-c:v", "png", "-"]
        data = subprocess.run(cmd, capture_output=True, check=True, timeout=120).stdout
        if data[:8] != b"\x89PNG\r\n\x1a\n":
            raise ValueError(f"no frame at sample {i}")
        out.append(data)
    return out


def load_views(npz):
    d = np.load(io.BytesIO(npz))
    n = len({k.split("_")[0] for k in d.files if k.startswith("view")})
    if n < 2:
        raise ValueError("need >=2 views")
    return [{"pts_img": d[f"view{i}_pts3d"][0].astype(np.float64), "conf": d[f"view{i}_conf"][0].reshape(-1),
             "mask": d[f"view{i}_mask"][0].reshape(-1) > 0.5, "pose": d[f"view{i}_camera_poses"][0].astype(np.float64),
             "rgb": d[f"view{i}_img_no_norm"][0].reshape(-1, 3),
             "msf": float(d[f"view{i}_metric_scaling_factor"].reshape(-1)[0])
             if f"view{i}_metric_scaling_factor" in d.files else None} for i in range(n)]


def _frame(down, origin, forward):
    """Rows = world axes of the lab frame: +Y up (against gravity), camera mean forward ~ -Z."""
    y = -sf.unit(down)
    z = -sf.unit(forward - (forward @ y) * y)
    return np.stack([np.cross(y, z), y, z]), origin


def scale_of(views, ref):
    """ref {view, p0:[row,col], p1:[row,col], length_m?, length_sd_m?}: no length = A4 long edge."""
    if ref:
        a4 = ref.get("length_m") is None
        r = {"view": ref.get("view"), "p0": ref.get("p0"), "p1": ref.get("p1"),
             "length_m": A4_LONG_M if a4 else float(ref["length_m"]),
             "length_sd_m": A4_SD_M if a4 else float(ref.get("length_sd_m") or 0.0),
             "source": "A4 sheet long edge, ISO 216 297 mm" if a4 else "user-given size"}
        if not r["length_m"] > 0:
            raise ValueError("length_m must be > 0")
        if not all(isinstance(r[k], (list, tuple)) and len(r[k]) == 2 for k in ("p0", "p1")):
            raise ValueError("reference p0 and p1 must be [row, col]")
        r["pixel_sd_rel"] = np.sqrt(2) * CLICK_SD_PX / max(float(np.hypot(*np.subtract(r["p0"], r["p1"]))), 1.0)
        e = sf.known_object_scale(views, r)
        lo, hi = A4_FACTOR_RANGE
        if a4 and not lo <= e["metres_per_model_unit"] <= hi:
            return {**scale_of(views, None), "reference_rejected": {
                "source": "scale from A4 clicks", "metres_per_model_unit": e["metres_per_model_unit"],
                "reason": (f"The two clicks are {e['model_length']:.3g} model units apart, which would rescale the"
                           f" room by {e['metres_per_model_unit']:.3g}x. A real A4 edge (297 mm or 210 mm) should"
                           f" give {lo:g}x to {hi:g}x, so this scale was not applied. Click both ends of one A4 edge.")}}
        return {"status": "MEASURED", "metres_per_model_unit": e["metres_per_model_unit"], "sd": e["sd"],
                "reference": {k: e[k] for k in ("source", "view", "p0", "p1", "length_m", "length_sd_m")}}
    msf = [v["msf"] for v in views]
    if all(m is not None for m in msf):  # spread of MapAnything's own per-view metric factors
        return {"status": "MODEL-ESTIMATED", "metres_per_model_unit": 1.0, "sd": float(np.std(msf) / np.mean(msf)),
                "evidence": "MapAnything metric output; sd = relative spread of per-view metric scaling factors"}
    return {"status": "scale unverified", "metres_per_model_unit": 1.0, "sd": None,
            "evidence": "MapAnything nominal metric output; no reference object and no model scale uncertainty"}


def analyse(npz, ref=None):
    """MapAnything npz bytes -> (aligned points, rgb uint8, room metadata, lab-scene-v1 scene)."""
    views = load_views(npz)
    rng = np.random.default_rng(sf.SEED)
    keep, cols, grids = [], [], []
    for v in views:
        p = v["pts_img"].reshape(-1, 3)
        ok = v["mask"] & np.isfinite(p).all(1)
        if ok.any():
            ok &= v["conf"] >= np.quantile(v["conf"][ok], sf.CONF_QUANTILE)
            keep.append(p[ok])
            cols.append(v["rgb"][ok])
            grids.append((v["pts_img"], ok.reshape(v["pts_img"].shape[:2])))
    if not keep:
        raise ValueError("no valid points")
    pts, rgb = np.concatenate(keep), np.concatenate(cols)
    cams = np.stack([v["pose"][:3, 3] for v in views])
    down = sf.unit(np.mean([v["pose"][:3, 1] for v in views], 0))  # OpenCV: +y image-down, pose cam->world
    forward = sf.unit(np.mean([v["pose"][:3, 2] for v in views], 0))
    sub = pts[rng.choice(len(pts), min(len(pts), 60000), replace=False)]
    # N42: N06 room picked a plane 25 deg off camera-down with 10% of points under it (inliers 3.9%); a floor has
    # nothing under it, so 1% support + at most 2% of points below finds the real, sparsely seen floor.
    floor = sf.fit_floor(sub, down, cams, rng, sf.local_triplets(grids, rng), min_support=0.01, max_below=0.02)
    c = cams.mean(0)
    if floor:
        n = floor["normal_down"]
        rot, origin = _frame(n, c + ((floor["origin"] - c) @ n) * n, forward)
        gravity = {"status": "MODEL-ESTIMATED", "method": "RANSAC floor plane normal (S05d)",
                   "uncertainty_deg": round(floor["normal_bootstrap_std_deg"], 4),
                   "angle_to_camera_down_deg": round(sf.angle_deg(n, down), 3)}
        floor_out = {"status": "FIT", **{k: round(float(floor[k]), 6) for k in
                     ("inliers", "inlier_fraction", "rms_residual", "p95_abs_residual", "normal_bootstrap_std_deg")}}
    else:  # no floor: provisional down = mean camera down, floor at the 98th percentile depth along it
        rot, origin = _frame(down, c + np.percentile((pts - c) @ down, 98) * down, forward)
        gravity = {"status": "unverified", "method": "mean camera-down prior; no floor plane found",
                   "uncertainty_deg": None}
        floor_out = {"status": "ABSTAIN", "reason": "no plane below all cameras within the camera-down prior"}
    scale = scale_of(views, ref)
    k = scale["metres_per_model_unit"]
    aligned = (pts - origin) @ rot.T * k
    idx = rng.permutation(len(aligned))[:MAX_POINTS]
    room = {"schema": "n08-room/1", "views": len(views), "points": int(len(idx)), "floor": floor_out,
            "gravity": gravity, "scale": scale,
            "labels": {"input": "RECORDED", "geometry": "MODEL-ESTIMATED (MapAnything)", "scale": scale["status"]},
            "camera_positions_m": np.round((cams - origin) @ rot.T * k, 4).tolist(),
            "model_grid_hw": list(views[0]["pts_img"].shape[:2])}
    scene = {"version": "lab-scene-v1", "label": "SIMULATED", "units": "m", "gravity": [0, -9.81, 0],
             "room": {"kind": "ply", "floor_y": 0, "source": "room.ply", "scale_verified": scale["status"] == "MEASURED"},
             "objects": []}
    return aligned[idx], np.clip(rgb[idx] * 255 + 0.5, 0, 255).astype(np.uint8), room, scene


def _write(path, obj):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, indent=1) + "\n", encoding="utf-8")
    for attempt in range(40):  # Windows refuses replace while a poller has the file open; Linux never does
        try:
            return os.replace(tmp, path)
        except PermissionError:
            if attempt == 39:
                raise
            time.sleep(0.05)


def finish(job_dir, ref=None):
    """CPU only: saved mapanything.npz -> room.ply, room.json, scene.json (rerun with a new reference = rescale).
    N42: a rescale keeps the scene objects (lab shell, clicked objects) scaled about the floor origin by new/old
    metres per model unit; only when the floor fit is unchanged (same frame), else they are dropped with the reason."""
    from scene_job import write_ply
    job_dir = Path(job_dir)
    old = {n: json.loads((job_dir / n).read_text(encoding="utf-8")) for n in ("room.json", "scene.json") if (job_dir / n).exists()}
    pts, rgb, room, scene = analyse((job_dir / "mapanything.npz").read_bytes(), ref)
    objs = old.get("scene.json", {}).get("objects", [])
    if objs and old.get("room.json", {}).get("floor") == room["floor"]:
        f = room["scale"]["metres_per_model_unit"] / old["room.json"]["scale"]["metres_per_model_unit"]
        scene["objects"] = [{**o, "position": [round(x * f, 4) for x in o["position"]],
                             "size": [round(x * f, 4) for x in o["size"]]} for o in objs]
        if "shell" in old["room.json"]:
            sh = old["room.json"]["shell"]
            room["shell"] = {**sh, "rescaled_by": round(f, 6), "labels": {**sh["labels"], "scale": room["scale"]["status"]},
                             "kept": [{**k, "size_m": [round(x * f, 4) for x in k["size_m"]]} for k in sh["kept"]],
                             "rescale_note": "wall and opening numbers are from before the rescale; multiply by rescaled_by"}
    elif objs:
        room["objects_dropped"] = f"{len(objs)} scene objects dropped: the floor fit changed, rebuild the lab shell"
    write_ply(job_dir / "room.ply", np.round(pts, 5), rgb)
    _write(job_dir / "room.json", room)
    _write(job_dir / "scene.json", scene)
    return {"scene": scene, "room": room}


def set_status(job_dir, **fields):
    path = Path(job_dir) / "status.json"
    old = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    _write(path, {**old, **fields, "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})


def modal_reconstruct(frames, gpu=GPU):
    import modal
    fn = modal.Function.from_name(APP, "reconstruct")
    if gpu != GPU:
        fn = fn.with_options(gpu=gpu)
    call = fn.spawn(frames)
    try:
        return call.get(timeout=ROOM_START_BUDGET_S if gpu == GPU else 300 + 240)
    except (TimeoutError, modal.exception.TimeoutError):
        call.cancel(terminate_containers=True)  # cancel first, so the retry cannot overlap this input
        if gpu == GPU:
            raise RuntimeError(f"no GPU capacity/result within {ROOM_START_BUDGET_S}s on {gpu}") from None
        raise


def retry_on_a10g(error):
    """Only GPU OOM/capacity failures, never auth, input, timeout or arbitrary model errors."""
    message = str(error).lower()
    return (type(error).__name__ == "OutOfMemoryError"
            or any(s in message for s in ("cuda out of memory", "cuda error: out of memory",
                                          "no gpu capacity", "no capacity", "insufficient gpu capacity")))


def run_job(job_dir, video, duration_s, owner, ref=None, remote=modal_reconstruct, gpu_db=None, cap_db=None, after=None):
    """Background job; each GPU attempt joins the shared queue with its own cap reservation.
    after(job_dir) (N42): one automatic lab shell pass (its paid calls are ledgered inside); a failure keeps the room."""
    job_dir = Path(job_dir)
    attempts = []
    try:
        set_status(job_dir, state="sampling")
        frames = sample_frames(video, duration_s)
        for device in (GPU, FALLBACK_GPU):
            estimate = cost(300 + 240 + IDLE_S, device, CPU, MEM_GIB)["total_usd"]
            rid = daily_cap.reserve("Modal", estimate, f"N30 room {job_dir.name} {device}", path=cap_db)
            call, log, jid, started = time.time(), None, None, False
            attempt = {"gpu": device, "reservation_id": rid}
            attempts.append(attempt)
            try:
                jid = gpu_jobs.enqueue(owner, "reconstruct", gpu_db, reservation=rid, cap_db=cap_db)
                set_status(job_dir, state="reconstructing", gpu_job=jid, frames=len(frames))
                gpu_jobs.start(jid, gpu_db)
                started, call = True, time.time()
                r = remote(frames) if device == GPU else remote(frames, gpu=device)
                log = scene_log(APP, call, time.time(), r, r.get("gpu", device), CPU, MEM_GIB, IDLE_S)
                attempt["state"] = "done"
            except Exception as e:
                attempt.update(state="failed", error=f"{type(e).__name__}: {e}"[:300])
                if device != GPU or not retry_on_a10g(e):
                    raise
            finally:  # conservative: includes each GPU pool's own 15 minute idle window, also on failure
                try:
                    actual = 0
                    if started:
                        actual = (log["cost"]["upper_bound"]["total_usd"] if log else
                                  cost(time.time() - call + IDLE_S, device, CPU, MEM_GIB)["total_usd"])
                    try:
                        daily_cap.settle(rid, actual, path=cap_db)
                    except ValueError:  # already settled by the reaper: never charge twice
                        pass
                    attempt.update(estimated_usd=actual, wall_s=round(time.time() - call, 3))
                    set_status(job_dir, gpu_attempts=attempts)
                finally:
                    if jid:
                        gpu_jobs.finish(jid, gpu_db)
            if log:
                break
        (job_dir / "mapanything.npz").write_bytes(r["npz"])
        _write(job_dir / "cost-log.json", log)
        out = finish(job_dir, ref)
        shell = {}
        if after:
            set_status(job_dir, state="building lab shell")
            try:
                after(job_dir)
                shell = {"shell": "done"}
            except Exception as e:  # noqa: BLE001  the room is still usable; the Build lab shell button retries
                shell = {"shell": "failed", "shell_error": f"{type(e).__name__}: {e}"[:300]}
        set_status(job_dir, state="done", timing_s=log["timing_s"], gpu=log["gpu"],
                   peak_allocated_bytes=r.get("peak_allocated_bytes"), gpu_name=r.get("gpu_name"),
                   estimated_usd=round(sum(a["estimated_usd"] for a in attempts), 8),
                   scale=out["room"]["scale"]["status"], gravity=out["room"]["gravity"]["status"], **shell)
    except daily_cap.CapExceeded as e:
        set_status(job_dir, state="failed", code="DAILY_CAP", error=str(e)[:300])
    except Exception as e:  # noqa: BLE001  the poller must see the failure, not a stuck job
        set_status(job_dir, state="failed", code="ERROR", error=f"{type(e).__name__}: {e}"[:300])
