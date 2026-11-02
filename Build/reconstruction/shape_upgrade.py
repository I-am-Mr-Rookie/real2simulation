"""Optional post-ready SF3D upgrades. Physics remains the measured box, never the generated surface."""
import json
import threading
import time
import uuid

from Build.gpu import sf3d
from Build.reconstruction import live_room, object_lift

LOCK = threading.RLock()
_running = set()
_PROCESS = uuid.uuid4().hex


def prepare(d, inputs):
    previous = _read(d, "shape-upgrades.json") if (d / "shape-upgrades.json").exists() else {}
    batch = uuid.uuid4().hex
    for item in inputs:
        png = f"{batch}-{item['id']}.png"
        (d / "objects" / png).write_bytes(item.pop("png"))
        item["png"] = png
    live_room._write(d / "shape-upgrades.json", {"batch": batch, "inputs": inputs, "process": _PROCESS})
    for item in previous.get("inputs", []):
        png = d / "objects" / item["png"]
        if png.name == item["png"] and png.suffix == ".png":
            png.unlink(missing_ok=True)


def _read(d, name):
    return json.loads((d / name).read_text(encoding="utf-8"))


def fail_interrupted(d):
    """Report orphaned upgrades without resuming (which could pay twice). Caller holds LOCK."""
    if not (d / "shape-upgrades.json").exists():
        return
    work = _read(d, "shape-upgrades.json")
    if str(d) in _running or (work.get("process") == _PROCESS and not work.get("started_at")):
        return  # prepared/scheduled here, but the thread has not started yet
    for item in _read(d, "room.json").get("shell", {}).get("kept", []):
        if item.get("upgrade", {}).get("state") == "pending":
            _update(d, work["batch"], item["id"], {"state": "failed", "reason": "SF3D interrupted (server restart)"})


def _update(d, batch, oid, upgrade, shape=None, glb=None):
    with LOCK:
        if _read(d, "shape-upgrades.json")["batch"] != batch:
            return
        room, scene = _read(d, "room.json"), _read(d, "scene.json")
        kept = next((o for o in room.get("shell", {}).get("kept", []) if o["id"] == oid), None)
        obj = next((o for o in scene.get("objects", []) if o["id"] == oid), None)
        if not kept or not obj:
            return
        kept["upgrade"] = upgrade
        if shape is not None:
            (d / "objects" / f"{oid}.glb").write_bytes(glb)
            obj["shape"] = shape
            kept.update(shape="mesh", fallback_reason=None, sf3d=upgrade.get("sf3d"))
        elif upgrade["state"] == "failed":
            obj["shape"] = {"type": "box", "fallback_reason": upgrade["reason"]}
            kept["fallback_reason"] = upgrade["reason"]
        live_room._write(d / "scene.json", scene)
        live_room._write(d / "room.json", room)


def run(d, owner, *, gpu_db=None, cap_db=None, generate=sf3d.generate_remote):
    """One attempt per object, in a background thread AFTER status=done.
    shortcut: in-process supervisor; restart fails pending shapes, spend remains reserved until the GPU lease reaps.
    """
    with LOCK:
        if not (d / "shape-upgrades.json").exists() or str(d) in _running:
            return
        work = _read(d, "shape-upgrades.json")
        if work.get("started_at"):
            return
        work["started_at"] = time.time()
        live_room._write(d / "shape-upgrades.json", work)
        _running.add(str(d))
    try:
        def changed():
            with LOCK:
                return _read(d, "shape-upgrades.json")["batch"] != work["batch"]

        for item in work["inputs"]:
            with LOCK:
                if _read(d, "shape-upgrades.json")["batch"] != work["batch"]:
                    break  # do not pay for the remainder of a replaced shell
            started = time.time()
            try:
                r = generate((d / "objects" / item["png"]).read_bytes(), cap_path=cap_db,
                             timeout_s=sf3d.BACKGROUND_BUDGET_S, owner=owner, gpu_path=gpu_db, abort=changed)
                turns, verts, indices, _ = object_lift.fit_mesh(r["vertices"], r["faces"], item["proxy"])
                shape = object_lift.mesh_shape(item["category"],
                        f"/api/workspace/rooms/{d.name}/objects/{item['id']}.glb", turns, verts, indices)
                shape["collider"] = "box"
                receipt = {k: r.get(k) for k in ("gpu", "gpu_name", "wall_s", "model_load_s", "inference_s", "estimated_usd")}
                _update(d, work["batch"], item["id"], {"state": "ready", "sf3d": receipt,
                        "ready_at": time.time()}, shape, r["glb"])
            except Exception as e:
                _update(d, work["batch"], item["id"], {"state": "failed",
                        "reason": f"SF3D: {type(e).__name__}: {e}"[:300], "finished_at": time.time(),
                        "wall_s": round(time.time() - started, 3)})
    finally:
        with LOCK:
            _running.discard(str(d))
            latest = _read(d, "shape-upgrades.json")
            if latest["batch"] != work["batch"] and not latest.get("started_at"):
                start(d, owner, gpu_db=gpu_db, cap_db=cap_db, generate=generate)


def start(d, owner, **kwargs):
    if (d / "shape-upgrades.json").exists():
        threading.Thread(target=run, args=(d, owner), kwargs=kwargs, daemon=True).start()
