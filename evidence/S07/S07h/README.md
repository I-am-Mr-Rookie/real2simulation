# S07h — owner clips OWN02–OWN06: held-out / robustness g with the frozen S07i pipeline

**Label: MEASURED per clip** (real SAM 3.1 tracks; user-declared scale 0.2028 m book edge; phone clock NOT externally verified).
Local g = 9.79 m/s² is used for comparison only; nothing was tuned toward it.

- Script: `python evidence/S07/S07h/measure_heldout.py [--self-check]` (run from repo root). It **imports**
  `evidence/S07/S07i/measure_own01.py` (record/window/assume/run, Build/measurement free_fall + uncertainty) and asserts its
  constants are unchanged (0.2028 m ± 0.5 mm, 2 px box edge, 2 px detection, 1e-4 s PTS, 0.1 % clock, 8 px release).
- Inputs: controller batch tracks `evidence/S07/S07i/track-own0{2..6}.json` (canonical checkout, untracked; SHA-256 per clip in
  `results.json`), fixed `evidence/S07/S07i/fall-windows.json`, `evidence/S07/S07i/result-own01.json`. No video, Modal, GPU or Meta call.
- Rules were pre-registered in `Run-System/Runs/S07h-orch172/PLAN.md` (commit 815c59d3) and the script committed before the first run:
  scale frames = release−6…release−2 from fall-windows.json; release = S07i +8 px rule; end = min(contiguous track, pre-registered
  fall end); split ⌊2n/3⌋; held-out PASS iff RMSE ≤ 6 px (3 × declared 2 px); coverage at 1u/2u.

## Results (`results.json`)

| clip | scene | g ± u (m/s²) | z vs 9.79 | in 2u | fall frames (n) | held-out RMSE px | held-out |
|---|---|---|---|---|---|---|---|
| OWN01 | 01 (S07i) | 10.96 ± 0.77 | +1.52 | yes | f47–54 (8) | 23.0 | FAIL |
| OWN02 | 02_live_check | 9.29 ± 0.32 | −1.57 | yes | f47–59 (13) | 39.6 | FAIL |
| OWN03 | 03_test_clean | 9.54 ± 0.63 | −0.39 | yes | f45–57 (13) | 87.3 | FAIL |
| OWN04 | 04_test_shadow | 10.39 ± 0.46 | +1.31 | yes | f46–55 (10) | 35.1 | FAIL |
| OWN05 | 05_repeat_a | 8.62 ± 1.28 | −0.91 | yes | f44–50 (7) | 13.0 | FAIL |
| OWN06 | 05_repeat_b (sheet partly down) | 7.12 ± 1.02 ⚠ | −2.63 | no | f48–55 (8) | 119.1 | FAIL |

u = S07i conditional total ⊕ |centroid − box-centre| model term. ⚠ OWN06 violates the rule premise (see below): report, do not use.

- **Coverage vs 9.79:** 2/6 intervals contain 9.79 at 1u, 5/6 at 2u. **Held-out: 0/6 pass** → no clip is a validated measurement;
  the g values are prefix-fit numbers with a failed out-of-sample check, exactly like OWN01.
- **Spread:** six values 7.12–10.96 (OWN02–05 only: 8.62–10.39). Some pairs disagree beyond their u (e.g. OWN04 − OWN02 =
  1.10 ± 0.56, z ≈ 2.0) → the stated u likely under-covers real systematics.
- **Repeatability 05a vs 05b:** 8.62 − 7.12 = 1.51 ± 1.63 (z 0.92), but 05b is invalid (premise violated), so this is not a usable
  repeatability figure. **05c/05d (OWN07/OWN08) pending**: CUDA OOM in the batch track; S07j re-tracks.
- **Robustness clips:** 06 nosheet / clutter / lowres (OWN09–OWN11) pending (OOM, S07j). Front cover OWN12 excluded (no free fall, S07i).

## Failure modes (diagnosed from the tracks after the fit; no rule or parameter was changed)

1. **Impact frame inside the pre-registered window** (OWN02 f59, OWN03 f57, OWN06 f55): the colour rule's "strictly increasing run"
   ends at the floor contact, so the last held-out frame is a landing/decelerating frame → −80, −186, −204 px residuals dominate RMSE.
   Next pre-registration should end at fall end − 1 (decide before fitting new clips).
2. **Systematic later-fall deficit** (OWN01–04): held-out residuals are all negative and growing even before the impact frame
   (e.g. OWN04 −6…−58 px with SAM loss after f55, OWN02 −11…−28 px): the prefix acceleration over-predicts the lower fall. Consistent with
   non-uniform image scale (perspective / lens / book not in the scale plane as it drops) and **book rotation** — SAM box height grows
   ~218→313 px (OWN02), 217→304 px (OWN03) during the fall, moving the mask centroid relative to the body. Single-plane scale is unverified.
3. **Release push / misdetected release (OWN06)**: SAM y moves 338→722 px across the "held" scale frames f45–49 (box-width sd 5.1 px vs
   0.6–1.5 px elsewhere); the colour release (f51, sheet partly down) was late, so the scale frames are in motion and the fit starts mid-fall.
   The g = 7.12 is reported but the clip fails the method's premise. 05b/OWN06 needs a re-registered window.
4. **Short windows (OWN05)**: colour fall end f50 while SAM y keeps increasing to f52 → 7 frames, 4 training (1 dof beyond 3 params): large u (1.28).
   Held-out residuals here are positive (+5…+20 px), opposite sign to OWN01–04.
5. **SAM loss** (OWN04 f56–60 missing): window ended by contiguity at f55, as for OWN01 (f55–60).

Bottom line: on 6 owner clips the frozen S07i pipeline gives g within 2u of 9.79 on 5/6 clips but **fails held-out prediction on all 6**;
it is not yet a validated phone measurement. Fixes need new pre-registered rules (end before impact, release check on SAM y, rotation-robust
point / scale), then re-run on OWN07–OWN11 once S07j tracks them.

