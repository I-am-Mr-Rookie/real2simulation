# S07j-orch173 REPORT — DONE
Lane CLAUDE; model anthropic/claude-opus-5-5/high; coding quota OpenCodex-managed, not polled. Tokens/cost: unknown (not observable). Modal: NOT run; evidence/S20/runtime/ read only (journal row count/amounts), not written.
UTC issued 2026-10-30T23:44:12Z; worktree start 23:46:24Z; work stopped 2026-10-30T23:52:20+00:00. Base main daffaee2.

## Changes
1. OOM fix — `Build/measurement/runtime/modal_track.py`: new `shared_predictor(load)` + module `_MODEL`: SAM 3.1 predictor loaded once per container, reused per clip. Per-clip wrappers (`handle_request` logger, `handle_stream_request` logger) are re-applied on the cached ORIGINALS each clip (no stacking; chunk mode resets to the original stream). Failed load caches nothing -> next clip retries; per-clip try/except isolation unchanged; sessions already closed in `finally` (tracking.py:207, track_chunks). gc+empty_cache between clips kept. Result gains `model_reused`. Image unchanged (no rebuild).
2. Envelope 2 — `Build/guardrails/standalone.py`: named constants `LEDGER, MAX_JOBS, CAP_USD = standalone-gpu-ledger-2.jsonl, 3, 1.50`. reserve_gpu counts every unsettled Modal journal row, so it is cumulative: old 2 jobs/$1.00 stay counted -> exactly 1 new job <= $0.50. Old ledger/journal rows never touched; no release. Record: [ENVELOPE-2.md](../../../evidence/S07/S07j/ENVELOPE-2.md).
3. Re-track subset — `evidence/S07/S07j/fall-windows-own07-11.json`: OWN07-OWN11 windows/prompts/object_id copied unchanged from S07i, outputs moved to evidence/S07/S07j/track-ownNN.json (S07i failed results untouched; `open("x")` would refuse them). Windows: OWN07 f40-61, OWN08 f30-50, OWN09 f4-24, OWN10 f6-18, OWN11 f23-34.
   All-in worst case: (300+780) s x $0.0003677/s = $0.397 (count-independent) -> reserve $0.40 <= $0.50.

## Controller command (after fast-forward merge to main; refresh evidence/S20/runtime/receipt.json from the Modal dashboard first, as in S07i)
```powershell
$env:PYTHONUTF8='1'; $env:S20_MODAL_RESERVATION_USD='0.40'; uv run --python 3.12 --with modal==1.6.3 --env-file .env modal run Build/measurement/runtime/modal_track.py --batch evidence/S07/S07j/fall-windows-own07-11.json --approval evidence/S07/S07g/OWNER-APPROVAL.md
```
Optional no-GPU preflight: prefix `$env:S07B_DRY='1';` (plans/extracts frames, never admits).

## Tests (fresh, in worktree)
- `python -B -m unittest discover -s tests/measurement -t tests/measurement` -> Ran 90, OK (skipped=1, ST03 media).
  New: SharedPredictorTest (load once/originals returned; failed load retried; track_one loads only via shared_predictor), S07j subset == S07i windows except out.
- `python -B -m unittest discover -s tests/guardrails -t tests/guardrails` -> Ran 95, 1 failure: `test_admission...test_guest_precomputed_fixture_read_does_not_consult_admission` (web Library copy string) — PRE-EXISTING: fails identically on clean main (verified via git stash). New envelope-2 tests pass.

## Ponytail (full, 5.3.3)
Reuse: existing reserve_gpu/claim_gpu global checks (no reservations.py change); envelope = 3 constants; existing fake-modal harness + LiveAdmission fixture. Smallest: memoized load vs restructuring track_one; no PYTORCH_CUDA_ALLOC_CONF (needs image.env -> image rebuild). Skipped: S07B_DRY local dry-run of the subset (S07i dry-run covered same windows); no Modal/GPU verification of the OOM fix.
Risks: (a) OOM fix unverified on GPU — if sam3 leaks per-session state, reuse could still grow; per-clip failures stay isolated. (b) `evidence/S20/simulated_cap_regression.py` (not owned) replays envelope 1; its test now pins envelope-1 constants — controller may want to note this in S20 evidence. (c) Envelope 2 admits only 1 new job/$0.50 because old rows remain unsettled liability.

Communication: silent; one completion message to controller.
