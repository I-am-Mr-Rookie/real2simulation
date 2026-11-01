"""N07 Mode B experiments: POST/GET /internal/workspace/experiments (browser: /api/workspace/experiments).

POST {file_id, target_text | point {x, y} (frame-0 source pixels), known_size?, project_id?} queues one background
job: Build/pipeline/live_experiment.run on the user's N03 file (hosted SAM 3.1, daily-cap reserved). One worker
thread, so one paid tracking call at a time. Rows live in the N03 SQLite database (experiments table, no Redis)
and every experiment is attached to an N03 project (given, the file's, or a new experiment project).
"""
import json
import uuid
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, Body, Depends

from Build.api.storage.files import _default
from Build.api.workspace.auth import error, require_owner
from Build.guardrails.daily_cap import CapExceeded
from Build.pipeline import live_experiment

_SCHEMA = ("CREATE TABLE IF NOT EXISTS experiments (id TEXT PRIMARY KEY, user TEXT NOT NULL, project_id TEXT NOT NULL,"
           " file_id TEXT NOT NULL, status TEXT NOT NULL, request TEXT NOT NULL, result TEXT, error TEXT,"
           " created TEXT NOT NULL, updated TEXT NOT NULL)")
_POOL = ThreadPoolExecutor(max_workers=1)
_submit = _POOL.submit  # shortcut: jobs running at a server restart stay 'running'; add a startup sweep if seen


def _now(store):
    return store.now().strftime("%Y-%m-%dT%H:%M:%SZ")


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and 0 <= v < 100_000


def start(store, owner, payload, run=None, submit=None):
    p = payload if isinstance(payload, dict) else {}
    text, point, size = p.get("target_text"), p.get("point"), p.get("known_size")
    has_text = isinstance(text, str) and 0 < len(text.strip()) <= 80
    has_point = isinstance(point, dict) and _num(point.get("x")) and _num(point.get("y"))
    if has_text == has_point or (text is not None and not has_text) or (point is not None and not has_point):
        raise error(422, "INVALID_INPUT", "give exactly one of target_text (1 to 80 characters) or point {x, y}")
    if size is not None and not (isinstance(size, str) and len(size) <= 200):
        raise error(422, "INVALID_INPUT", "known_size must be text such as 'ball diameter 6.5 cm'")
    file = store.get(owner, str(p.get("file_id") or ""))
    if not file["media_type"].startswith("video/"):
        raise error(422, "INVALID_INPUT", "experiments need a video file")
    project_id = p.get("project_id") or file["project_id"]
    if project_id:
        project_id = store.project(owner, str(project_id))["id"]
    else:
        project_id = uuid.uuid4().hex
        with store.lock:
            store.db.execute("INSERT INTO projects (id, user, mode, title, created) VALUES (?,?,?,?,?)",
                             (project_id, owner, "experiment", f"Experiment: {file['name']}"[:120], _now(store)))
    req = {"file_id": file["id"], "target_text": text.strip() if has_text else None,
           "point": [point["x"], point["y"]] if has_point else None, "known_size": size}
    eid = uuid.uuid4().hex
    with store.lock:
        store.db.execute(_SCHEMA)
        store.db.execute("INSERT INTO experiments VALUES (?,?,?,?,?,?,NULL,NULL,?,?)",
                         (eid, owner, project_id, file["id"], "queued", json.dumps(req), _now(store), _now(store)))
    (submit or _submit)(_job, store, owner, eid, req, run or live_experiment.run)
    return get(store, owner, eid)


def _set(store, eid, status, result=None, err=None):
    with store.lock:
        store.db.execute("UPDATE experiments SET status=?, result=?, error=?, updated=? WHERE id=?",
                         (status, result and json.dumps(result), err and json.dumps(err), _now(store), eid))


def _job(store, owner, eid, req, run):
    _set(store, eid, "running")
    try:
        result = run(store.path(owner, req["file_id"]), req["target_text"],
                     tuple(req["point"]) if req["point"] else None, req["known_size"])
        _set(store, eid, "done", result=result)
    except CapExceeded:
        _set(store, eid, "failed", err={"code": "CAP_EXCEEDED", "message": "daily paid-call cap reached; no call made"})
    except ValueError as exc:  # unreadable video, frame mismatch, unparsable tracker reply
        _set(store, eid, "failed", err={"code": "UNPROCESSABLE", "message": str(exc)[:300]})
    except Exception as exc:  # tracker down; RuntimeError text is our own status-only message
        msg = str(exc)[:200] if isinstance(exc, RuntimeError) else type(exc).__name__
        _set(store, eid, "failed", err={"code": "TRACKER_UNAVAILABLE", "message": msg})


def _row(r):
    return {"id": r["id"], "project_id": r["project_id"], "file_id": r["file_id"], "status": r["status"],
            "request": json.loads(r["request"]), "result": r["result"] and json.loads(r["result"]),
            "error": r["error"] and json.loads(r["error"]), "created": r["created"], "updated": r["updated"]}


def get(store, owner, eid):
    # N25 F9: the job thread writes on this same shared connection; reading outside the lock raced it (404/500 polls)
    with store.lock:
        store.db.execute(_SCHEMA)
        row = store.db.execute("SELECT * FROM experiments WHERE id=? AND user=?", (str(eid), owner)).fetchone()
    if not row:
        raise error(404, "NOT_FOUND", "experiment not found")
    return {"experiment": _row(row)}


def _list_row(r):
    """List rows drop the heavy result; the seeded sample keeps its SAMPLE / RECORDED label so it is never a bare hash."""
    row = {**_row(r), "result": None, "sample": None}
    if r["file_id"] == "sample" and r["result"]:
        s = json.loads(r["result"]).get("sample") or {}
        row["sample"] = {"label": s.get("label"), "source": s.get("source"), "title": "SAMPLE (RECORDED): falling apple"}
    return row


def refit(store, owner, eid, known_size=None, segment=None):
    """Re-run scale + fitter on a stored track (no new SAM call, no spend); summary without the arrays."""
    e = get(store, owner, eid)["experiment"]
    if e["status"] != "done" or not (e["result"] or {}).get("track"):
        return {"status": e["status"], "trajectory_id": e["id"], "error": e["error"],
                "detail": "tracking has not finished, so there is nothing to fit yet"}
    out = live_experiment.analyse(e["result"]["track"], known_size or e["request"]["known_size"], segment)
    out.pop("trajectory", None)
    return {**out, "trajectory_id": e["id"]}


def create_router(store=None, run=None, submit=None) -> APIRouter:
    db = (lambda: store) if store else _default  # same lazy N03 store as the files router
    router = APIRouter(prefix="/internal/workspace", dependencies=[Depends(require_owner)])

    @router.post("/experiments", status_code=202)
    def start_experiment(payload: dict = Body(...), owner: str = Depends(require_owner)):
        return start(db(), owner, payload, run, submit)

    @router.get("/experiments")
    def list_experiments(project_id: str | None = None, owner: str = Depends(require_owner)):
        with db().lock:
            db().db.execute(_SCHEMA)
            rows = db().db.execute("SELECT * FROM experiments WHERE user=? AND (? IS NULL OR project_id=?)"
                                   " ORDER BY created DESC, id", (owner, project_id, project_id)).fetchall()
        return {"experiments": [_list_row(r) for r in rows]}

    @router.get("/experiments/{experiment_id}")
    def get_experiment(experiment_id: str, owner: str = Depends(require_owner)):
        return get(db(), owner, experiment_id)

    return router

