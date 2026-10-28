"""Execute actual stager with synthetic Git bytes and temporary destinations only."""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
source = ROOT / "infra/railway/dev/stage.py"
paths = ["Build/api/health/app.py", "infra/railway/dev/api.Dockerfile", ".env", "archive/private.txt"]


def git(command, **kwargs):
    if command[1] == "rev-parse": return "a" * 40 + "\n"
    if command[1] == "ls-tree": return "\n".join(paths)
    if command[1] == "show":
        return b"synthetic-new-content\n" if command[2].endswith("app.py") else b"ARG R2S_SOURCE_REVISION\n"
    raise AssertionError(command)


observations = []
for optimize in (0, 1):
    with tempfile.TemporaryDirectory() as temporary:
        target = Path(temporary) / "existing"
        original = target / "Build/api/health/app.py"
        original.parent.mkdir(parents=True)
        original.write_bytes(b"synthetic-original-do-not-overwrite")
        blocked = False
        with patch.object(sys, "argv", [str(source), "api", str(target)]), \
             patch("subprocess.check_output", side_effect=git), redirect_stdout(io.StringIO()):
            try:
                exec(compile(source.read_text(), str(source), "exec", optimize=optimize),
                     {"__file__": str(source), "__name__": "__main__"})
            except AssertionError:
                blocked = True
        overwritten = original.read_bytes() != b"synthetic-original-do-not-overwrite"
        assert blocked == (optimize == 0)
        assert overwritten == (optimize == 1)
        observations.append(dict(optimize=optimize, existing_target_blocked=blocked,
                                 synthetic_existing_file_overwritten=overwritten))
(HERE / "stage-observations.json").write_text(json.dumps(observations, indent=2) + "\n", encoding="utf-8")
print("PASS: reproduced optimized-mode fresh-destination guard loss using synthetic bytes only")
