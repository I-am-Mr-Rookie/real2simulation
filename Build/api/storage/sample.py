"""N11: one labelled SAMPLE project per user, seeded on their first files/projects list.

Recorded results only, from committed evidence: the RM04 room reconstruction (Pexels clip, display bytes baked into
the api image by infra/railway/dev/stage.py) and the ST03 falling-apple experiment (evidence/N07). No video bytes.
"""
import hashlib
import json
import logging
import re
import shutil
import time
import uuid
from pathlib import Path

from fastapi import Depends, Request

from Build.api.workspace.auth import require_owner

ROOT = Path(__file__).resolve().parents[3]
BUNDLE = ROOT / "evidence/S13l/reconstruct/bundle"
MANIFEST = ROOT / "Build/pipeline/recorded/RM04-S13l-mapanything.json"
EXPERIMENT = ROOT / "evidence/N07/live-st03.json"
TITLE = "SAMPLE (RECORDED): classroom room and falling apple"
_NOTE = "SAMPLE / RECORDED: stock Pexels clips analysed earlier; not your video and not a new measurement."


def _room(root, owner, project_id, bundle, manifest):
    """Write a done room job from the recorded RM04 display bundle; None when the bytes are absent or not the recorded ones."""
    try:
        listed = json.loads(Path(manifest).read_text(encoding="utf-8"))["files"]
        ply, scene = (Path(bundle) / n for n in ("points-mobile.ply", "scene.json"))
        data = ply.read_bytes()
        if hashlib.sha256(data).hexdigest() != listed["points-mobile.ply"]["sha256"]:
            return None
        poses = json.loads(scene.read_text(encoding="utf-8"))["camera_path"]
    except (OSError, KeyError, ValueError):
        return None
    job_id = uuid.uuid4().hex
    d = Path(root) / "rooms" / owner / job_id
    d.mkdir(parents=True)
    labels = {"input": "RECORDED", "geometry": "MODEL-ESTIMATED (MapAnything)", "scale": "scale unverified"}
    room = {"schema": "n08-room/1", "sample": True, "points": int(re.search(rb"element vertex (\d+)", data)[1]),
            "floor": {"status": "ABSTAIN", "reason": "recorded sample: no floor plane fitted"},
            "gravity": {"status": "unverified", "method": "none for this recorded sample", "uncertainty_deg": None},
            "scale": {"status": "scale unverified", "metres_per_model_unit": 1.0, "sd": None,
                      "evidence": "MapAnything nominal scale; no reference object. Rescale in the app with a known size."},
            "labels": labels, "camera_positions_m": [p["pose"]["position_m"] for p in poses], "note": _NOTE}
    scene = {"version": "lab-scene-v1", "label": "SIMULATED", "units": "m", "gravity": [0, -9.81, 0],
             "room": {"kind": "ply", "floor_y": 0, "source": "room.ply", "scale_verified": False}, "objects": []}
    (d / "room.ply").write_bytes(data)
    for name, obj in (("room.json", room), ("scene.json", scene),
                      ("status.json", {"job_id": job_id, "state": "done", "file_id": None, "project_id": project_id,
                                       "sample": True, "scale": "scale unverified", "label": _NOTE,
                                       "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})):
        (d / name).write_text(json.dumps(obj, indent=1) + "\n", encoding="utf-8")
    return d


def seed(store, owner, bundle=None, manifest=None, experiment=None):
    """Idempotent per user (samples table). Returns the project id when it seeded now, else None."""
    bundle, manifest, experiment = bundle or BUNDLE, manifest or MANIFEST, experiment or EXPERIMENT
    from Build.api import experiment as exp  # lazy: experiment imports storage.files
    now = store.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    room_dir = None
    with store.lock:
        db = store.db
        db.execute("CREATE TABLE IF NOT EXISTS samples (user TEXT PRIMARY KEY, project_id TEXT NOT NULL)")
        if db.execute("SELECT 1 FROM samples WHERE user=?", (owner,)).fetchone():
            return None
        db.execute("BEGIN")
        try:
            pid = uuid.uuid4().hex
            db.execute("INSERT INTO projects (id, user, mode, title, created) VALUES (?,?,?,?,?)",
                       (pid, owner, "room", TITLE, now))
            result = json.loads(Path(experiment).read_text(encoding="utf-8"))["result"]
            result["sample"] = {"label": _NOTE, "source": "ST03, Pexels License", "recorded_cost_usd": result.pop("cost_usd", None)}
            req = {"file_id": "sample", "target_text": "apple", "point": None, "known_size": None}
            db.execute(exp._SCHEMA)
            db.execute("INSERT INTO experiments VALUES (?,?,?,?,?,?,?,NULL,?,?)",
                       (uuid.uuid4().hex, owner, pid, "sample", "done", json.dumps(req), json.dumps(result), now, now))
            room_dir = _room(store.root, owner, pid, bundle, manifest)
            db.execute("INSERT INTO samples VALUES (?,?)", (owner, pid))
            db.execute("COMMIT")
        except BaseException:
            db.execute("ROLLBACK")
            if room_dir:
                shutil.rmtree(room_dir, ignore_errors=True)
            raise
    return pid


def make_hook(db):
    """Router dependency: seed before a user's first files/projects list; a seeding fault never breaks the list."""
    def hook(request: Request, owner: str = Depends(require_owner)):
        if request.method == "GET" and request.url.path.rstrip("/").endswith(("/files", "/projects")):
            try:
                seed(db(), owner)
            except Exception:
                logging.getLogger(__name__).exception("sample seeding failed")
    return hook
