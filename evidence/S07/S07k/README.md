# S07k — SECOND ANALYSIS (v2): pre-registered track-internal fall-window rule on owner clips

**Label: MEASURED per clip, SECOND ANALYSIS (v2)** — real SAM 3.1 tracks; user-declared scale 0.2028 m book edge; phone
clock NOT externally verified. Local g = 9.79 m/s² is a comparison only; no rule was chosen by g vs 9.79.

**Forking-paths caveat (plain):** this is a second analysis of the same six clips after v1 (S07h) failed held-out on all of
them. The rule was written after reading the v1 failure modes and after seeing the OWN02 y-trace. Pre-registration
(PLAN commit fee5d1e3, script commit 8517698f, both before the one real run) limits but does not remove that bias. v2 is
NOT independent confirmation; any agreement with 9.79 here is weaker evidence than a first, blind analysis would be.
OWN07–OWN11 (orch178) are the closest thing to out-of-sample for v2: the rule was frozen before their tracks existed and
was applied unchanged (mapping commit 42e736a0 before the one real run). Same scene/operator/phone, so still not independent.

- Script: `python evidence/S07/S07k/measure_v2.py [--self-check]` from repo root. It imports S07h `measure_heldout`
  (locate/_Bytes/row/FROZEN/PENDING) and through it the frozen S07i `measure_own01` (record/run/assume, Build/measurement
  free_fall + uncertainty); asserts S07i constants unchanged; swaps only `window`, `SCALE_FRAMES`, `TRACK` per clip.
- Rule (Run-System/Runs/S07k-orch174/PLAN.md): release R = first frame with centroid-y step > 4 px and next step > 4 px;
  scale = up to 5 contiguous frames ending at R−2, ≥3 needed, y range ≤ 6 px; window ends before box-width change > 10 %
  vs scale mean, velocity halving, or SAM gap; ≥ 8 fall frames else ABSTAIN; split ⌊2n/3⌋; held-out PASS iff RMSE ≤ 6 px.
- Inputs: `evidence/S07/S07g/track-own01.json`, `evidence/S07/S07i/track-own02..06.json`,
  `evidence/S07/S07j/track-own07..11.json` (S07j re-track; SHA-256 per clip in results.json).
  No video, frames, Modal, GPU or Meta call.
- orch178 asserts (run() and `--self-check`): v2 constants equal the orch174 values; OWN01–OWN06 rows+clips SHA-256
  = 41ce6dd7… (orch174 results.json), i.e. byte-identical. Only the input mapping and the "pending S07h" table cell changed.

## v1 (S07h) vs v2 (`results.json`)

| clip | v1 g ± u (m/s²), window | v1 held-out RMSE px | v2 g ± u (m/s²), window | v2 held-out RMSE px |
|---|---|---|---|---|
| OWN01 | 10.96 ± 0.77 (z +1.52) f47–54 n=8 | 23.0 FAIL | ABSTAIN: window f47–f53 has 7 < 8 frames | – |
| OWN02 | 9.29 ± 0.32 (z −1.57) f47–59 n=13 | 39.6 FAIL | 7.27 ± 3.07 (z −0.82) f46–53 n=8 | 20.5 FAIL |
| OWN03 | 9.54 ± 0.63 (z −0.39) f45–57 n=13 | 87.3 FAIL | 9.56 ± 0.63 (z −0.37) f45–56 n=12 | 28.9 FAIL |
| OWN04 | 10.39 ± 0.46 (z +1.31) f46–55 n=10 | 35.1 FAIL | 10.40 ± 0.46 (z +1.33) f46–55 n=10 | 35.1 FAIL |
| OWN05 | 8.62 ± 1.28 (z −0.91) f44–50 n=7 | 13.0 FAIL | 9.62 ± 0.74 (z −0.23) f44–52 n=9 | 6.5 FAIL |
| OWN06 | 7.12 ± 1.02 (z −2.63) f48–55 n=8 | 119.1 FAIL | ABSTAIN: 0 tracked scale frames before release f46 | – |
| OWN07 | 8.72 ± 0.21 (z -5.07) f47–59 n=13 | 73.0 FAIL | 9.51 ± 0.93 (z -0.30) f46–54 n=9 | 7.0 FAIL |
| OWN08 | 8.82 ± 0.27 (z -3.54) f36–48 n=13 | 87.8 FAIL | 8.82 ± 0.27 (z -3.54) f36–47 n=12 | 17.8 FAIL |
| OWN09 | 6.74 ± 1.77 (z -1.72) f9–22 n=14 | 99.5 FAIL | ABSTAIN (v2 rule: fall window f9-f9 has 1 < 8 frames) | – |
| OWN10 | ABSTAIN (StopIteration: ) | – | ABSTAIN (v2 rule: no sustained centroid-y release) | – |
| OWN11 | ABSTAIN (StopIteration: ) | – | ABSTAIN (v2 rule: no sustained centroid-y release) | – |

