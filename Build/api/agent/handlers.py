"""N07 real agent tool handlers (owner, args) -> JSON: list_files, start_experiment_track, fit by trajectory id;
N21 start_room_build -> the N08 POST /internal/workspace/rooms endpoint (same store, validation and GPU queue)."""
import functools

from fastapi import HTTPException

from Build.agent import core
from Build.api import experiment
from Build.api.storage.files import _default as _store


def _safe(fn):
    def wrapped(owner, args):
        try:
            return fn(owner, args)
        except HTTPException as exc:  # 404/422 from the store: give the model the code, not a traceback
            d = exc.detail if isinstance(exc.detail, dict) else {}
            return {"status": "error", "error": {"code": d.get("code", "ERROR"), "detail": d.get("message", "")}}
    return wrapped


@_safe
def list_files(owner, args):
    files = _store().list(owner)[:50]
    return {"status": "ok", "files": [{k: f[k] for k in ("id", "name", "media_type", "duration_s", "project_id")}
                                      for f in files]}


@_safe
def start_experiment_track(owner, args):
    e = experiment.start(_store(), owner, {"file_id": args["file_id"], "target_text": args["target"]})["experiment"]
    return {"status": e["status"], "trajectory_id": e["id"], "project_id": e["project_id"],
            "detail": "tracking runs in the background; call fit with this trajectory_id when it is done"}


@_safe
def fit(owner, args):
    if "trajectory_id" not in args:
        return core.DEFAULT_HANDLERS["fit"](owner, args)  # simulated lab arrays keep the N05 path
    return experiment.refit(_store(), owner, args["trajectory_id"])


@functools.cache
def _room_start():
    from Build.api import room  # reuse the route body instead of duplicating its checks
    return next(r.endpoint for r in room.create_router().routes if r.path.endswith("/rooms") and "POST" in r.methods)


@_safe
def start_room_build(owner, args):
    job = _room_start()({"file_id": args["file_id"]}, owner)["job"]
    return {"status": job["state"], "room_job_id": job["job_id"], "project_id": job.get("project_id"),
            "detail": "room reconstruction runs in the background on the GPU queue; the workspace shows progress"}


HANDLERS = {"list_files": list_files, "start_experiment_track": start_experiment_track, "fit": fit,
            "start_room_build": start_room_build}

