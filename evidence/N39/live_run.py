"""N39 live run (room job copied from N31): owner room clip N06_room.mp4 (PRIVATE) room job (Mode A path, L4) then one click -> SAM 3.1 -> SF3D.

uv run --python 3.12 --with modal==1.6.3 --with numpy --with fastapi --with httpx --with python-multipart \
  --with jsonschema --with pillow --env-file <root>/.env python evidence/N39/live_run.py room <N06_room.mp4> <data_dir>
  ... python evidence/N39/live_run.py shell <data_dir> <job_id> <sf3d 0|1> [budget_s]   (N39 room shell)
data_dir must be gitignored (test-data/private/N39): frames, crops and meshes of the owner room never enter git.
evidence/N39/live/*.json keeps numbers only (no images, no mesh data). Secrets come from the env file, never printed.
"""
import json
import os
import shutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
OUT = HERE / "live"
OUT.mkdir(exist_ok=True)
os.environ["WORKSPACE_INTERNAL_TOKEN"] = os.urandom(16).hex()  # local TestClient only
OWNER = "user_n39live"

from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from Build.api.room import create_router  # noqa: E402
from Build.api.room.objects import create_router as objects_router  # noqa: E402
from Build.api.storage.files import Store, video_seconds  # noqa: E402
from Build.reconstruction import live_room  # noqa: E402

h = {"x-workspace-token": os.environ["WORKSPACE_INTERNAL_TOKEN"], "x-workspace-owner": OWNER}


def remote(frames, gpu=None, budget_s=120):
    """live_room.modal_reconstruct with the timeout caught by name: with modal 1.6.3 get() raised a TimeoutError that
    is not modal.exception.TimeoutError (runs 1 and 2 on Nov 2: no cancel, no A10G fallback). Same spawn/cancel.
    N31_ROOM_GPU=A10G (after two L4 no-capacity runs) makes run_job's first attempt A10G, ledgered at the A10G rate."""
    import modal
    gpu = gpu or live_room.GPU
    fn = modal.Function.from_name(live_room.APP, "reconstruct").with_options(gpu=gpu)
    call = fn.spawn(frames)
    try:
        return call.get(timeout=budget_s if gpu == "L4" else 300 + 240)
    except Exception as e:
        if type(e).__name__ != "TimeoutError":
            raise
        call.cancel(terminate_containers=True)
        if gpu == "L4":
            raise RuntimeError(f"no GPU capacity/result within {budget_s}s on {gpu}") from None
        raise


live_room.GPU = os.environ.get("N31_ROOM_GPU", live_room.GPU)  # run_job reads the module global per attempt
if sys.argv[1] == "room":
    video, data = Path(sys.argv[2]), Path(sys.argv[3])
    store = Store(data)
    tmp = data / "tmp" / "n06-upload"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(video, tmp)
    rec = store.add(OWNER, "N06_room.mp4", "video/mp4", tmp, video_seconds(tmp))
    app = FastAPI()
    app.include_router(create_router(store, remote=remote))
    c = TestClient(app)
    t0 = time.time()
    job = c.post("/internal/workspace/rooms", headers=h, json={"file_id": rec["id"]}).json()["job"]
    while time.time() - t0 < 900:
        s = c.get(f"/internal/workspace/rooms/{job['job_id']}", headers=h).json()["job"]
        if s["state"] in ("done", "failed"):
            break
        time.sleep(5)
    d = data / "rooms" / OWNER / job["job_id"]
    if (d / "status.json").exists():  # numbers only: GPU, peak memory, timing, cost
        shutil.copyfile(d / "status.json", OUT / f"room-status-{job['job_id'][:8]}.json")
    if s["state"] == "done":
        for v in range(8):
            r = c.get(f"/internal/workspace/rooms/{job['job_id']}/views/{v}.png", headers=h)
            (data / f"view{v}.png").write_bytes(r.content)  # owner room frames: local only
    print(json.dumps({"job_id": job["job_id"], "state": s["state"], "error": s.get("error"),
                      "estimated_usd": s.get("estimated_usd"), "wall_s": round(time.time() - t0, 1)}))
elif sys.argv[1] == "shell":  # N39: python evidence/N39/live_run.py shell <data_dir> <job_id> <sf3d 0|1> [budget_s]
    data, job_id, use_sf3d = Path(sys.argv[2]), sys.argv[3], sys.argv[4] == "1"
    from Build.gpu import sf3d
    from Build.reconstruction import object_lift
    budget = int(sys.argv[5]) if len(sys.argv) > 5 else 220
    calls = []

    cache_f = data / "sam-boxes.json"  # pixel boxes of the private clip: local only; reused to avoid repeat paid calls
    cache = json.loads(cache_f.read_text()) if cache_f.exists() else {}

    def detect(png, noun, w, h):  # N39_DRY=1: no paid call, no detections (wall fit only)
        import hashlib
        key = f"{hashlib.sha1(png).hexdigest()[:12]}-{noun}"
        if os.environ.get("N39_DRY"):
            boxes = []
        elif key in cache:
            return cache[key]
        else:
            boxes = cache[key] = object_lift.sam_text(png, noun, w, h)
            cache_f.write_text(json.dumps(cache))
        calls.append({"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "noun": noun, "boxes": len(boxes)})
        return boxes
    app = FastAPI()
    app.include_router(objects_router(Store(data), detect=detect,
                                      generate=lambda png: sf3d.generate_remote(png, timeout_s=budget)))
    t0 = time.time()
    r = TestClient(app).post(f"/internal/workspace/rooms/{job_id}/shell", headers=h, json={"sf3d": use_sf3d})
    body = r.json()
    out = {"http": r.status_code, "seconds": round(time.time() - t0, 1), "dry": bool(os.environ.get("N39_DRY")),
           "sam_calls": calls, "shell": body.get("shell"), "error": body.get("error"),
           "scene_objects": [{k: o[k] for k in ("id", "position", "size")} for o in (body.get("scene") or {}).get("objects", [])]}
    name = "shell-dry.json" if out["dry"] else f"shell-sf3d{int(use_sf3d)}.json"
    (OUT / name).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("http", "seconds", "error")}), json.dumps(out["shell"])[:3000])
else:
    data, job_id, view, row, col = Path(sys.argv[2]), sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
    app = FastAPI()
    from Build.gpu import sf3d
    # client budget (seconds, argv[8]) keeps the ledger under the N31 $1.50 total: (budget + IDLE_S) s x A10G rate
    budget = int(sys.argv[8]) if len(sys.argv) > 8 else 220
    app.include_router(objects_router(Store(data), generate=lambda png: sf3d.generate_remote(png, timeout_s=budget)))
    c = TestClient(app)
    t0 = time.time()
    r = c.post(f"/internal/workspace/rooms/{job_id}/objects", headers=h,
               json={"view": view, "point": [row, col], "category": sys.argv[7]})
    body = r.json()
    o = body.get("object", {})
    out = {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "http": r.status_code,
           "seconds": round(time.time() - t0, 1),
           "object": {k: v for k, v in o.items() if k not in ("shape",)},  # mesh data stays local
           "shape": {k: v for k, v in (o.get("shape") or {}).items() if k not in ("vertices", "indices")},
           "error": body.get("error")}
    (OUT / f"object-v{view}-{row}-{col}.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(out)[:2500])

