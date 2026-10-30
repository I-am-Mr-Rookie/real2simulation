"""Focused offline suites with writes confined to this review and protected-file hashes checked."""
from __future__ import annotations

import contextlib
import hashlib
import json
import os
from pathlib import Path
import socket
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
sys.path.insert(0, str(ROOT))
(OUT / "tmp").mkdir(exist_ok=True)
tempfile.tempdir = str(OUT / "tmp")


def deny(*_args, **_kwargs):
    raise AssertionError("offline review forbids network")


def audit(event, args):
    if event == "open":
        path, mode, flags = args
        if isinstance(path, (str, bytes, os.PathLike)):
            target = Path(os.fsdecode(path)).resolve()
            if target.name == ".env":
                raise AssertionError("review never reads .env")
            writing = bool(mode and any(c in mode for c in "wax+")) or bool(
                flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC))
            if writing and not target.is_relative_to(OUT):
                raise AssertionError(f"write outside review: {target}")


sys.addaudithook(audit)
socket.socket.connect = socket.create_connection = deny
baseline = json.loads((OUT / "results.json").read_text("utf-8"))["protected_input_sha256"]


def unchanged():
    for name, expected in baseline.items():
        with (ROOT / name).open("rb") as stream:
            assert hashlib.file_digest(stream, "sha256").hexdigest() == expected, name


unchanged()
modules = ["tests.agent.test_visible_text", "tests.agent.test_contracts", "tests.agent.test_reply",
           "tests.agent.test_trial", "tests.agent.test_retry", "tests.agent.test_interview",
           "tests.agent.test_muse", "tests.pipeline.test_understand", "tests.spec.test_setup_validation"]
with (OUT / "tests.txt").open("w", encoding="utf-8") as log, contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
    suite = unittest.defaultTestLoader.loadTestsFromNames(modules)
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
unchanged()
summary = {"modules": modules, "tests_run": result.testsRun, "failures": len(result.failures),
           "errors": len(result.errors), "skipped": len(result.skipped), "success": result.wasSuccessful(),
           "protected_files": len(baseline), "protected_inputs_unchanged": True,
           "network_denied": True, "spend_usd": 0}
(OUT / "tests-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, indent=2))
assert result.wasSuccessful(), "see tests.txt"
