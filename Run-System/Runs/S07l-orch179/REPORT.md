# S07l-orch179 REPORT — DONE

- Lane/model: CLAUDE, anthropic/claude-opus-5-5/high; coding quota OpenCodex-managed; not polled. Tokens/cost: unobservable; $0 compute (CPU-only, no Modal/GPU/Meta).
- UTC: issued 2026-10-31T00:09:37Z, worktree start 00:10:05Z, work stopped 2026-10-31T00:17:23+00:00; deadline 00:39:37Z. Branch run/S07l-orch179 from main e8d329fe.
- Files: evidence/S07/S07l/diagnose.py, results.json, README.md; Run-System/Runs/S07l-orch179/PLAN.md, TIMEBOX.json, REPORT.md.

## Result (details: evidence/S07/S07l/README.md)
Why held-out fails: (f) the fixed 6 px threshold is below the expected held-out RMSE of an EXACT quadratic with the declared 2 px noise in 6/6 v2 windows (6.1–9.2 px, median 7.1) — primary, structural. (a) v1: impact inside 5/9 windows (main v1 cause); v2 hard impact excluded but held-third acceleration < train-third in 6/6. (b)/(c) box height +22 % median, correlated with speed (r 0.92, slope 10–23 ms ⇒ blur-like) and centroid–box drift 10–20 px: systematic ~2x excess. (d) drag REJECTED (0/6 physically plausible, cubic held-out passes 0/6). (e) VFR rejected; rolling shutter unresolved (≤1.1 px if readout along portrait x, up to 9.8 px if along y; 20 ms readout ASSUMED). (g) scale REJECTED as held-out cause (pixel test is scale-independent; g shift median 0.036 m/s²).
ONE v3 change (HYPOTHESIS): pre-registered predictive χ² held-out test (σ = max(train sd, 2 px), variance σ²(1+leverage), p ≥ 0.05). Post-hoc effect on seen windows: v2 4/6, v1 1/9 — not evidence; freeze before new clips.

## Checks (fresh)
- `python -B evidence/S07/S07l/diagnose.py --self-check` → "S07l self-check OK (synthetic)".
- `python -B evidence/S07/S07l/diagnose.py` → results.json; asserts reproduction of all 15 S07h/S07k held-out RMSEs within 0.05 px (passed).
- `python -B -m unittest discover -s tests/measurement -t tests/measurement` → Ran 90 tests, OK (skipped=1).
- `python Run-System/worker_timebox.py check` on TIMEBOX.json (see below).

## Ponytail (full) applied
- Reuse: imports S07k measure_v2 (TRACKS, DECEL) → S07h measure_heldout (locate, HELD_PASS_PX) → S07i measure_own01 (DETECTION_STD_PX); no copied pipeline code. numpy/scipy (installed) for polyfit/chi2 instead of hand-rolled code.
- Smallest complete: one ~230-line script; pixel-space fits suffice because Build.measurement free_fall fits y(pts) only — proven by the reproduction assert rather than re-wrapping fit_free_fall per hypothesis.
- Skipped: mask-derived width (not stored in tracks), rolling-shutter direction (not knowable from tracks), lens distortion (no calibration), any new tracking/frames. OWN10/11 have no window in either analysis.
- Risks: assumptions (20 ms readout, drag constants, mass/area) labelled; v3 χ² effect is post-hoc on the same clips (forking paths); empirical σ from 5–8 frames is noisy and inflated by systematics (lenient).

## Communication
Silent run; one completion message to controller per contract. No canonical controls edited.

