# S07m - v3 predictive held-out check (THIRD analysis)

THIRD ANALYSIS (v3, pre-registered after seeing v1/v2 fail; forking-paths caveat) - MEASURED owner-clip SAM 3.1 tracks; user-declared scale, phone clock unverified, rolling shutter assumed

Rules: ../../../Run-System/Runs/S07m-orch180/PLAN.md. Script: measure_v3.py. Data: results.json.

| set | clip | frames | g +/- u (m/s^2) | in 1u/2u | held RMSE px | sigma px | chi2/dof | p | v3 | impact | max w/h change | h~speed r | centroid drift px | RS20ms px |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| v1 | OWN01 | f47-f54 | 10.96 +/- 0.77 | N/Y | 23.0 | 2.00 | 12.3/3 | 0.0065 | FAIL | N | 0.10/0.07 | 0.65 | 8.07 | 3.75 |
| v1 | OWN02 | f47-f59 | 9.29 +/- 0.32 | N/Y | 39.6 | 3.84 | 26.1/5 | 8.5e-05 | FAIL | N | 0.21/0.48 | 0.44 | 10.64 | 12.95 |
| v1 | OWN03 | f45-f57 | 9.54 +/- 0.63 | Y/Y | 87.3 | 4.09 | 88.7/5 | 1.2e-17 | FAIL | Y | 0.09/0.44 | 0.92 | 23.44 | 14.10 |
| v1 | OWN04 | f46-f55 | 10.39 +/- 0.46 | N/Y | 35.1 | 2.00 | 44.6/4 | 4.9e-09 | FAIL | N | 0.10/0.10 | 0.92 | 11.38 | 7.73 |
| v1 | OWN05 | f44-f50 | 8.62 +/- 1.28 | Y/Y | 13.0 | 2.00 | 2.3/3 | 0.51 | PASS | N | 0.03/0.16 | 0.60 | 13.28 | 1.62 |
| v1 | OWN06 | f48-f55 | 7.12 +/- 1.02 | N/N | 119.1 | 2.95 | 122.3/3 | 2.4e-26 | FAIL | Y | 0.06/0.19 | 0.93 | 13.95 | 2.08 |
| v1 | OWN07 | f47-f59 | 8.72 +/- 0.21 | N/N | 73.0 | 3.71 | 68.0/5 | 2.7e-13 | FAIL | Y | 0.18/0.51 | 0.79 | 16.79 | 10.79 |
| v1 | OWN08 | f36-f48 | 8.82 +/- 0.27 | N/N | 87.8 | 2.82 | 167.3/5 | 2.7e-34 | FAIL | Y | 0.07/0.32 | 0.81 | 11.56 | 11.93 |
| v1 | OWN09 | f9-f22 | 6.74 +/- 1.77 | N/Y | 99.5 | 2.69 | 373.1/5 | 1.8e-78 | FAIL | Y | 0.34/0.48 | 0.79 | 31.51 | 16.50 |
| v2 | OWN02 | f46-f53 | 7.27 +/- 3.07 | Y/Y | 20.5 | 3.21 | 5.1/3 | 0.16 | PASS | N | 0.08/0.18 | 0.93 | 10.97 | 1.64 |
| v2 | OWN03 | f45-f56 | 9.56 +/- 0.63 | Y/Y | 28.9 | 4.09 | 18.6/4 | 0.00095 | FAIL | N | 0.05/0.44 | 0.97 | 19.52 | 9.82 |
| v2 | OWN04 | f46-f55 | 10.40 +/- 0.46 | N/Y | 35.1 | 2.00 | 44.6/4 | 4.9e-09 | FAIL | N | 0.10/0.10 | 0.92 | 11.38 | 7.73 |
| v2 | OWN05 | f44-f52 | 9.62 +/- 0.74 | Y/Y | 6.5 | 2.00 | 3.5/3 | 0.33 | PASS | N | 0.03/0.22 | 0.83 | 13.28 | 3.61 |
| v2 | OWN07 | f46-f54 | 9.51 +/- 0.93 | Y/Y | 7.0 | 2.00 | 3.5/3 | 0.32 | PASS | N | 0.04/0.21 | 0.96 | 10.17 | 3.55 |
| v2 | OWN08 | f36-f47 | 8.82 +/- 0.27 | N/N | 17.8 | 2.82 | 9.0/4 | 0.061 | PASS | N | 0.07/0.32 | 0.85 | 11.46 | 8.32 |

Abstained: v1 OWN10 (StopIteration: ); v1 OWN11 (StopIteration: ); v2 OWN01 (v2 rule: fall window f47-f53 has 7 < 8 frames); v2 OWN06 (v2 rule: only 0 tracked scale frames before release f46); v2 OWN09 (v2 rule: fall window f9-f9 has 1 < 8 frames); v2 OWN10 (v2 rule: no sustained centroid-y release); v2 OWN11 (v2 rule: no sustained centroid-y release)

Coverage vs 9.79 (copied S07h/S07k flags): {"v1": {"all_measured": {"n": 9, "in_1u": 2, "in_2u": 6}, "v3_pass_only": {"n": 1, "in_1u": 1, "in_2u": 1}, "v3_pass": 1, "validated_conditional": 1}, "v2": {"all_measured": {"n": 6, "in_1u": 4, "in_2u": 5}, "v3_pass_only": {"n": 4, "in_1u": 3, "in_2u": 3}, "v3_pass": 4, "validated_conditional": 4}}

**Bottom line:** validated (conditional) windows: v1 OWN05, v2 OWN02, v2 OWN05, v2 OWN07, v2 OWN08.

## Interpretation (hand-written after the single run; numbers above are script output)

- Frozen PLAN rule: v3 PASS and no in-window impact = "validated (conditional)". Result: v1 1/9 windows (OWN05); v2 4/6 windows (OWN02, OWN05, OWN07, OWN08). Only OWN05 passes in BOTH window sets. Every v1 window with an S07l-flagged impact fails.
- Coverage vs 9.79 (copied S07h/S07k flags): all measured v1 2/9 in 1u, 6/9 in 2u; v2 4/6 in 1u, 5/6 in 2u. v3-PASS only: v1 1/1 in 1u; v2 3/4 in 1u, 3/4 in 2u.
- Limits of v3 itself: only 3-5 held frames, and the leverage term inflates allowed error, so power is low: v2 OWN02 passes with 20.5 px held RMSE (g 7.27 +/- 3.07). v2 OWN08 passes (p 0.061) while its g = 8.82 +/- 0.27 is ~3.6 u below 9.79 - v3 does NOT detect the systematic bias. Passing v3 = "the quadratic predicts the next frames within its own error bars", not "g is accurate".
- Bias sources still present in every passing window (S07l, reported alongside, not gating): centroid-minus-box drift 10-13 px; box height growth with speed (r 0.60-0.96, motion blur/rotation); rolling shutter can add 1.6-8.3 px held RMSE at an ASSUMED 20 ms readout.

**Plain bottom line:** under the pre-registered v3 rule, OWN05 (both window sets) and OWN02/OWN07/OWN08 (v2 windows only) are conditional measurements whose fall is predictively consistent with constant acceleration. No clip is an unconditionally validated phone measurement of g: scale is user-declared (0.2028 m), the phone clock is not externally verified, rolling-shutter readout is assumed, centroid/blur bias is unmodelled, and v3 is a third analysis chosen after v1/v2 failed (forking paths) with low power, already shown unable to flag a 3.6 u miss (v2 OWN08).

