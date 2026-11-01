"""N14: POST /internal/workspace/rooms/{id}/objects {view, point:[row, col]} (browser /api/workspace/rooms/... via BFF).

Click on a done room job's view image (GET .../views/{view}.png, model grid pixels) -> hosted SAM 3.1 box ->
box proxy (Build/reconstruction/object_lift.py) -> appended to the job's scene.json as a fixed "block".
Labels: geometry MODEL-ESTIMATED; scale from room.json (MEASURED, MODEL-ESTIMATED or scale unverified).
N31: optional "category" (object_lift.CATEGORIES, default "other") sets fixed/mass/friction (MODEL-ESTIMATED). The object's
RGBA cut-out goes to Stable Fast 3D (Build/gpu/sf3d.py, L4, daily_cap); the mesh (GLB at GET .../objects/{id}.glb) is the
object's shape and collider. On any SF3D failure the measured box stays, with the reason in shape.fallback_reason.
"""
import json
import time

from fastapi import APIRouter, Body, Depends
from fastapi.responses import Response

from Build.api.room import _ID
from Build.api.storage.files import _default
from Build.api.workspace.auth import error, require_owner
from Build.gpu import sf3d
from Build.guardrails import daily_cap
from Build.reconstruction import live_room, object_lift


def create_router(store=None, segment=object_lift.sam_box, generate=sf3d.generate_remote) -> APIRouter:
    db = (lambda: store) if store else _default
    router = APIRouter(prefix="/internal/workspace", dependencies=[Depends(require_owner)])

    def done_dir(owner, job_id):
        d = db().root / "rooms" / owner / job_id
        if not _ID.fullmatch(job_id) or not (d / "status.json").exists():
            raise error(404, "NOT_FOUND", "room job not found")
        if json.loads((d / "status.json").read_text(encoding="utf-8"))["state"] != "done":
            raise error(409, "NOT_READY", "room job is not done")
        return d

    @router.get("/rooms/{job_id}/views/{view}.png")
    def view_image(job_id: str, view: int, owner: str = Depends(require_owner)):
        try:
            png, _, _ = object_lift.view_png((done_dir(owner, job_id) / "mapanything.npz").read_bytes(), view)
        except ValueError as e:
            raise error(422, "INVALID_INPUT", str(e)[:300]) from None
        return Response(png, media_type="image/png", headers={"cache-control": "no-store"})

    @router.get("/rooms/{job_id}/objects/{object_id}.glb")
    def object_glb(job_id: str, object_id: str, owner: str = Depends(require_owner)):
        f = done_dir(owner, job_id) / "objects" / f"{object_id}.glb"
        if not object_id.startswith("room-object-") or not object_id[12:].isdigit() or not f.exists():
            raise error(404, "NOT_FOUND", "object mesh not found")
        return Response(f.read_bytes(), media_type="model/gltf-binary", headers={"cache-control": "no-store"})

    @router.post("/rooms/{job_id}/objects")
    def add_object(job_id: str, payload: dict = Body(...), owner: str = Depends(require_owner)):
        d = done_dir(owner, job_id)
        view, point = payload.get("view"), payload.get("point")
        category = payload.get("category", "other")
        if category not in object_lift.CATEGORIES:
            raise error(422, "INVALID_INPUT", "category must be one of " + ", ".join(object_lift.CATEGORIES))
        if not (isinstance(point, list) and len(point) == 2 and all(isinstance(x, (int, float)) for x in point)):
            raise error(422, "INVALID_INPUT", "point must be [row, col] on the view image")
        npz = (d / "mapanything.npz").read_bytes()
        try:
            png, w, h = object_lift.view_png(npz, view)
            if not (0 <= point[0] < h and 0 <= point[1] < w):
                raise ValueError(f"point must be [row, col] inside {h}x{w}")
        except ValueError as e:
            raise error(422, "INVALID_INPUT", str(e)[:300]) from None
        try:
            box, _ = segment(png, point, w, h)
        except daily_cap.CapExceeded as e:
            raise error(429, "DAILY_CAP", str(e)[:300]) from None
        except (RuntimeError, ValueError, KeyError, OSError) as e:
            raise error(502, "SEGMENTATION_FAILED", str(e)[:300]) from None
        room = json.loads((d / "room.json").read_text(encoding="utf-8"))
        try:
            proxy = object_lift.lift(npz, view, point, box, room)
        except ValueError as e:
            raise error(422, "NO_OBJECT_POINTS", str(e)[:300]) from None
        scene, obj = object_lift.to_scene(json.loads((d / "scene.json").read_text(encoding="utf-8")), proxy,
                                          category=category)
        gen = {}
        try:  # SF3D shape; any failure keeps the measured box and says why
            gen = generate(object_lift.crop_rgba(npz, view, box, proxy["mask"]))
            turns, verts, idx = object_lift.fit_mesh(gen["vertices"], gen["faces"], proxy)
            (d / "objects").mkdir(exist_ok=True)
            (d / "objects" / f"{obj['id']}.glb").write_bytes(gen["glb"])
            obj["shape"] = object_lift.mesh_shape(category, f"/api/workspace/rooms/{job_id}/objects/{obj['id']}.glb",
                                                  turns, verts, idx)
        except daily_cap.CapExceeded as e:
            obj["shape"] = {"type": "box", "fallback_reason": f"SF3D skipped: daily GPU cap ({e})"[:300]}
        except Exception as e:  # noqa: BLE001  shape is optional: the box is the documented fallback
            obj["shape"] = {"type": "box", "fallback_reason": f"SF3D failed: {type(e).__name__}: {e}"[:300]}
        record = {**obj, "view": view, "point": point, "sam_box": [int(x) for x in box], "size_sd_m": proxy["size_sd"],
                  "points": proxy["points"], "sam_cost_usd": object_lift.USD_PER_IMAGE,
                  "sf3d": {k: gen.get(k) for k in ("gpu", "gpu_name", "wall_s", "model_load_s", "inference_s",
                                                  "peak_allocated_bytes", "estimated_usd")} if gen else None,
                  "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                  "labels": {"geometry": "MODEL-ESTIMATED (SAM 3.1 box + MapAnything points, measured box)",
                             "shape": ("MODEL-GENERATED shape, Powered by Stability AI (Stable Fast 3D), fitted to the box"
                                       if obj["shape"]["type"] == "mesh" else "box fallback"),
                             "mass_friction": f"MODEL-ESTIMATED from category {category}",
                             "scale": room["scale"]["status"],
                             "caveat": "visible surface only; the hidden back is not observed, so depth size is a lower bound"}}
        live_room._write(d / "scene.json", scene)
        f = d / "objects.json"
        live_room._write(f, [*(json.loads(f.read_text(encoding="utf-8")) if f.exists() else []), record])
        return {"object": record, "scene": scene}

    return router
