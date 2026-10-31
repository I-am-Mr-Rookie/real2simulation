# S07h-orch176 REPORT — DONE

Lane CLAUDE; assigned anthropic/claude-opus-5-5/high (OpenCodex-managed; not polled). UTC start 2026-10-30T23:57:45Z (issue), end 2026-10-31T00:01:37+00:00.
Worktree .worktrees/S07h-orch176, branch run/S07h-orch176 from 25dca01e (main has since moved to ecd753db; controller rebases/merges).
Tokens/cost: unknown (not observable). No Modal/GPU/Meta/API spend; no video/frames to any model.

## Result (evidence/S07/S07h/README.md, results.json)
- 11 clips: 9 measured, OWN10 clutter + OWN11 lowres ABSTAIN (no release: SAM centroid drifts upward, never falls), OWN12 excluded.
- New: OWN07 05c 8.72 ± 0.21 (z −5.07), OWN08 05d 8.82 ± 0.27 (z −3.54), OWN09 nosheet 6.74 ± 1.77 (scale-box glitch f5 851 px).
- Coverage vs 9.79: 2/9 at 1u, 6/9 at 2u. Held-out pass 0/9 (OWN07–09 RMSE 73.0/87.8/99.5 px; impact frames dominate).
- 05a–d repeatability (valid 05a/c/d): 8.62/8.72/8.82, SD 0.10, weighted 8.76 ± 0.17, χ²/dof 0.05; 05b (7.12) flagged invalid.
  Precise but ~1 m/s² low → shared systematic. OWN01–OWN06 numbers byte-identical to orch172 (asserted).
- OWN11 units: S07i record() uses the record's 478×850 size → self-consistent m/px; px constants not rescaled (noted; moot, abstained).

## Pre-registration / integrity
PLAN.md + results-orch172.json snapshot committed (2ac7cc95), then script extension (d96884af), both BEFORE the first OWN07–11 run.
No rule/constant/script change after seeing results; only README text and results.json output followed.

## Ponytail (full) — concrete choices
- Reuse: no new pipeline; same measure_heldout.py importing frozen S07i measure_own01.py; plan() reused on the S07j windows file.
- Smallest complete change: input-only track map (rules.update(s07j)) guarded by an assert that S07j windows == S07i except "out";
  PENDING removed (now empty); repeatability() is the only new logic (+ tiny assert test in --self-check).
- Byte-identity of OWN01–06: compared json.dumps of rows/clips to an unchanged copy of the orch172 results (results-orch172.json),
  instead of re-deriving from git at run time.
- Skipped: viewing frames to confirm OWN10/11 SAM identity (forbidden: no frames to model); any rule fix (v2 = S07k, untouched).

## Fresh checks
- python -B evidence/S07/S07h/measure_heldout.py --self-check → "self-check OK" + "S07h self-check OK" (incl. byte-identity, 11 rows).
- python -B evidence/S07/S07h/measure_heldout.py → table above, results.json written.
- python -B -m unittest discover -s tests/measurement -t tests/measurement → Ran 90 tests, OK (skipped=1).
- python Run-System/worker_timebox.py check Run-System/Runs/S07h-orch176/TIMEBOX.json (see below).

## Files
evidence/S07/S07h/measure_heldout.py, README.md, results.json, results-orch172.json (new snapshot);
Run-System/Runs/S07h-orch176/PLAN.md, TIMEBOX.json, REPORT.md.

## Limits / risks
- OWN02–06 tracks live only in the canonical checkout (untracked); OWN07–11 tracks are on main (S07j). SHA-256 per clip in results.json.
- OWN10/OWN11 abstain cause (wrong/static object tracked) is inferred from centroid y only; identity not verified.
- Stated u under-covers systematics (05 repeats z −3.5…−5.1). Not a validated measurement; v2 (S07k) is the fix path.
- Completion message: app thread-messaging tool (mcp__codex_app) was removed from this session's catalog mid-run; final line returned in
  this chat instead. Communication: silent otherwise.

## Next
Controller: review + merge run/S07h-orch176; feed failure modes 6–7 (identity check, scale outlier guard) into S07k pre-registration.