v2 scale frames: OWN02 f42–44, OWN03 f40–43, OWN04 f41–44, OWN05 f39–42, OWN07 f40–44, OWN08 f30–34. u = S07i conditional
total ⊕ |centroid − box-centre| model term (OWN02's 3.07 is dominated by that term: centroid 7.27 vs box 10.27).
v1 for OWN07–OWN11: S07h-orch176 had not merged at orch178 start (S07h results.json has OWN01–06 only) → "pending S07h".
Controller fix at acceptance (2026-10-31T00:12Z): after S07h-orch176 merged, measure_heldout no longer exported PENDING; measure_v2.py now names the S07j re-tracked clips locally (RETRACKED) and the v1 cells above come from the merged S07h results.json. Rerun: every v2 g/u/window/held-out value identical to orch178 (only OWN09-11 scene labels now use S07h names); coverage unchanged.

## Coverage (11 clips)
- v2: 11 clips, 6 measured, 5 ABSTAIN. Within 1u of 9.79: 4/6 (OWN02, OWN03, OWN05, OWN07). Within 2u: 5/6 (adds OWN04
  z +1.33; OWN08 z −3.54 is outside 2u). OWN01–06 subset unchanged from orch174 (3/4 at 1u, 4/4 at 2u).
- **Held-out pass: 0/6 (v1: 0/6 on OWN01–06).** Closest: OWN05 6.5 px, OWN07 7.0 px vs 6 px threshold. OWN08 first three
  held-out residuals are small (0.4, −2.3, 4.1 px) then −35.2 px at f47 — impact/decel frame survives the window rule.
- Abstains: OWN01 (7-frame window), OWN06 (no static pre-release frames), OWN09, OWN10, OWN11 (see robustness).
- OWN12 excluded (no free fall).

## 05a–d repeatability (same scene, four drops)
- OWN05 (05a) 9.62 ± 0.74, OWN07 (05c) 9.51 ± 0.93, OWN08 (05d) 8.82 ± 0.27; **OWN06 (05b) flagged: sheet partly down,
  v2 ABSTAIN**. Measured three: mean 9.32, sample SD 0.43 m/s² (n=3; not a precision claim). OWN08's 8.82 disagrees with
  OWN05/07 beyond its stated u (0.27), so the per-clip u under-states drop-to-drop spread.

## Robustness (S07j re-tracks, rule unchanged)
- **06 nosheet (OWN09):** centroid fall is clear (y 295→1620 px), but the scale frames f4–f7 include a SAM box-width outlier
  (f5 = 851 px vs ~315 px) that inflates the scale-mean width; f10 then trips the 10 % width stop → 1-frame window → ABSTAIN.
  A SAM glitch, not physics; the frozen rule has no outlier rejection and was not changed.
- **06 clutter (OWN10)** and **06 lowres 478×850 (OWN11):** SAM centroid barely moves (y 195→169 and 73→67 px, constant
  box width) over the tracked windows, so no release is detected → ABSTAIN. The tracks do not follow a falling book there
  (likely wrong object or clutter/low-res tracking failure; not verified against frames — no frames viewed in this run).
- Net: v2 abstains rather than reporting g on all three robustness clips; it does not show robustness to clutter/low-res.

## What this does and does not show
- Shows: a track-only rule removes impact frames inside the window for OWN03 and abstains on the two clips v1 should not
  have measured; held-out RMSE falls on OWN02/03/05.
- Does not show: a validated measurement. No clip passes the pre-registered 6 px held-out test, so per-clip g ± u remains
  conditional on the declared error model, which the held-out residuals reject. The 2u coverage is not a gate pass.

