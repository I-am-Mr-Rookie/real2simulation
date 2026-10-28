"""Load the unchanged R14 tests against an explicitly selected external source."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest

HERE = Path(__file__).resolve().parent
AUDIT_ROOT = HERE.parents[2]
SOURCE = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(SOURCE))
FILES = ("Build/instruments/synthetic.py", "contracts/fit/quantity.py", "Build/lab/pipeline.py")


def hashes():
    return {name: hashlib.sha256((SOURCE / name).read_bytes()).hexdigest() for name in FILES}


before = hashes()
spec = importlib.util.spec_from_file_location("r14_external", AUDIT_ROOT / "tests/instruments/test_r14_invariants.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
suite = unittest.defaultTestLoader.loadTestsFromModule(module)
for pattern in ("test_quantity_contract.py", "test_synthetic.py"):
    suite.addTests(unittest.defaultTestLoader.discover(str(SOURCE / "tests/instruments"), pattern=pattern))
stream = io.StringIO()
result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
(HERE / "candidate-unittest.log").write_text(stream.getvalue(), encoding="utf-8")

baseline = json.loads((HERE / "probe.json").read_text(encoding="utf-8"))
rows = [row for group in baseline["frozen"].values() for row in group] + baseline["dyadic_sweep"]["cases"]
cache, mismatches = {}, []
for row in rows:
    key = (abs(row["input"]), row["resolution"])
    if key not in cache:
        cache[key] = module.observations(*key)
    observed = cache[key][row["instrument"]]["value"]
    if observed != row["expected"]:
        mismatches.append({"input_hex": row["input_hex"], "resolution_hex": row["resolution_hex"],
                           "instrument": row["instrument"], "expected": row["expected"], "observed": observed})
after = hashes()
report = {
    "source_root": str(SOURCE), "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=SOURCE, text=True).strip(),
    "branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=SOURCE, text=True).strip(),
    "source_sha256_before": before, "source_sha256_after": after,
    "source_unchanged_during_check": before == after,
    "audit_tests_sha256": hashlib.sha256((AUDIT_ROOT / "tests/instruments/test_r14_invariants.py").read_bytes()).hexdigest(),
    "tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
    "oracle_observations": len(rows), "oracle_mismatches": mismatches,
}
(HERE / "candidate-verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
sys.exit(0 if result.wasSuccessful() and not mismatches and before == after else 1)
