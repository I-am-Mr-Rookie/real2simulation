"""N11: one labelled SAMPLE project per user, seeded on their first files/projects list.

Recorded results only: a hash-verified public classroom bundle (baked into the API image by
infra/railway/dev/stage.py) and the ST03 falling-apple experiment (evidence/N07). No per-user inference/video bytes.
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


def _public_bytes(bundle, listed, name):
    if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name):
        raise ValueError("invalid public sample asset name")
    data = (Path(bundle) / name).read_bytes()
    if hashlib.sha256(data).hexdigest() != listed[name]["sha256"]:
        raise ValueError("public sample archive hash mismatch")
    return data


def _ensure_shell(d, bundle, manifest):
    """Copy the once-computed RM02 shell, never generate it on a user's request."""
    from Build.reconstruction import live_room
    from Build.reconstruction.shape_upgrade import LOCK
    template, listed = manifest["sample_shell"], manifest["files"]
    if template["schema"] != "sample-room-shell/1":
        raise ValueError("unsupported public sample shell")
    with LOCK:
        room = json.loads((d / "room.json").read_text(encoding="utf-8"))
        targets = {"mapanything.npz": template["archive"], "room.ply": template["point_cloud"]}
        for oid, name in template["meshes"].items():
            if not re.fullmatch(r"room-object-[0-9]+", oid):
                raise ValueError("invalid public sample object id")
            targets[f"objects/{oid}.glb"] = name
        if room.get("sample_shell_sha256") == listed[template["scene"]]["sha256"]:
            # A later user edit/deletion is intentional. Only restore missing binary assets, not scene objects.
            for target, source in targets.items():
                if not (d / target).is_file():
                    (d / target).parent.mkdir(exist_ok=True)
                    (d / target).write_bytes(_public_bytes(bundle, listed, source))
            return
        scene = json.loads((d / "scene.json").read_text(encoding="utf-8"))
        if room.get("shell") or any(str(o.get("id", "")).startswith(("room-object-", "wall-")) for o in scene.get("objects", [])):
            return  # preserve a shell the user explicitly built, including its active/finished upgrades
        # Validate the entire shared pack before changing an old sample, including already-present archives.
        new_scene = json.loads(_public_bytes(bundle, listed, template["scene"]))
        new_room = json.loads(_public_bytes(bundle, listed, template["room"]))
        if new_room["scale"]["status"] != "scale unverified" or new_scene["room"].get("scale_verified"):
            raise ValueError("recorded sample scale must remain unverified")
        for obj in new_scene["objects"]:
            if obj.get("shape", {}).get("type") == "mesh":
                if obj["id"] not in template["meshes"]:
                    raise ValueError("public sample mesh is missing from the manifest")
                obj["shape"]["glb"] = f"/api/workspace/rooms/{d.name}/objects/{obj['id']}.glb"
        # Keep user-added objects/settings. Record the old metadata so the source/frame migration is recoverable.
        existing_ids = {obj["id"] for obj in scene.get("objects", [])}
        objects = [obj for obj in new_scene["objects"] if obj["id"] not in existing_ids] + scene.get("objects", [])
        if len(objects) > 50:  # scene.mjs MAX_OBJECTS; never make an existing user's scene unloadable
            return
        contents = {target: _public_bytes(bundle, listed, source) for target, source in targets.items()}
        for name, obj in (("sample-previous-room.json", room), ("sample-previous-scene.json", scene)):
            if not (d / name).exists():
                live_room._write(d / name, obj)
        for target, data in contents.items():
            (d / target).parent.mkdir(exist_ok=True)
            (d / target).write_bytes(data)
        live_room._write(d / "scene.json", {**new_scene, **scene, "room": new_scene["room"], "objects": objects})
        live_room._write(d / "room.json", {**new_room, "sample": True, "note": _NOTE,
                                          "labels": {**new_room.get("labels", {}), "input": "SAMPLE / RECORDED",
                                                     "geometry": "SAMPLE / RECORDED, " + new_room.get("labels", {}).get("geometry", "MODEL-ESTIMATED")},
                                          "sample_shell_sha256": listed[template["scene"]]["sha256"]})


def ensure_room_archive(d, bundle=None, manifest=None):
    """Repair pre-N58 samples too; never substitute a public archive for a user's room."""
    d = Path(d)
    status = json.loads((d / "status.json").read_text(encoding="utf-8"))
    if not status.get("sample"):
        if (d / "mapanything.npz").is_file():
            return
        raise FileNotFoundError("room reconstruction archive is unavailable")
    bundle = bundle or BUNDLE
    manifest = json.loads(Path(manifest or MANIFEST).read_text(encoding="utf-8"))
    if "sample_shell" in manifest:
        _ensure_shell(d, bundle, manifest)
    if (d / "mapanything.npz").is_file():
        return
    name = "RM04-mapanything.npz"
    data = _public_bytes(bundle, manifest["files"], name)
    from Build.reconstruction import live_room
    # Use the same gravity-aligned frame as A4 scaling and object lifting, not the old display-only PLY frame.
    (d / "mapanything.npz").write_bytes(data)
    try:
        out = live_room.finish(d)
        room = {**out["room"], "sample": True, "note": _NOTE}
        (d / "room.json").write_text(json.dumps(room) + "\n", encoding="utf-8")
    except Exception:
        (d / "mapanything.npz").unlink(missing_ok=True)
        raise


def _room(root, owner, project_id, bundle, manifest):
    """Seed legacy display metadata, then install the shared RM02 shell when available; no inference."""
    try:
        recorded = json.loads(Path(manifest).read_text(encoding="utf-8"))
        listed = recorded["files"]
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
    if "RM04-mapanything.npz" in listed or "sample_shell" in recorded:
        ensure_room_archive(d, bundle, manifest)
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
        previous = db.execute("SELECT project_id FROM samples WHERE user=?", (owner,)).fetchone()
        if previous:
            if db.execute("SELECT 1 FROM projects WHERE id=? AND user=?", (previous[0], owner)).fetchone():
                found = False
                for status_file in (store.root / "rooms" / owner).glob("*/status.json"):
                    status = json.loads(status_file.read_text(encoding="utf-8"))
                    if status.get("sample") and status.get("project_id") == previous[0]:
                        found = True
                        ensure_room_archive(status_file.parent, bundle, manifest)
                if not found:  # old experiment-only seeds can recover once the shared bundle is available
                    _room(store.root, owner, previous[0], bundle, manifest)
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
