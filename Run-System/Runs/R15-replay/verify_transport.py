"""Verify the actual replay CLI against unchanged R14 synthetic receipts."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FROZEN = ROOT / "evidence/S10/replay-invariants"
expected = json.loads((FROZEN / "actual-record-hashes.json").read_text(encoding="utf-8"))
cases = []
for case in expected["cases"]:
    artifact = FROZEN / f'{case["template"]}-validated.json'
    result = subprocess.run(
        ["node", "Build/lab/replay-check.mjs"], input=artifact.read_text(encoding="utf-8"),
        text=True, capture_output=True, encoding="utf-8", timeout=15, cwd=ROOT, check=True,
    )
    actual = json.loads(result.stdout)
    assert actual == case["replay"], (case["template"], actual, case["replay"])
    cases.append({"template": case["template"], "artifact_sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(), "replay": actual})

sources = ["Build/simulator/replay.mjs", "Build/lab/replay-check.mjs",
           "tests/simulator/r14-replay-invariants.test.mjs", "tests/simulator/replay-recovery.test.mjs"]
receipt = {"captured_at": datetime.now(timezone.utc).isoformat(),
           "scope": "local synthetic CLI replay; identity equality, not authentication or physical accuracy",
           "sources_sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sources},
           "cases": cases}
(ROOT / "evidence/S10/replay-recovery/r15-transport.json").write_text(
    json.dumps(receipt, indent=2, allow_nan=False) + "\n", encoding="utf-8")
print("PASS: four actual CLI replay/trace identities equal unchanged R14 receipts")
