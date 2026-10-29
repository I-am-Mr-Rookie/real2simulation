"""Mutation self-check: each guard removed -> agent tests must fail. Restores files via git."""
import subprocess
import sys
from pathlib import Path

MUTANTS = [
    ("contracts/agent/validate.py", "if candidate[\"template\"] not in TEMPLATES:", "if False:"),
    ("contracts/agent/validate.py", "if candidate[\"id\"] in seen:", "if False:"),
    ("Build/agent/muse.py", "if body.get(\"status\") not in (None, \"completed\"):", "if False:"),
    ("Build/agent/muse.py", "validate_response(output_text(post(build_request(context))), (), context[\"scene_id\"])",
     "__import__('json').loads(output_text(post(build_request(context))))"),
    ("Build/agent/record_muse.py", "if len(rows) >= MAX_CALLS or spent + worst > MAX_USD:", "if False:"),
]
for path, old, new in MUTANTS:
    p = Path(path)
    src = p.read_bytes().decode("utf-8")  # bytes I/O: keep original line endings on restore
    assert src.count(old) == 1, (path, old)
    p.write_bytes(src.replace(old, new).encode("utf-8"))
    try:
        rc = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests/agent", "-p", "test_*.py"],
                            capture_output=True).returncode
    finally:
        p.write_bytes(src.encode("utf-8"))
    print("KILLED" if rc else "SURVIVED", path, old[:60])
