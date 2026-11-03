"""N08 room jobs: /internal/workspace/rooms (browser /api/workspace/rooms via the BFF proxy).

GET /rooms -> {rooms: [status...]} owner's jobs newest first; POST /rooms {file_id, project_id?, reference?} -> 202 {job};
background thread runs Build/reconstruction/live_room.
GET /rooms/{id} -> status (+ GPU dot/queue position while reconstructing); GET /rooms/{id}/result -> scene + room;
GET /rooms/{id}/room.ply; POST /rooms/{id}/scale {reference} -> CPU-only rescale of the saved reconstruction.
DELETE /rooms/{id} -> remove an owner's inactive, non-SAMPLE room, keeping its uploaded video.
N42: with the real GPU remote, a finished job runs one automatic lab shell pass (objects.build_shell_files; state
"building lab shell", then status shell done/failed); a rescale keeps and scales the shell (live_room.finish).
Job files: R2S_DATA_DIR/rooms/<owner>/<job_id>/ (status.json, scene.json, room.json, room.ply, mapanything.npz).
N59: done is usable before optional SF3D upgrades finish. Per-object states are in status.shape_upgrades and
result.room.shell.kept[].upgrade; generated meshes keep measured-box physics.
"""
import json
import re
import threading
import time
import uuid
from contextlib import contextmanager

from fastapi import APIRouter, Body, Depends
from fastapi.responses import FileResponse

from Build.api import gpu
from Build.api.storage.files import _default
from Build.api.workspace.auth import error, require_owner
from Build.reconstruction import live_room

_ID = re.compile(r"[0-9a-f]{32}")
ROOM_STARTS_PER_DAY = 3
_active_rooms = set()


@contextmanager
def room_write(d):
    from Build.reconstruction.shape_upgrade import LOCK
    # shortcut: process-local mutation admission, replace with shared leases before using multiple API workers.
    key = str(d.resolve())
    with LOCK:
        if not (d / "status.json").is_file():
            raise error(404, "NOT_FOUND", "room job not found")
        if key in _active_rooms:
            raise error(409, "ROOM_BUSY", "This room is being updated. Try again when it finishes.")
        _active_rooms.add(key)
    try:
        yield
    finally:
        with LOCK:
            _active_rooms.discard(key)


@contextmanager
def _daily_room_limit(counter, day, limit, message, previous=()):
    from Build.reconstruction.shape_upgrade import LOCK
    # shortcut: process-local lock, use a shared lock before adding API worker processes.
    with LOCK:
        count = (json.loads(counter.read_text(encoding="utf-8")) if counter.exists() else
                 {"day": day, "count": sum(c.get("count", 0) for c in previous if c.get("day") == day)})
        used = count.get("count", 0) if count.get("day") == day else 0
        if used >= limit:
            raise error(429, "QUOTA_UPLOADS", message)
        counter.parent.mkdir(parents=True, exist_ok=True)
        next_count = {"day": day, "count": used + 1}
        live_room._write(counter, next_count)
        try:
            yield next_count
        except BaseException:
            live_room._write(counter, count)
            raise


