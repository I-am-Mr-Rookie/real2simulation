# N26 fixture seeder: inserts 3 finished experiments for one owner into the local temp data dir, using the real fitter
# (Build.pipeline.live_experiment.analyse) on the RECORDED apple track. No network, no paid call.
# usage: python evidence/N26/seed.py <owner_user_id> <data_dir>
import json, sqlite3, sys, uuid
from datetime import datetime, timezone
from Build.pipeline import live_experiment as le
from tests.pipeline.test_live_experiment import apple_track

owner, root = sys.argv[1], sys.argv[2]
track = {**apple_track(), "source": "RECORDED hosted SAM 3.1 response (N26 fixture)"}
short = {"frames": track["frames"][:5], "source": track["source"]}
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
db = sqlite3.connect(f"{root}/r2s.sqlite3", timeout=20, isolation_level=None)
pid = uuid.uuid4().hex
db.execute("INSERT INTO projects (id, user, mode, title, created) VALUES (?,?,?,?,?)", (pid, owner, "experiment", "N26 fixtures", now))
out = {}
for key, tr, size in (("no_size", track, None), ("typed_size", track, "apple diameter 8 cm"), ("abstain", short, None)):
    eid = uuid.uuid4().hex
    result = {**le.analyse(tr, size), "track": tr}
    db.execute("INSERT INTO experiments VALUES (?,?,?,?,?,?,?,NULL,?,?)",
               (eid, owner, pid, "fixture", "done", json.dumps({"file_id": "fixture", "known_size": size}), json.dumps(result), now, now))
    out[key] = {"id": eid, "label": result.get("label"), "has_curve": "curve" in result, "reason": result.get("reason"),
                "quantity": result.get("quantity")}
print(json.dumps(out))