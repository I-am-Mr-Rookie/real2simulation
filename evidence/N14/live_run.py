"""N14 live run: RM02 (Pexels, clips.csv) room job (N08, Modal) then one click -> hosted SAM 3.1 -> box proxy.

uv run --python 3.12 --with modal==1.6.3 --with numpy --with fastapi --with httpx --with python-multipart \
  --with jsonschema --with pillow --env-file <root>/.env python evidence/N14/live_run.py room <RM02.mp4> <data_dir>
  ... python evidence/N14/live_run.py object <data_dir> <job_id> <view> <row> <col>
Writes evidence/N14/live/*. Secrets come from the env file, never printed.
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
OWNER = "user_n14live"

from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from Build.api.room import create_router  # noqa: E402
from Build.api.room.objects import create_router as objects_router  # noqa: E402
from Build.api.storage.files import Store, video_seconds  # noqa: E402

h = {"x-workspace-token": os.environ["WORKSPACE_INTERNAL_TOKEN"], "x-workspace-owner": OWNER}

if sys.argv[1] == "room":
    video, data = Path(sys.argv[2]), Path(sys.argv[3])
    store = Store(data)
    tmp = data / "tmp" / "rm02-upload"
    shutil.copyfile(video, tmp)
    rec = store.add(OWNER, "RM02.mp4", "video/mp4", tmp, video_seconds(tmp))
    app = FastAPI()
    app.include_router(create_router(store))
    app.include_router(objects_router(store))
    c = TestClient(app)
    t0 = time.time()
    job = c.post("/internal/workspace/rooms", headers=h, json={"file_id": rec["id"]}).json()["job"]
    while time.time() - t0 < 900:
        s = c.get(f"/internal/workspace/rooms/{job['job_id']}", headers=h).json()["job"]
        if s["state"] in ("done", "failed"):
            break
        time.sleep(5)
    d = data / "rooms" / OWNER / job["job_id"]
    for name in ("status.json", "room.json", "cost-log.json"):
        if (d / name).exists():
            shutil.copyfile(d / name, OUT / f"room-{name}")
    if s["state"] == "done":
        for v in range(8):
            r = c.get(f"/internal/workspace/rooms/{job['job_id']}/views/{v}.png", headers=h)
            (data / f"view{v}.png").write_bytes(r.content)  # RM02 frames stay out of git (local only)
    print(json.dumps({"job_id": job["job_id"], "state": s["state"], "error": s.get("error"),
                      "estimated_usd": s.get("estimated_usd"), "wall_s": round(time.time() - t0, 1)}))
else:
    data, job_id, view, row, col = Path(sys.argv[2]), sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
    app = FastAPI()
    app.include_router(objects_router(Store(data)))
    c = TestClient(app)
    t0 = time.time()
    r = c.post(f"/internal/workspace/rooms/{job_id}/objects", headers=h, json={"view": view, "point": [row, col]})
    out = {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "http": r.status_code,
           "seconds": round(time.time() - t0, 1), "body": r.json()}
    (OUT / f"object-v{view}-{row}-{col}.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(out)[:1500])
