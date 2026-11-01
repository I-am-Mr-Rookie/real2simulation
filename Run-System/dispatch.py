"""Build a lean worker prompt. usage: python Run-System/dispatch.py <RID> <30|60> <model> <effort> <taskfile>
Writes Run-System/Runs/ORCH-20261029-1654/DISPATCH-<RID>.json and prints {"P": prompt, "due": dhaka}."""
import json, subprocess, sys

rid, minutes, model, effort, taskfile = sys.argv[1:6]
tb = json.loads(subprocess.check_output([sys.executable, "Run-System/worker_timebox.py", "issue", rid, minutes]))
task = open(taskfile, encoding="utf-8").read().strip()
prompt = (f"Run {rid}. Read Run-System/WORKER_CONTRACT.md first and follow it. Model {model}/{effort}.\n"
          f"Timebox: issued {tb['issued_at']}; deadline {tb['deadline_at']} (Dhaka {tb['deadline_dhaka']}); "
          f"cutoff {tb['implementation_cutoff_at']}.\n{task}")
out = f"Run-System/Runs/ORCH-20261029-1654/DISPATCH-{rid}.json"
json.dump({"id": rid, "model": model, "effort": effort, "minutes": int(minutes), "prompt": prompt},
          open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({"P": prompt, "due": tb["deadline_dhaka"]}))
