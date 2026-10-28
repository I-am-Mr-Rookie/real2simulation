"""Controlled lifecycle fixture only: no simulator, network, secrets or external work."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

root = Path.cwd()
config = json.loads((root / "config.json").read_text(encoding="utf-8"))
json.loads(sys.stdin.read())  # Exercise the actual service's stdin transport.
child = subprocess.Popen(
    [config["node"], str(root / "idle-child.mjs"), config["token"], str(root)],
    stdin=subprocess.DEVNULL,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
record = {"pid": os.getpid(), "parentPid": os.getppid(), "childPid": child.pid,
          "token": config["token"]}
target = root / f"bridge-{os.getpid()}.json"
temporary = target.with_suffix(".tmp")
temporary.write_text(json.dumps(record), encoding="utf-8")
temporary.replace(target)
# A hard fixture lifetime bounds failures even if the harness itself crashes.
try:
    child.wait(timeout=60)
except subprocess.TimeoutExpired:
    child.kill()
    child.wait(timeout=5)
sys.exit(1)
