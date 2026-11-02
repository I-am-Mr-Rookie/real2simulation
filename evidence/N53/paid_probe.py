"""One owner-authorized <=$5 public RM02 job on DEV CPU, with temporary code overlay and worker-only ledger.

Run only through the bounded bootstrap. No deployed file/config changes, no private inputs, no repeat run.
"""
import hashlib
import json
import os
import sqlite3
import sys
import threading
import time
from pathlib import Path
from unittest.mock import patch

BASE = Path(__file__).resolve().parents[2]
DATA = BASE / "data"
for entry in ("/app", "/app/Build/gpu", "/app/Build/reconstruction/spike", str(BASE)):
    sys.path.insert(0, entry)
os.environ["R2S_DATA_DIR"] = "/data"  # preserve shared queue reaper defaults; all worker charges explicitly use CAP
from Build.api.room.objects import build_shell_files
from Build.api.storage.files import video_seconds
from Build.gpu import sf3d
from Build.guardrails import daily_cap
from Build.measurement import hosted_sam
from Build.reconstruction import live_room, object_lift, room_shell

CAP = DATA / "spend.sqlite3"
LIMIT = daily_cap._units("5")
LOCK = threading.Lock()
EVENTS = []
START = time.perf_counter()


def timed(name, fn):
    def call(*args, **kwargs):
        start = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            with LOCK:
                EVENTS.append({"stage": name, "start_s": start - START,
                               "duration_s": time.perf_counter() - start})
    return call


def main():
    DATA.mkdir(exist_ok=False)  # fail closed on an accidental second paid invocation
    original_reserve = daily_cap.reserve

    def reserve(provider, amount, label="", path=None, now=None):
        if Path(path or daily_cap.default_path()).resolve() != CAP.resolve():
            raise RuntimeError("worker probe must not charge the visitor ledger")
        with LOCK:
            con = daily_cap._connect(CAP)
            try:
                spent = con.execute("SELECT COALESCE(SUM(COALESCE(actual,reserved)),0) FROM spend").fetchone()[0]
            finally:
                con.close()
            if spent + daily_cap._units(amount) > LIMIT:
                raise daily_cap.CapExceeded("N53 worker per-job $5 ceiling")
            return original_reserve(provider, amount, label, path=CAP, now=now)

    # This exact job/file is N47's approved public RM02, not an owner room.
    [source] = Path("/data").glob("rooms/*/6979686e91dd4e47975bcbaa5afb4e14/status.json")
    record = json.loads(source.read_text())
    assert record["file_id"] == "c6db535cbf9d4baa822dc61453acee56"
    video = Path("/data/files") / source.parent.parent.name / record["file_id"]
    duration = video_seconds(video)
    job = DATA / "rooms/user_n53worker/53535353535353535353535353535353"
    job.mkdir(parents=True)
    stats = {}
    import modal
    for app, function in (("r2s-ondemand", "reconstruct"), ("r2s-sf3d", "generate")):
        try:
            s = modal.Function.from_name(app, function).get_current_stats()
            stats[app] = {"runners": s.num_total_runners, "backlog": s.backlog}
        except Exception as e:
            stats[app] = {"error_type": type(e).__name__}

    def detect(png, noun, w, h):
        return object_lift.sam_text(png, noun, w, h, cap_path=CAP)

    def generate(png):
        return sf3d.generate_remote(png, cap_path=CAP)

    def shell(d):
        return build_shell_files(d, detect, timed("sf3d", generate))

    deployed = {name: hashlib.sha256((Path("/app") / name).read_bytes()).hexdigest()
                for name in ("Build/reconstruction/live_room.py", "Build/reconstruction/room_shell.py",
                             "Build/reconstruction/_sam_mask_codec.py", "Build/gpu/sf3d.py")}
    start = time.perf_counter()
    with patch.object(daily_cap, "reserve", reserve), \
         patch.object(object_lift, "_sam_image", timed("sam_network", object_lift._sam_image)), \
         patch.object(hosted_sam, "image_instances", timed("mask_decode_validation", hosted_sam.image_instances)), \
         patch.object(room_shell, "furniture", timed("furniture_lift", room_shell.furniture)), \
         patch.object(live_room, "_write", timed("json_save", live_room._write)):
        live_room.run_job(job, video, duration, "user_n53worker", cap_db=CAP,
                          gpu_db="/data/gpu.sqlite3", after=shell)
    elapsed = time.perf_counter() - start
    assert all(hashlib.sha256((Path("/app") / name).read_bytes()).hexdigest() == value
               for name, value in deployed.items()), "deployed source changed during the isolated probe"
    status = json.loads((job / "status.json").read_text())
    room = json.loads((job / "room.json").read_text()) if (job / "room.json").exists() else {}
    con = sqlite3.connect(CAP)
    con.row_factory = sqlite3.Row
    ledger = [dict(r) for r in con.execute("SELECT * FROM spend ORDER BY reserved_at,id")]
    con.close()
    total = sum(r["reserved"] if r["actual"] is None else r["actual"] for r in ledger)
    assert total <= LIMIT
    assert not any(r["actual"] is None for r in ledger), "unsettled paid liability"
    for r in ledger:
        r["estimated_usd"] = r["actual"] / 1e8
        r["model"] = ("sam-3.1" if r["provider"] == "Meta Model API" else
                      "stabilityai/stable-fast-3d" if r["label"] == "N31 sf3d" else "facebook/map-anything")
        r["units"] = 1
        r["unit_type"] = "image" if r["provider"] == "Meta Model API" else "GPU attempt"
    summary = {"label": "MEASURED one public RM02 backend job on DEV host, temporary new-code process; no deploy",
               "worker_budget_usd": 5, "worker_charges_use_separate_ledger": True, "browser_upload_s": None,
               "input_duration_s": duration, "input_bytes": video.stat().st_size,
               "initial_modal_stats": stats, "wall_s": elapsed, "status": status,
               "shell_timing_s": room.get("shell", {}).get("timing_s"),
               "sf3d_objects": [{k: x.get(k) for k in ("id", "shape", "sf3d", "fallback_reason")}
                                for x in room.get("shell", {}).get("kept", [])],
               "estimated_usd": total / 1e8, "ledger_rows": len(ledger),
               "deployed_source_unchanged": True,
               "overlay_sha256": {name: hashlib.sha256((BASE / name).read_bytes()).hexdigest() for name in deployed}}
    (BASE / "result.json").write_text(json.dumps(summary, indent=2))
    (BASE / "ledger.json").write_text(json.dumps(ledger, indent=2))
    (BASE / "events.json").write_text(json.dumps(EVENTS, indent=2))
    print("RESULT " + json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
