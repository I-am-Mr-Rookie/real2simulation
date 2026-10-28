"""Read-only local scope/ignore/source audit; no provider modules imported."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
SPIKE = "Build/reconstruction/spike/"
owned = {".gitignore", *(SPIKE + name for name in (
    "rm02_watchdog.py", "test_rm02_watchdog.py", "test_rm02_deadline.py", "README.md"))}

def git(*args):
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, timeout=10)
    return result.returncode, result.stdout.decode("utf-8"), result.stderr.decode("utf-8")

changed = git("diff", "--name-only")[1].splitlines()
assert set(changed) <= owned, changed
assert git("diff", "--check")[0] == 0
assert git("branch", "--show-current")[1].strip() == "run/S05b-recovery9"
constants = {}
for node in ast.parse((ROOT / SPIKE / "rm02_deadline.py").read_text()).body:
    if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
        constants[node.targets[0].id] = ast.literal_eval(node.value)
assert constants == dict(TOTAL_SECONDS=1200, STARTUP_SECONDS=90, EXECUTION_SECONDS=900,
                         CLEANUP_SECONDS=60, STOP_SECONDS=20, EXIT_SECONDS=10), constants
assert not git("diff", "--", SPIKE + "modal_rm02.py", SPIKE + "rm02_deadline.py",
               SPIKE + "requirements.in", SPIKE + "requirements-linux-py311.txt")[1]
paths = {
    "evidence/S05/S05b/recovery8/attempt-x/local/RM02-mapanything.npz": True,
    "evidence/S05/S05b/recovery8/attempt-x/local/partial-result": True,
    "evidence/S05/S05b/recovery8/attempt-x/worker.json": False,
    "evidence/S05/S05b/recovery8/attempt-x/watchdog.json": False,
    "evidence/S05/S05b/recovery8/attempt-x/gpu-result.json": False,
    "evidence/S05/S05b/recovery8/input.json": False,
    SPIKE + "rm02_watchdog.py": False,
    "evidence/S05/S05b/recovery9/limits.md": False,
}
ignores = {}
for path, expected in paths.items():
    code, out, err = git("check-ignore", "-v", "--", path)
    assert code in (0, 1) and not err, (path, code, err)
    assert (code == 0) == expected, (path, out)
    ignores[path] = {"ignored": code == 0, "rule": out.strip()}
hashes = {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in sorted(owned)}
versions = {}
for name, interpreter in (("default", sys.executable), ("target", "C:/Users/HP/AppData/Roaming/uv/python/cpython-3.11-windows-x86_64-none/python.exe")):
    result = subprocess.run([interpreter, "-E", "-s", "-B", "-c",
                             "import sys,time;print(sys.version);print(time.get_clock_info('monotonic'))"],
                            capture_output=True, timeout=10, check=True)
    versions[name] = result.stdout.decode("utf-8").strip()
report = {"scope_pass": True, "branch": "run/S05b-recovery9", "head": git("rev-parse", "HEAD")[1].strip(),
          "changed_tracked": changed, "production_constants_unchanged": constants,
          "runner_and_dependencies_unchanged": True, "ignore_checks": ignores,
          "sha256": hashes, "runtime_versions": versions,
          "status": git("status", "--short")[1]}
Path(__file__).with_name("audit.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
