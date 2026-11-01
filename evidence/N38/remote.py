"""Send a checked-in probe over Railway SSH without exporting service variables."""
import base64
import json
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
PROJECT = "b07b0d66-2001-4ccc-915d-7d226744d189"
ENVIRONMENT = "c5823a28-5118-49d8-b4d6-9851fa8ccc45"


def remote(service, command):
    result = subprocess.run(["railway", "ssh", "-i", str(Path.home() / ".ssh/railway_chatgpt_ed25519"), "--project", PROJECT, "--environment", ENVIRONMENT,
                             "--service", service, command], capture_output=True, timeout=120)
    if result.returncode:
        raise RuntimeError(f"SSH command failed (exit {result.returncode}); raw output suppressed")
    return result.stdout


if __name__ == "__main__":
    encoded = base64.b64encode((ROOT / "probe.py").read_bytes()).decode()
    command = "python -c " + shlex.quote(f"import base64;exec(base64.b64decode('{encoded}'))")
    output = remote("api", command).decode()
    data = json.loads(output[output.index("{"):])
    (ROOT / sys.argv[1]).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(data, indent=2))
