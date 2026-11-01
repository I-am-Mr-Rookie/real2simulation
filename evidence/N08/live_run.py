"""N08 live run: licensed RM02 room clip (Pexels, clips.csv) -> /internal/workspace/rooms -> Modal reconstruct.

uv run --python 3.12 --with modal==1.6.3 --with numpy --with fastapi --with httpx --with python-multipart \
  --with jsonschema --env-file <root>/.env python evidence/N08/live_run.py <RM02.mp4> <data_dir>
Writes evidence/N08/live/{status,room,scene,cost-log,polls}.json. Secrets come from the env file, never printed.
"""
import json
import os
import shutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
video, data = Path(sys.argv[1]), Path(sys.argv[2])
os.environ["R2S_DATA_DIR"] = str(data)
os.environ["WORKSPACE_INTERNAL_TOKEN"] = os.urandom(16).hex()  # local TestClient only

from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from Build.api.room import create_router  # noqa: E402
from Build.api.storage.files import Store, video_seconds  # noqa: E402

store = Store(data)
tmp = data / "tmp" / "rm02-upload"
shutil.copyfile(video, tmp)
rec = store.add("user_n08live", "RM02.mp4", "video/mp4", tmp, video_seconds(tmp))
app = FastAPI()
app.include_router(create_router(store))
c = TestClient(app)
h = {"x-workspace-token": os.environ["WORKSPACE_INTERNAL_TOKEN"], "x-workspace-owner": "user_n08live"}
t0 = time.time()
job = c.post("/internal/workspace/rooms", headers=h, json={"file_id": rec["id"]}).json()["job"]
polls = []
while time.time() - t0 < 900:
    s = c.get(f"/internal/workspace/rooms/{job['job_id']}", headers=h).json()["job"]
    polls.append({"t_s": round(time.time() - t0, 1), "state": s["state"], "gpu": s.get("gpu")})
    if s["state"] in ("done", "failed"):
        break
    time.sleep(5)
out = HERE / "live"
out.mkdir(exist_ok=True)
d = data / "rooms" / "user_n08live" / job["job_id"]
for name in ("status.json", "room.json", "scene.json", "cost-log.json"):
    if (d / name).exists():
        shutil.copyfile(d / name, out / name)
(out / "polls.json").write_text(json.dumps({"wall_s": round(time.time() - t0, 1), "polls": polls}, indent=1) + "\n")
print(json.dumps({"state": s["state"], "wall_s": round(time.time() - t0, 1), "error": s.get("error"),
                  "estimated_usd": s.get("estimated_usd"), "scale": s.get("scale"), "gravity": s.get("gravity")}))
