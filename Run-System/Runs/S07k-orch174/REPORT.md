# S07k-orch174 REPORT — DONE

- Lane CLAUDE; model anthropic/claude-opus-5-5/high (as assigned). Coding quota: OpenCodex-managed; not polled. Tokens/cost:
  unknown (unobservable). No Modal/GPU/Meta/paid call. Issued 2026-10-30T23:50:31Z; work stopped 2026-10-30T23:57Z (DONE early).
- Worktree `.worktrees/S07k-orch174`, branch `run/S07k-orch174` from main 032b06aa. Not merged (controller acceptance).

## Order (pre-registration)
1. fee5d1e3 PLAN.md fixes v2 rule. 2. 8517698f measure_v2.py committed after a synthetic-only self-check, before any real run.
3. One real run -> results.json. 4. README/REPORT text only; no script edits after results.

## Results (evidence/S07/S07k/README.md, results.json)
v2 measured 4/6 (OWN01, OWN06 ABSTAIN); held-out pass 0/4 (v1 0/6); in 1u 3/4, in 2u 4/4 vs 9.79. OWN05 6.5 px (threshold 6).
OWN07–OWN11 pending (0-frame tracks, S07j). Forking-paths caveat stated plainly in README.

## Checks (fresh)
- `python -B evidence/S07/S07k/measure_v2.py --self-check` -> "S07k self-check OK (synthetic only)".
- `python -B evidence/S07/S07k/measure_v2.py` (once) -> table above.
- `python -B -m unittest discover -s tests/measurement -t tests/measurement` -> Ran 86, OK (skipped=1).
- `python Run-System/worker_timebox.py check Run-System/Runs/S07k-orch174/TIMEBOX.json` (see commit).

## Ponytail (full) applied
- Reuse: imported S07h `measure_heldout` (locate, _Bytes, row, FROZEN, PENDING) and S07i `measure_own01.run()` unchanged;
  swapped only `window/SCALE_FRAMES/TRACK` (S07h pattern) instead of copying fit/uncertainty code. ~150-line single script.
- Smallest complete: one rule function + per-clip wrapper + table; self-check is 3 synthetic asserts (release/scale/impact,
  width-change abstain, static abstain). No Build/ or tests/ edits, no new deps, no options.
- Skipped: OWN07–OWN11 (no frames), per-clip end-reason field (not required), box-centre-derived window (v2 window fixed from
  centroid for both points, declared), plots.

## Risks / limits
- Forking paths: author saw v1 failures and the OWN02 trace before fixing the rule; v2 is a second analysis, not confirmation.
- Held-out still fails everywhere -> declared error model (2 px) is rejected; g ± u stays conditional, no gate claim.
- Inputs are canonical untracked track files (SHA-256 recorded); scale is user-declared, phone clock unverified.
- Controller-chat completion message tool (mcp__codex_app) was removed from this session's catalog mid-run; the final line
  is delivered as this worker's reply instead.

Communication: silent; no optional narration; one final line.

