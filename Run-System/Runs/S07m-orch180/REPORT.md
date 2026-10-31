# S07m-orch180 REPORT — DONE

- Lane/model: CLAUDE, anthropic/claude-opus-5-5/high. Coding quota: OpenCodex-managed; not polled. Tokens/cost: unknown (not observable); $0 cloud (no Modal/GPU/Meta call; no video/frames to any model).
- UTC: issued 2026-10-31T00:18:09Z, work stopped 2026-10-31T00:21:57+00:00, deadline 00:48:09Z. Base main 7d59cfc2; branch run/S07m-orch180.
- Commit order (pre-registration evidence): ec2b2c3b PLAN.md -> 5296bd62 measure_v3.py + self-check -> single real run -> this commit (results/README/REPORT/TIMEBOX).

## Result (evidence/S07/S07m/README.md, results.json)
- v3 PASS (all with no in-window impact): v1 1/9 (OWN05); v2 4/6 (OWN02, OWN05, OWN07, OWN08). Abstentions unchanged (v1 OWN10/11; v2 OWN01/06/09/10/11).
- Coverage vs 9.79: all v1 2/9 in 1u, 6/9 in 2u; v2 4/6, 5/6. PASS-only: v1 1/1 in 1u; v2 3/4 in 1u and 2u.
- Bottom line: OWN05 (both sets), OWN02/OWN07/OWN08 (v2) are CONDITIONAL measurements; no clip is an unconditionally validated phone measurement. v3 is low-power (3-5 held frames) and passed v2 OWN08 (g 8.82 +/- 0.27, ~3.6u off 9.79), so it does not catch systematic bias. Unverified: user-declared scale, phone clock, rolling shutter (assumed 20 ms), centroid drift 10-13 px and blur/height growth in every passing window. Third analysis after seeing v1/v2 fail (forking paths) — stated in PLAN before the run.

## Files
- Run-System/Runs/S07m-orch180/PLAN.md, TIMEBOX.json, REPORT.md
- evidence/S07/S07m/measure_v3.py, results.json, README.md (table generated; "Interpretation" section hand-written after the run)

## Checks (fresh)
- python -B evidence/S07/S07m/measure_v3.py --self-check -> "S07m self-check OK (synthetic)".
- python -B evidence/S07/S07m/measure_v3.py -> real run; held RMSE of every window reproduced its S07h/S07k row (<0.05 px assert in diagnose.run()).
- python -B -m unittest discover -s tests/measurement -t tests/measurement -> Ran 90, OK (skipped=1).
- python Run-System/worker_timebox.py check ...TIMEBOX.json -> "TIMING PASS".

## Ponytail (applied, full)
- Reuse: v3 is NOT reimplemented; measure_v3.py imports S07l diagnose (run/analyse/V3_ALPHA/DETECT_PX), which chains S07k -> S07h -> S07i helpers. Only new code: per-window join with S07h/S07k rows, coverage counts, README table (~60 lines) + synthetic self-check (impact window FAIL, exact quadratic PASS, aggregation counts).
- g/u/z/in_1u/in_2u copied from pipeline rows, not recomputed.
- Skipped: no new fit, no cubic/drag/blur modelling, no re-tracking, no new windows, no tests/ additions (Owns excludes tests/).

## Deviation (disclosed)
- The real run was executed twice: after the first run the bottom_line string listed clip names without window-set tags (ambiguous). Fixed formatting only (one line) and re-ran; verified rows and coverage identical to the first run (python json compare: True True). No rule, threshold, window or number changed.

## Risks / next
- v3 PASS must not be presented as accuracy validation; OWN08 counterexample. A calibrated reference (known-g check or independent scale/clock) is still required for a validated phone measurement.
- Communication: silent; one completion line to controller. Canonical controls not edited.

