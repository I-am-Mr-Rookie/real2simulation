"""N07 live run: ST03 (Pexels License) through POST/GET /internal/workspace/experiments, hosted SAM 3.1. Key never printed.

Usage: python evidence/N07/live_run.py <ST03.mp4> <.env path> <data dir outside the repo>
Writes evidence/N07/live-st03.json (result without per-frame arrays) and ledger.jsonl (paid call, from the daily cap).
"""
import hashlib
import json
import os
import shutil
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
SOURCE_SHA256 = "7239da801ff407cf5ff047fceb82351724ad35985be298ffcb0e4ba1a53df051"


def main(video, env, data):
    if hashlib.sha256(Path(video).read_bytes()).hexdigest() != SOURCE_SHA256:
        raise SystemExit("ST03 bytes differ from the accepted source hash")
    for line in Path(env).read_text(encoding="utf-8").splitlines():
        k, _, v = line.partition("=")
        if k.strip() in ("MODEL_API_KEY", "MODEL_API_BASE_URL") and v.strip():
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    os.environ.update(R2S_DATA_DIR=data, WORKSPACE_INTERNAL_TOKEN="local-n07")
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from Build.api.experiment import create_router
    from Build.api.storage.files import Store
    store = Store(data)
    tmp = Path(data) / "st03-upload.mp4"
    shutil.copyfile(video, tmp)
    f = store.add("n07-live", "ST03.mp4", "video/mp4", tmp, None)
    app = FastAPI()
    app.include_router(create_router(store))
    c, h = TestClient(app), {"x-workspace-token": "local-n07", "x-workspace-owner": "n07-live"}
    t0 = time.time()
    e = c.post("/internal/workspace/experiments", headers=h, json={"file_id": f["id"], "target_text": "apple"}).json()
    polls = [e["experiment"]["status"]]
    while polls[-1] in ("queued", "running") and time.time() - t0 < 900:
        time.sleep(3)
        polls.append(c.get(f"/internal/workspace/experiments/{e['experiment']['id']}", headers=h).json()["experiment"]["status"])
    got = c.get(f"/internal/workspace/experiments/{e['experiment']['id']}", headers=h).json()["experiment"]
    res = got["result"] or {}
    if res.get("track"):
        res["track"] = {k: v for k, v in res["track"].items() if k != "frames"} | {"tracked_frames": len(res["track"]["frames"])}
    out = {"utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "seconds": round(time.time() - t0, 1),
           "status": got["status"], "error": got["error"], "polled_statuses": sorted(set(polls)),
           "project_id_attached": bool(got["project_id"]), "result": res}
    (ROOT / "evidence/N07/live-st03.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    con = sqlite3.connect(Path(data) / "spend.sqlite3")
    rows = con.execute("SELECT reserved_at, provider, label, reserved, actual FROM spend").fetchall()
    with (ROOT / "evidence/N07/ledger.jsonl").open("a", encoding="utf-8") as fh:
        for at, prov, label, reserved, actual in rows:
            fh.write(json.dumps({"utc": at, "provider": prov, "model": "sam-3.1", "label": label,
                                 "reserved_usd": reserved / 1e8, "cost_usd": actual / 1e8 if actual is not None else None,
                                 "video_frames_processed": res.get("video_frames_processed")}) + "\n")
    print(json.dumps({k: out[k] for k in ("status", "error", "seconds")} | {"motion": res.get("motion"),
          "quantity": res.get("quantity"), "segment": res.get("segment"), "cost_usd": res.get("cost_usd")}))


if __name__ == "__main__":
    main(*sys.argv[1:4])

