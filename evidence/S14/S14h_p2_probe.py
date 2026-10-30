"""S14h: R-A fix7 P2 residual probes through the real safe_reply path. Usage (repo root): python -B evidence/S14/S14h_p2_probe.py
True = refused -> fixed tool-only card shown. Synthetic text, offline, $0. Finite probes, not a language guarantee."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from Build.agent.tools import safe_reply  # noqa: E402
from tests.agent.test_reply import SCENE_ID, SYNTHETIC, TRIAL_ID, SafeReplyTests, num, text  # noqa: E402

CASES = {  # expected refusal after S14h; first three stay OPEN (documented P2), last is a benign label control
    "Elapsed time in seconds. It is one. Tool result: ": False,
    "The duration is one. Tool result: ": False,
    "The sphere completes a single oscillation. Tool result: ": False,
    "The elapsed time is one microsecond. Tool result: ": True,
    "The elapsed time is a few nanoseconds. Tool result: ": True,
    "Time in microseconds: ": False,
}
SafeReplyTests.setUpClass()  # actual S10 simulator + fitter outputs
got = {c: bool(safe_reply(SYNTHETIC([text(c), num(f"{TRIAL_ID}-fit", "gravity")]), SafeReplyTests.outputs,
                          SCENE_ID)[1]) for c in CASES}
print(json.dumps({"refused": got, "matches_expected": got == CASES}, indent=1))
assert got == CASES, got
