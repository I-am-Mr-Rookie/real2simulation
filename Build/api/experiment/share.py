"""N16 Guess the Gravity: owner shares one finished experiment as a public, clip-free challenge.

Owner (BFF /api/workspace/experiments/<id>/share): POST create, DELETE revoke. Public (BFF /api/guess/<token>):
GET replay without the answer, POST reveal {guess}. The share row copies only the trajectory, the fitted quantity and
its labels: no file id, no video, no user id or name. Token = 192 random bits, revoked rows answer 404.
"""
import json
import math
import secrets

from fastapi import APIRouter, Body, Depends

from Build.api.experiment import get as get_experiment
from Build.api.storage.files import _default
from Build.api.workspace.auth import error, require_owner

_SCHEMA = ("CREATE TABLE IF NOT EXISTS guess_shares (token TEXT PRIMARY KEY, user TEXT NOT NULL,"
           " experiment_id TEXT NOT NULL, payload TEXT NOT NULL, created TEXT NOT NULL, revoked TEXT)")
_TOKEN_LEN = 32  # token_urlsafe(24)


def _now(store):
    return store.now().strftime("%Y-%m-%dT%H:%M:%SZ")


def create(store, owner, experiment_id):
    store.db.execute(_SCHEMA)
    e = get_experiment(store, owner, experiment_id)["experiment"]  # 404 for other users' experiments
    res = e["result"] or {}
    q, traj = res.get("quantity"), res.get("trajectory")
    if e["status"] != "done" or not q or not traj or q.get("unit") != "m/s^2" or traj.get("unit") != "m":
        raise error(422, "NOT_SHAREABLE",
                    "only a finished experiment with a measured acceleration in m/s^2 (known size given) can be shared")
    row = store.db.execute("SELECT token FROM guess_shares WHERE user=? AND experiment_id=? AND revoked IS NULL",
                           (owner, e["id"])).fetchone()
    if row:
        return {"token": row["token"], "path": f"/guess/{row['token']}"}
    payload = {"trajectory": {k: traj[k] for k in ("axes", "unit", "t_s", "x", "y")}, "motion": res.get("motion"),
               "quantity": {k: q.get(k) for k in ("name", "value", "unit", "uncertainty", "label")},
               "label": res.get("label")}
    token = secrets.token_urlsafe(24)
    with store.lock:
        store.db.execute("INSERT INTO guess_shares VALUES (?,?,?,?,?,NULL)",
                         (token, owner, e["id"], json.dumps(payload), _now(store)))
    return {"token": token, "path": f"/guess/{token}"}


def revoke(store, owner, experiment_id):
    store.db.execute(_SCHEMA)
    get_experiment(store, owner, experiment_id)
    with store.lock:
        n = store.db.execute("UPDATE guess_shares SET revoked=? WHERE user=? AND experiment_id=? AND revoked IS NULL",
                             (_now(store), owner, str(experiment_id))).rowcount
    return {"revoked": n}


def _share(store, token):
    store.db.execute(_SCHEMA)
    row = (store.db.execute("SELECT payload FROM guess_shares WHERE token=? AND revoked IS NULL", (token,)).fetchone()
           if isinstance(token, str) and len(token) == _TOKEN_LEN else None)
    if not row:
        raise error(404, "NOT_FOUND", "this challenge does not exist or was withdrawn")
    return json.loads(row["payload"])


def public_view(store, token):
    p = _share(store, token)
    return {"title": "Guess the Gravity", "trajectory": p["trajectory"], "motion": p["motion"],
            "question": "What vertical acceleration (g, in m/s^2) does this object have?"}


def reveal(store, token, guess):
    p = _share(store, token)
    if not isinstance(guess, (int, float)) or isinstance(guess, bool) or not math.isfinite(guess) or not 0 <= guess <= 1000:
        raise error(422, "INVALID_INPUT", "guess must be a number between 0 and 1000 (m/s^2)")
    q = p["quantity"]
    return {"guess": guess, "difference": guess - q["value"], "quantity": q, "label": p["label"],
            "note": "Measured from video by a fitter, not a calibrated instrument; scale comes from a size the owner stated."}


def create_router(store=None) -> APIRouter:
    db = (lambda: store) if store else _default
    router = APIRouter()

    @router.post("/internal/workspace/experiments/{experiment_id}/share", status_code=201)
    def share(experiment_id: str, owner: str = Depends(require_owner)):
        return create(db(), owner, experiment_id)

    @router.delete("/internal/workspace/experiments/{experiment_id}/share")
    def unshare(experiment_id: str, owner: str = Depends(require_owner)):
        return revoke(db(), owner, experiment_id)

    @router.get("/public/guess/{token}")
    def view(token: str):
        return public_view(db(), token)

    @router.post("/public/guess/{token}/reveal")
    def show(token: str, payload: dict = Body(...)):
        return reveal(db(), token, payload.get("guess"))

    return router