def create_router(store=None, remote=live_room.modal_reconstruct, stats=gpu.modal_stats, shell=None) -> APIRouter:
    db = (lambda: store) if store else _default
    router = APIRouter(prefix="/internal/workspace", dependencies=[Depends(require_owner)])
    if shell is None and remote is live_room.modal_reconstruct:  # N42: auto lab shell; fake-remote tests stay offline
        from Build.api.room.objects import build_shell_files as shell

    def job_dir(owner, job_id):
        d = db().root / "rooms" / owner / job_id
        if (not _ID.fullmatch(job_id) or d.resolve() != db().root.resolve() / "rooms" / owner / job_id
                or not (d / "status.json").exists()):
            raise error(404, "NOT_FOUND", "room job not found")
        return d

    def read(d, name):
        return json.loads((d / name).read_text(encoding="utf-8"))

    @router.delete("/rooms/{job_id}")
    def delete_room(job_id: str, owner: str = Depends(require_owner)):
        from Build.reconstruction.shape_upgrade import LOCK, _running, _PROCESS
        with LOCK:
            d = job_dir(owner, job_id)
            status = read(d, "status.json")
            if status.get("sample"):
                raise error(409, "SAMPLE_ROOM", "Sample rooms can't be deleted")
            room = read(d, "room.json") if (d / "room.json").is_file() else {}
            pending = any(o.get("upgrade", {}).get("state") in ("pending", "queued", "running")
                          for o in room.get("shell", {}).get("kept", []))
            work = read(d, "shape-upgrades.json") if (d / "shape-upgrades.json").is_file() else {}
            queued = work.get("inputs") and work.get("process") == _PROCESS and not work.get("started_at")
            if (status.get("state") not in ("done", "failed", "cancelled") or pending or queued or
                    str(d.resolve()) in _active_rooms or str(d) in _running):
                raise error(409, "ROOM_BUSY", "This room has a queued or running job. Try again when it finishes.")
            target = db().root.resolve() / "rooms" / owner / job_id
            paths = sorted(d.rglob("*"), key=lambda p: len(p.parts), reverse=True)
            # Validate every exact target before removing anything; never follow links into another room or shared pack.
            if d.resolve() != target or any(p.is_symlink() or p.resolve() != target / p.relative_to(d) for p in paths):
                raise error(409, "INVALID_STORAGE", "Room storage contains a linked path and cannot be deleted safely")
            try:
                for path in [p for p in paths if p != d / "status.json"] + [d / "status.json"]:
                    if path.is_dir():
                        path.rmdir()
                    else:
                        path.unlink()
                d.rmdir()
            except OSError:
                raise error(503, "DELETE_FAILED", "Room could not be fully deleted. Try again.") from None
        return {"deleted": job_id, "quota": db().quota(owner)}

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
        reference = ref_of(payload)
        db().check_storage(owner)
        counter = db().root / "rooms" / owner / "room-starts.json"
        with _daily_room_limit(counter, db()._day(), ROOM_STARTS_PER_DAY,
                              f"Daily room limit reached ({ROOM_STARTS_PER_DAY} per day). Try again tomorrow."):
            job_id = uuid.uuid4().hex
            d = counter.parent / job_id
            d.mkdir(parents=True)
            live_room.set_status(d, job_id=job_id, state="queued", file_id=rec["id"], project_id=project_id,
                                 created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
            threading.Thread(target=live_room.run_job, daemon=True,
                             args=(d, db().path(owner, rec["id"]), rec["duration_s"], owner, reference, remote, None,
                                   None, shell)).start()  # positional: tests stub run_job(*a)
        return {"job": read(d, "status.json")}

    @router.get("/rooms/{job_id}")
    def status(job_id: str, owner: str = Depends(require_owner)):
        d = job_dir(owner, job_id)
        s = read(d, "status.json")
        if s["state"] == "done" and (d / "room.json").exists():
            from Build.reconstruction.shape_upgrade import LOCK, fail_interrupted
            with LOCK:
                fail_interrupted(d)
                s["shape_upgrades"] = [{"id": o["id"], **o["upgrade"]}
                                       for o in read(d, "room.json").get("shell", {}).get("kept", []) if "upgrade" in o]
        if s["state"] in ("queued", "sampling", "reconstructing"):
            s["gpu"] = gpu.status(owner, stats())
        return {"job": s}

    @router.get("/rooms/{job_id}/result")
    def result(job_id: str, owner: str = Depends(require_owner)):
        d = job_dir(owner, job_id)
        if read(d, "status.json")["state"] != "done":
            raise error(409, "NOT_READY", "room job is not done")
        if read(d, "status.json").get("sample"):
            from Build.api.storage.sample import ensure_room_archive
            try:
                ensure_room_archive(d)
            except (OSError, ValueError, KeyError):
                raise error(503, "DEPENDENCY_UNAVAILABLE", "public sample archive is unavailable") from None
        from Build.reconstruction.shape_upgrade import LOCK, fail_interrupted
        with LOCK:  # never report the final ready state with the preceding box-only scene
            fail_interrupted(d)
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
            from Build.api.storage.sample import ensure_room_archive
            from Build.reconstruction.shape_upgrade import LOCK
            with room_write(d):
                ensure_room_archive(d)
                with LOCK:
                    out = live_room.finish(d, ref_of(payload))
                live_room.set_status(d, scale=out["room"]["scale"]["status"])
        except (OSError, KeyError):
            raise error(503, "DEPENDENCY_UNAVAILABLE", "room reconstruction archive is unavailable") from None
        except (ValueError, TypeError) as e:
            raise error(422, "INVALID_REFERENCE", str(e)[:300]) from None
        return out

    return router
