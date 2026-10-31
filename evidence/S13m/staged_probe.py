"""S13m staged-API probe: import the app from a stage.py api context, upload the approved RM04 clip with a synthetic
owner/token fixture, GET the three bundle files and compare sha256 with the recorded manifest. Offline (TestClient)."""
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

stage, clip, out = (Path(a).resolve() for a in sys.argv[1:4])
os.chdir(stage)
sys.path.insert(0, str(stage))
os.environ.pop("REDIS_URL", None)
os.environ.update(WORKSPACE_INTERNAL_TOKEN="synthetic-s13m-token", WORKSPACE_UPLOAD_DIR=tempfile.mkdtemp())
from fastapi.testclient import TestClient  # noqa: E402
from Build.api.health.app import app  # noqa: E402
from Build.api.workspace import jobs  # noqa: E402

assert Path(jobs.__file__).resolve().is_relative_to(stage), jobs.__file__
H = {"x-workspace-token": "synthetic-s13m-token", "x-workspace-owner": "user_synthS13m"}
c, data = TestClient(app), clip.read_bytes()
sha = hashlib.sha256(data).hexdigest()
uid = c.post("/internal/workspace/uploads", headers=H, json={"media_type": "video/mp4", "size_bytes": len(data), "sha256": sha}).json()["upload_id"]
for at in range(0, len(data), 8_388_608):
    assert c.put(f"/internal/workspace/uploads/{uid}/chunks/{at}", headers=H, content=data[at:at + 8_388_608]).status_code == 200
job = c.post(f"/internal/workspace/uploads/{uid}/complete", headers=H).json()["job"]
want = json.loads(Path(jobs.BUNDLE_MANIFEST).read_text(encoding="utf-8"))["files"]
res = {"stage": str(stage), "clip_sha256": sha, "job_status": job["status"], "scene_dir": str(jobs.SCENE_DIR), "files": {}}
for name, entry in want.items():
    r = c.get(f"/internal/workspace/scenes/{job['job_id']}/bundle/{name}", headers=H)
    body = hashlib.sha256(r.content).hexdigest()
    if name == "scene.json":  # served id is re-bound to the job; every other field must equal the verified bytes
        orig = json.loads((jobs.SCENE_DIR / name).read_bytes())
        same = r.json() == {**orig, "id": job["job_id"]}
    else:
        same = body == entry["sha256"]
    res["files"][name] = {"status": r.status_code, "cache_control": r.headers.get("cache-control"), "body_sha256": body,
                          "source_sha256_header": r.headers.get("x-r2s-source-sha256"), "manifest_sha256": entry["sha256"],
                          "match": same and r.headers.get("x-r2s-source-sha256") == entry["sha256"]}
other = c.get(f"/internal/workspace/scenes/{job['job_id']}/bundle/points.ply", headers={**H, "x-workspace-owner": "user_synthOther"})
os.environ["WORKSPACE_SCENE_DIR"] = str(stage / "no-such-dir")
missing = c.get(f"/internal/workspace/scenes/{job['job_id']}/bundle/points.ply", headers=H)
res |= {"other_owner": other.status_code, "missing_dir": [missing.status_code, missing.json()["detail"]["code"]]}
res["ok"] = (job["status"] == "ready" and all(f["status"] == 200 and f["match"] for f in res["files"].values())
             and res["other_owner"] == 404 and res["missing_dir"] == [503, "DEPENDENCY_UNAVAILABLE"])
out.write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
print(json.dumps({"ok": res["ok"]}))
