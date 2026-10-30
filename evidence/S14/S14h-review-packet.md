# S14h cross-vendor review packet

Base main `d3a1343` (includes fix7 `3b07b4e`, R-A recheck5 CLEAR). Branch `run/S14h-orch115`.

## What changed
1. `contracts/agent/validate.py` `_UNIT`: `(?:milli)?seconds?` -> `(?:milli|micro|nano)?seconds?`. Closes the R-A P2 probe "one microsecond" via the existing fix7 clause rule; "in microseconds: <q>" still binds.
2. `tests/agent/test_reply.py`: one test — five distinct invalid replies (non-JSON, digit, microsecond, spelled number, forged ref) each return non-empty issues and the identical code-owned tool-only card. No Build/agent edit (fallback already code-owned).
3. Evidence: `evidence/S14/GATE_A.json`/`GATE_A.md`, `S14h_p2_probe.py` (+ `S14h-p2-probe.txt`), `S14h-replay.json`, `S14h-unittest.txt`.

## Verify (repo root, offline, $0)
```powershell
python -B -m unittest tests.agent.test_visible_text tests.agent.test_contracts tests.agent.test_reply tests.agent.test_trial tests.agent.test_retry tests.agent.test_interview tests.agent.test_muse tests.pipeline.test_understand   # 60 OK
python -B evidence/S14/S14g_fix_oracle.py corpus      # 84/84
python -B evidence/S14/S14h_p2_probe.py               # matches_expected true
python -B -c "import sys,json;sys.path.insert(0,'evidence/S14');import S14g_fix5_gate_a as F;print(json.dumps(F.run()['summary'])[:600])"   # 30/30, 0 fallback, 10/10, 0/10
```
Note: `evidence/reviews/R-A/recheck-fix7/verify.py` now exits 1 by design — its frozen protected-file hashes predate later main (first mismatch `Build/library/manifest.schema.json`, S16f) and S14h's `validate.py` edit. Re-baseline it in the review if reused.

## Review focus
- Does the unit addition refuse anything previously accepted in the 30 saved replies? (replay says no.)
- Is GATE_A.json faithful: verdict/label verbatim, 0/10 setup shown, residuals OPEN, no physical/scale claim?
- Still open by design: unitless "one", count nouns, other unlisted units, P3 conservative refusals.
