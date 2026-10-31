# S07m-orch180 PLAN — pre-registered v3 predictive check (written BEFORE any v3 run)

- Run: S07m-orch180 (QUEUE S07m, CLAUDE lane, step S07). Model anthropic/claude-opus-5-5/high; coding quota OpenCodex-managed; not polled.
- Issued 2026-10-31T00:18:09Z; deadline 00:48:09Z (Dhaka 06:48:09); minute-25 cutoff 00:43:09Z. Base main 7d59cfc2.
- Owns only: evidence/S07/S07m/; Run-System/Runs/S07m-orch180/.

## Objective
Apply ONE frozen predictive held-out test (v3) to the existing v1 (S07h) and v2 (S07k) fall windows of OWN01-OWN11 and report per clip g +/- u, held-out RMSE, chi-square, p, PASS/FAIL, S07l blur/rotation + centroid-drift numbers, coverage vs 9.79 (PASS-only and all), and a plain bottom line.

## Why v3 exists (honest framing)
- v1/v2 used "held-out RMSE <= 6 px", a threshold chosen before data. S07l showed it is miscalibrated: an EXACT quadratic with the declared 2 px detection error already gives expected held-out RMSE 6.1-9.2 px (median 7.1) from extrapolation leverage, so the test fails correct models.
- v3 corrects the test statistic; it does not change the goal (a validated predictive fit). It is a THIRD analysis. I have seen v1 and v2 fail on every window, and S07l's results.json already contains a "v3_candidate" p per window computed as a hypothesis (I have not read those numbers before this commit, but they exist). Forking-paths caveat: a PASS under v3 is weaker evidence than a pre-data PASS would be; the result must be read as exploratory-confirmatory, not as a blind pre-registered test.

## v3 rule (frozen)
For each window (frames f0..f1 of the pipeline, n frames, primary point = SAM 3.1 mask centroid y in px vs phone PTS):
1. Train = first floor(2n/3) frames; fit pixel y(t) quadratic (np.polyfit deg 2, t - t0) — same split and model as S07i/S07h/S07k.
2. sigma = max(train residual sd with n_train-3 dof, 2 px declared detection error).
3. Per held frame i: variance sigma^2 (1 + h_i), h_i = x_i'(X'X)^-1 x_i leverage of the training design.
4. chi2 = sum r_i^2 / (sigma^2 (1+h_i)), dof = number of held frames; p = chi2.sf.
5. PASS iff p >= 0.05. No other threshold, no window change, no outlier removal.
Implementation: reuse evidence/S07/S07l/diagnose.py analyse()/windows()/load() unchanged (its v3_candidate block is exactly this rule); measure_v3.py only imports it (which imports S07k -> S07h -> S07i helpers), adds the assert that held RMSE reproduces the pipeline row, and aggregates.

## Everything else frozen
- Windows: v1 = evidence/S07/S07h/results.json rows (v1 scale frames = up to 5 tracked frames ending 2 before release, as S07l); v2 = evidence/S07/S07k/results.json rows (rule scale_frames). Abstentions stay abstentions.
- g, u, z = (g-9.79)/u, in_1u, in_2u copied from those rows (same S07i fit/uncertainty). Nothing recomputed, nothing re-tracked.
- Coverage: count in_1u / in_2u for (a) v3 PASS windows only and (b) all measured windows, per window set.
- Alongside (reported, NOT gating): S07l b_shape (max width/height change, height-growth-vs-speed r), c_centroid offset range, a_impact flag, rolling-shutter (20 ms ASSUMED) held RMSE.
- 9.79 is used only for the coverage columns; nothing is selected or ranked by closeness to 9.79.

## Bottom-line rule (frozen)
A clip is called a "validated phone measurement (conditional)" only if its window PASSES v3 AND S07l flags no impact in window. Even then it stays conditional on: user-declared 0.2028 m scale, unverified phone clock, assumed (not measured) rolling-shutter readout, centroid/box drift. If no window passes: "no clip is a validated measurement".

## Checks
- python -B evidence/S07/S07m/measure_v3.py --self-check (synthetic only), committed before the single real run.
- python -B evidence/S07/S07m/measure_v3.py (single real run) -> results.json + README.md.
- python -B -m unittest discover -s tests/measurement -t tests/measurement.
- No Modal/GPU/Meta call; no video/frames to any model.

