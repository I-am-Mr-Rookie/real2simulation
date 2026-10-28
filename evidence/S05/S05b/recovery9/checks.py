"""Local-only bounded suite recorder; no runner or Modal imports."""
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
label, interpreter, suite = sys.argv[1:]
command = [interpreter, "-E", "-s", "-B", "-m", "unittest", "discover",
           "-s", "contracts/scene" if suite == "scene" else "Build/reconstruction/spike",
           "-p", "test_rm02_" + suite + ".py" if suite in ("deadline", "watchdog")
           else "test_*.py", "-v"]
started = time.monotonic()
try:
    result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=90)
    code, output = result.returncode, result.stdout + result.stderr
except subprocess.TimeoutExpired as exc:
    code, output = 124, (exc.stdout or b"") + (exc.stderr or b"")
log = Path(__file__).with_name(label + ".txt")
log.write_bytes(output)
metadata = {"command": command, "parent_cap_s": 90, "returncode": code,
            "elapsed_s": time.monotonic() - started, "log": log.name}
log.with_suffix(".json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
print(json.dumps(metadata))
print(output.decode("utf-8", errors="replace")[-1400:])
sys.exit(code)
