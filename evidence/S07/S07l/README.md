# S07l — DIAGNOSIS: why held-out prediction fails on every owner clip

**Label: DIAGNOSIS derived from MEASURED real SAM 3.1 tracks; ASSUMPTIONS labelled; 9.79 never used to choose anything.**
Inputs only: `evidence/S07/S07g/track-own01.json`, `evidence/S07/S07i/track-own02..06.json`, `evidence/S07/S07j/track-own07..11.json` (paths via S07k `measure_v2.TRACKS`) and S07h/S07k `results.json` windows. No tracking, video, frames, model, Modal, GPU or Meta call.

- Script: `python -B evidence/S07/S07l/diagnose.py [--self-check]` from repo root. Imports S07k `measure_v2` (→ S07h `measure_heldout` → S07i `measure_own01` + Build.measurement) for track paths, `locate`, DECEL, 6 px threshold and 2 px declared error. Fits are pixel-space y(pts) quadratics on the SAME windows and floor(2n/3) split; the script **asserts** it reproduces every S07h/S07k held-out RMSE within 0.05 px (15/15 windows: 9 v1, 6 v2).
- Thresholds/assumptions fixed in the script before the real run: impact = step < 0.5× previous; shape change > 5 %; centroid–box drift > 3 px; VFR = PTS step range > 1 ms; rolling-shutter readout 20 ms (ASSUMPTION, Realme C53 unknown); drag ρ 1.2, Cd 1.2, mass 0.2–1.0 kg, area edge-on 2 cm .. face-on 30 cm × 0.2028 m (ASSUMPTIONS).
- Coverage: windows exist only where v1/v2 measured (v1 9 clips, v2 6 clips: OWN02/03/04/05/07/08). OWN10/11 never had a fall window; nothing here changes that.

## Hypothesis → statistic → verdict (`results.json` → `summary`)

| # | hypothesis | statistic (from data) | verdict |
|---|---|---|---|
| a | impact/landing inside window | v1: 5/9 windows contain a velocity step < 0.5× previous (v1 median held-out 73.0 px). v2: 0/6 (DECEL rule), median held-out 19.2 px. But local acceleration in the held-out third is **below** the training third in **6/6** v2 windows (e.g. OWN08 15.2 → 0.5, OWN07 16.7 → 6.6, OWN04 16.2 → 10.7 px/frame²). | **v1: SUPPORTED (main v1 cause). v2: hard impact EXCLUDED; late-window deceleration PRESENT 6/6, source not uniquely identified** (pre-contact, or b/c below). |
| b | book rotation / perspective | v2 6/6 windows exceed 5 % box change; median max |Δw| 6.1 %, |Δh| 21.8 %. Height growth vs speed: r median 0.92, slope 9.7–22.8 ms (what a 10–23 ms exposure blur streak would produce). Width (not blur-affected for vertical motion) drifts 3–10 %. | **PRESENT 6/6.** Height growth more consistent with motion-blur elongation (HYPOTHESIS) than rotation; width drift shows some rotation/depth change. |
| c | centroid vs box-centre / mask-shape bias | centroid − box-centre y drifts by median 11.4 px across the window (6/6 > 3 px; range 10.2–19.5). Box-centre held-out passes 1/6 (OWN07 3.5 px), better in 3/6, worse in 3/6. | **PRESENT and larger than the 6 px threshold; switching point type does NOT fix it** (no consistent winner). |
| d | linear/quadratic air drag | cubic (first-order drag) fit on train: held-out better 1/6, passes 0/6. Implied linear-drag k median 1.95 s⁻¹; required k·v = −3.0…+9.2 m/s² vs plausible flat-plate drag 0.00–1.03 m/s² → **0/6 plausible**. | **REJECTED.** |
| e | frame timing (VFR, rolling shutter) | PTS steps 33.33 ms in every clip (0 VFR; CFR rendition — S07g raw jitter 33.23–33.43 ms ⇒ ≤ 0.5 px). Rolling shutter, 20 ms readout ASSUMED: along portrait y → held-out up to 9.8 px, apparent a ×1.04–1.08; along portrait x → ≤ 1.1 px. | **VFR REJECTED. Rolling shutter UNRESOLVED** — minor if readout runs along portrait x (usual landscape-sensor mounting, ASSUMPTION); material if along y. Not measurable from tracks. |
| f | declared 2 px error too small | static pre-release scatter median 0.24 px; smooth-fall train residual sd median 2.01 px (0.83–4.09). **Expected held-out RMSE of an EXACT quadratic with the declared 2 px = 6.1–9.2 px (median 7.1) > 6 px in 6/6 v2 windows** (extrapolation leverage of 3–4 held frames from 5–8 train frames). Observed/expected (empirical σ) median 1.99. | **2 px is about right at the median (too small for OWN02/03/08: 2.8–4.1 px). The 6 px PASS threshold is structurally infeasible — SUPPORTED, primary reason "every clip fails".** The remaining ~2× excess is systematic (a/b/c). |
| g | scale error (box vs mask width) | scale-frame box width rel. sd median 0.36 % ⇒ g shift median 0.036 m/s² (consequence only). Held-out is computed in pixels, so it is scale-independent by construction (reproduced exactly without m/px). Mask width not computable (tracks store mask centroid + SAM box only). | **REJECTED as a held-out cause** (affects g only, slightly). |

Per-window numbers: `results.json` → `windows[]` (clip, analysis v1/v2, frames, every statistic above, v3 candidate).

## ONE recommended v3 change — HYPOTHESIS, not evidence

Replace the fixed "held-out RMSE ≤ 6 px" with a **pre-registered predictive χ² test**: σ = max(train residual sd, 2 px declared), per held frame variance σ²(1 + leverage) from the floor(2n/3) quadratic fit, PASS iff χ²(m held frames) p ≥ 0.05 (implemented as `v3_candidate` in the script).

- Why: under (f) a perfect quadratic with the declared noise is expected to miss 6 px in every v2 window, so 0/N says nothing about the physics. The χ² test asks the question the 6 px rule meant to ask.
- Expected effect (computed on already-seen windows ⇒ post-hoc, forking-paths, NOT confirmation): v2 4/6 would pass (OWN02 p 0.16, OWN05 0.33, OWN07 0.32, OWN08 0.061), OWN03 (p 0.001) and OWN04 (p 5e-9) still fail; v1 1/9. g values unchanged (test change only).
- Risks: σ from 5–8 train frames is noisy and is inflated by the same blur/shape systematics, making the test more lenient on messy clips; the late-window deceleration (a) and centroid drift (c) remain unfixed. Must be frozen before any NEW clips and judged only there.

