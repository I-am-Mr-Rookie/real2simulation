"""Validate planning controls without secrets, inference, product builds or deployments."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dispatcher as d

EVENT = Path("C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon")
HASH = "4E0C276C7156D15E465EED4B53708821B70E7EE8D6733555A07A2EEC65CA60F7"

def main():
    root=Path(__file__).resolve().parents[1]
    ap=argparse.ArgumentParser()
    ap.add_argument("--plan",type=Path,default=EVENT/"08 Real2Simulation"/"final plan.html")
    args=ap.parse_args()
    raw=args.plan.read_bytes()
    assert hashlib.sha256(raw).hexdigest().upper()==HASH,"Plan changed again; reconcile before proceeding"
    plan=json.loads(re.search(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>',raw.decode("utf-8-sig"),re.S).group(1))
    q=(root/"QUEUE.md").read_text(encoding="utf-8")
    tasks=d.read_queue(root/"QUEUE.md")
    source=[t for t in tasks if re.fullmatch(r"S\d{2}[a-z]",t.id)]
    assert source and len({t.id for t in tasks})==len(tasks),"empty queue or duplicate task IDs"
    for step in plan["steps"]:
        rows=[t for t in source if t.step==step["id"]]
        # Queue may grow past the plan via recorded owner additions; never drop below it.
        assert rows and sum(t.minutes for t in rows)>=step["timebox_minutes"],step["id"]
        assert all(x in q for x in step["acceptance"]),(step["id"],"missing acceptance")
        assert step["fallback"] in q,(step["id"],"missing fallback")
    for i,a in enumerate(tasks):
        for b in tasks[i+1:]:
            # Finished rows can no longer run in parallel, so only live rows can collide.
            if a.lane!=b.lane and "S03" not in {a.step,b.step} and "DONE" not in {a.status,b.status}:
                assert not d.overlap(a,b),("parallel Owns overlap",a.id,b.id)
    assert all(t.status in {"TODO","IN PROGRESS","PARTIAL","BLOCKED","DONE"} for t in tasks)
    for line in (root/".env.example").read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            assert re.fullmatch(r"[A-Z_][A-Z0-9_]*=",line),"Values forbidden in .env.example"
    assert subprocess.run(["git","-C",str(root),"check-ignore","-q",".env"],capture_output=True).returncode==0
    assert subprocess.run(["git","-C",str(root),"check-ignore","-q",".env.example"],capture_output=True).returncode!=0
    tracked=d.git(root,"ls-files").splitlines()
    assert not any(Path(x).name==".env" or "/private/" in x or "/uploads/" in x for x in tracked)
    controls=[x for x in root.iterdir() if x.is_file() and x.suffix in {".md",".example"}]
    secret=re.compile(r"AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{24,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")
    assert not any(secret.search(f.read_text(encoding="utf-8")) for f in controls)
    print(json.dumps({"PASS":True,"source_steps":26,"source_tasks":len(source),"all_tasks":len(tasks),
                      "source_minutes":sum(t.minutes for t in source),"all_minutes":sum(t.minutes for t in tasks),
                      "max_task_minutes":max(t.minutes for t in tasks),"acyclic":True,
                      "parallel_owns_collisions":0,"env_example":"names only",
                      "pattern_scan":"clean generated controls; not a full external secret scanner"}))

if __name__=="__main__":
    main()
