"""N08 room jobs: /internal/workspace/rooms (browser /api/workspace/rooms via the BFF proxy).

GET /rooms -> {rooms: [status...]} owner's jobs newest first; POST /rooms {file_id, project_id?, reference?} -> 202 {job};
background thread runs Build/reconstruction/live_room.
GET /rooms/{id} -> status (+ GPU dot/queue position while reconstructing); GET /rooms/{id}/result -> scene + room;
GET /rooms/{id}/room.ply; POST /rooms/{id}/scale {reference} -> CPU-only rescale of the saved reconstruction.
N42: with the real GPU remote, a finished job runs one automatic lab shell pass (objects.build_shell_files; state
"building lab shell", then status shell done/failed); a rescale keeps and scales the shell (live_room.finish).
Job files: R2S_DATA_DIR/rooms/<owner>/<job_id>/ (status.json, scene.json, room.json, room.ply, mapanything.npz).
"""
import json
import re
import threading
import time
import uuid

from fastapi import APIRouter, Body, Depends
from fastapi.responses import FileResponse

from Build.api import gpu
from Build.api.storage.files import _default
from Build.api.workspace.auth import error, require_owner
from Build.reconstruction import live_room

_ID = re.compile(r"[0-9a-f]{32}")


def create_router(store=None, remote=live_room.modal_reconstruct, stats=gpu.modal_stats, shell=None) -> APIRouter:
    db = (lambda: store) if store else _default
    router = APIRouter(prefix="/internal/workspace", dependencies=[Depends(require_owner)])
    if shell is None and remote is live_room.modal_reconstruct:  # N42: auto lab shell; fake-remote tests stay offline
        from Build.api.room.objects import build_shell_files as shell

    def job_dir(owner, job_id):
        d = db().root / "rooms" / owner / job_id
        if not _ID.fullmatch(job_id) or not (d / "status.json").exists():
            raise error(404, "NOT_FOUND", "room job not found")
        return d

    def read(d, name):
        return json.loads((d / name).read_text(encoding="utf-8"))

    def ref_of(payload):
        ref = payload.get("reference")
        if ref is not None and not isinstance(ref, dict):
            raise error(422, "INVALID_INPUT", "reference must be an object")
        return ref

    # shortcut: in-process thread; a server restart marks nothing failed, upgrade to a worker queue if jobs get lost
    @router.get("/rooms")
    def list_rooms(owner: str = Depends(require_owner)):
        base = db().root / "rooms" / owner
        jobs = [read(d, "status.json") for d in (base.iterdir() if base.is_dir() else ())
                if _ID.fullmatch(d.name) and (d / "status.json").exists()]
        jobs.sort(key=lambda s: s.get("created_at") or s.get("updated_at") or "", reverse=True)
        return {"rooms": [{**s, "id": s.get("job_id")} for s in jobs]}

    @router.post("/rooms", status_code=202)
    def start(payload: dict = Body(...), owner: str = Depends(require_owner)):
        rec = db().get(owner, str(payload.get("file_id", "")))
        if not rec["media_type"].startswith("video/") or not rec["duration_s"]:
            raise error(415, "UNSUPPORTED_MEDIA", "room jobs need an uploaded video")
        project_id = payload.get("project_id") or rec["project_id"]
        if project_id is not None:
            db().project(owner, str(project_id))
        job_id = uuid.uuid4().hex
        d = db().root / "rooms" / owner / job_id
        d.mkdir(parents=True)
        live_room.set_status(d, job_id=job_id, state="queued", file_id=rec["id"], project_id=project_id,
                             created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        threading.Thread(target=live_room.run_job, daemon=True,
                         args=(d, db().path(owner, rec["id"]), rec["duration_s"], owner, ref_of(payload), remote, None,
                               None, shell)).start()  # positional: tests stub run_job(*a)
        return {"job": read(d, "status.json")}

    @router.get("/rooms/{job_id}")
    def status(job_id: str, owner: str = Depends(require_owner)):
        s = read(job_dir(owner, job_id), "status.json")
        if s["state"] in ("queued", "sampling", "reconstructing"):
            s["gpu"] = gpu.status(owner, stats())
        return {"job": s}

    @router.get("/rooms/{job_id}/result")
    def result(job_id: str, owner: str = Depends(require_owner)):
        d = job_dir(owner, job_id)
        if read(d, "status.json")["state"] != "done":
            raise error(409, "NOT_READY", "room job is not done")
        return {"scene": read(d, "scene.json"), "room": read(d, "room.json")}

    @router.get("/rooms/{job_id}/room.ply")
    def room_ply(job_id: str, owner: str = Depends(require_owner)):
        d = job_dir(owner, job_id)
        if not (d / "room.ply").exists():
            raise error(409, "NOT_READY", "room job is not done")
        return FileResponse(d / "room.ply", media_type="text/plain", headers={"cache-control": "no-store"})

    @router.post("/rooms/{job_id}/scale")
    def rescale(job_id: str, payload: dict = Body(...), owner: str = Depends(require_owner)):
        d = job_dir(owner, job_id)
        if read(d, "status.json")["state"] != "done":
            raise error(409, "NOT_READY", "room job is not done")
        try:
            out = live_room.finish(d, ref_of(payload))
        except (ValueError, TypeError) as e:
            raise error(422, "INVALID_REFERENCE", str(e)[:300]) from None
        live_room.set_status(d, scale=out["room"]["scale"]["status"])
        return out

    return router
