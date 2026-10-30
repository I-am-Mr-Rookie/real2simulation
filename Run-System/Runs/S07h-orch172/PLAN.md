# S07h-orch172 PLAN — held-out/robustness g on owner clips OWN02–OWN06 (frozen S07i pipeline)

Lane CLAUDE, anthropic/claude-opus-5-5/high (OpenCodex-managed; not polled). Issued 2026-10-30T23:44:12Z; cutoff 00:09:12Z; deadline 00:14:12Z.
Owns: evidence/S07/S07h/; Run-System/Runs/S07h-orch172/.

Objective: apply evidence/S07/S07i/measure_own01.py UNCHANGED (imported, constants untouched) to OWN02–OWN06 SAM 3.1 tracks
(canonical evidence/S07/S07i/track-own0N.json, controller batch run, untracked; SHA-256 recorded) -> g ± u or explicit abstain,
held-out residuals, table vs local 9.79 incl. OWN01, 05a/05b repeatability, coverage, failure modes.

Rules fixed here BEFORE any g on OWN02–06 was computed (committed before the first run):
1. Scale frames = first 5 tracked window frames = release−6 … release−2 from fixed evidence/S07/S07i/fall-windows.json
   (its window already reserves >= 5 held frames for box width). Same 0.2028 m edge, same 2 px edge / 0.5 mm allowances.
2. Release = S07i window(): first frame > median(scale frames y) + 8 px (unchanged).
3. Window end = min(last contiguous tracked frame [S07i rule], pre-registered fall end "increasing run to fN" in fall-windows.json).
   Reason: S07i tracks extend to fall end + 2 (post-impact frames); OWN01's window ended by SAM loss, not impact.
4. Split = S07i floor(2n/3) (unchanged). Uncertainty = S07i assume()/propagate_uncertainty + centroid-vs-box model term (unchanged).
5. Held-out PASS iff mask-centroid held-out RMSE <= 3 × DETECTION_STD_PX (6 px). Coverage reported at 1u and 2u vs 9.79.
6. Any FitAbstention / missing scale box / no release -> explicit abstain with the reason; no reruns with other parameters.
No Modal/GPU/Meta, no video reads, no tuning toward 9.79.
