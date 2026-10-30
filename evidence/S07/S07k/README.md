# S07k — SECOND ANALYSIS (v2): pre-registered track-internal fall-window rule on owner clips

**Label: MEASURED per clip, SECOND ANALYSIS (v2)** — real SAM 3.1 tracks; user-declared scale 0.2028 m book edge; phone
clock NOT externally verified. Local g = 9.79 m/s² is a comparison only; no rule was chosen by g vs 9.79.

**Forking-paths caveat (plain):** this is a second analysis of the same six clips after v1 (S07h) failed held-out on all of
them. The rule was written after reading the v1 failure modes and after seeing the OWN02 y-trace. Pre-registration
(PLAN commit fee5d1e3, script commit 8517698f, both before the one real run) limits but does not remove that bias. v2 is
NOT independent confirmation; any agreement with 9.79 here is weaker evidence than a first, blind analysis would be.

- Script: `python evidence/S07/S07k/measure_v2.py [--self-check]` from repo root. It imports S07h `measure_heldout`
  (locate/_Bytes/row/FROZEN/PENDING) and through it the frozen S07i `measure_own01` (record/run/assume, Build/measurement
  free_fall + uncertainty); asserts S07i constants unchanged; swaps only `window`, `SCALE_FRAMES`, `TRACK` per clip.
- Rule (Run-System/Runs/S07k-orch174/PLAN.md): release R = first frame with centroid-y step > 4 px and next step > 4 px;
  scale = up to 5 contiguous frames ending at R−2, ≥3 needed, y range ≤ 6 px; window ends before box-width change > 10 %
  vs scale mean, velocity halving, or SAM gap; ≥ 8 fall frames else ABSTAIN; split ⌊2n/3⌋; held-out PASS iff RMSE ≤ 6 px.
- Inputs: `evidence/S07/S07g/track-own01.json`, `evidence/S07/S07i/track-own02..06.json` (SHA-256 per clip in results.json).
  No video, frames, Modal, GPU or Meta call.

## v1 (S07h) vs v2 (`results.json`)

| clip | v1 g ± u (m/s²), window | v1 held-out RMSE px | v2 g ± u (m/s²), window | v2 held-out RMSE px |
|---|---|---|---|---|
| OWN01 | 10.96 ± 0.77 (z +1.52) f47–54 n=8 | 23.0 FAIL | ABSTAIN: window f47–f53 has 7 < 8 frames | – |
| OWN02 | 9.29 ± 0.32 (z −1.57) f47–59 n=13 | 39.6 FAIL | 7.27 ± 3.07 (z −0.82) f46–53 n=8 | 20.5 FAIL |
| OWN03 | 9.54 ± 0.63 (z −0.39) f45–57 n=13 | 87.3 FAIL | 9.56 ± 0.63 (z −0.37) f45–56 n=12 | 28.9 FAIL |
| OWN04 | 10.39 ± 0.46 (z +1.31) f46–55 n=10 | 35.1 FAIL | 10.40 ± 0.46 (z +1.33) f46–55 n=10 | 35.1 FAIL |
| OWN05 | 8.62 ± 1.28 (z −0.91) f44–50 n=7 | 13.0 FAIL | 9.62 ± 0.74 (z −0.23) f44–52 n=9 | 6.5 FAIL |
| OWN06 | 7.12 ± 1.02 (z −2.63) f48–55 n=8 | 119.1 FAIL | ABSTAIN: 0 tracked scale frames before release f46 | – |

v2 scale frames: OWN02 f42–44, OWN03 f40–43, OWN04 f41–44, OWN05 f39–42. u = S07i conditional total ⊕ |centroid − box-centre|
model term (OWN02's 3.07 is dominated by that term: centroid 7.27 vs box 10.27).

## Coverage
- v2: 6 clips, 4 measured, 2 ABSTAIN (OWN01 short window, OWN06 no static pre-release frames — v1's OWN06 "moving scale
  frames" failure now abstains instead of reporting). Within 1u of 9.79: 3/4; within 2u: 4/4.
- **Held-out pass: 0/4 (v1: 0/6).** OWN05 is closest (6.5 px vs 6 px threshold). OWN03/OWN04 held-out residuals still grow
  monotonically (−15…−46, −6…−58 px): the later-fall deficit is NOT explained by the window rule alone.
- Pending: OWN07–OWN11 (track files had 0 frames at start; CUDA OOM, S07j). OWN12 excluded (no free fall).

## What this does and does not show
- Shows: a track-only rule removes impact frames inside the window for OWN03 and abstains on the two clips v1 should not
  have measured; held-out RMSE falls on OWN02/03/05.
- Does not show: a validated measurement. No clip passes the pre-registered 6 px held-out test, so per-clip g ± u remains
  conditional on the declared error model, which the held-out residuals reject. The 2u coverage is not a gate pass.

