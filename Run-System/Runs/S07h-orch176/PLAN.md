# S07h-orch176 PLAN — resume: OWN07–OWN11 with the UNCHANGED S07h-orch172 rules

Lane CLAUDE, anthropic/claude-opus-5-5/high (OpenCodex-managed; not polled). Issued 2026-10-30T23:57:45Z; cutoff 00:22:45Z; deadline 00:27:45Z.
Owns: evidence/S07/S07h/; Run-System/Runs/S07h-orch176/.

Objective: run evidence/S07/S07h/measure_heldout.py logic unchanged on OWN07–OWN11 (S07j re-tracks), full 11-clip table.

Fixed BEFORE any OWN07–11 g is computed (this file + script committed before the first run):
1. Rules 1–6 of Run-System/Runs/S07h-orch172/PLAN.md unchanged (scale = release−6…release−2; S07i +8 px release; end = min(contiguous,
   pre-registered fall end); split floor(2n/3); held-out PASS iff RMSE <= 6 px; abstain on fit/scale/release failure, no reruns).
2. Only input change: track path map. OWN07–11 tracks from evidence/S07/S07j/fall-windows-own07-11.json ("out"); the script asserts
   every S07j window entry equals the S07i fall-windows.json entry except "out". OWN02–06 keep S07i tracks.
3. FROZEN S07i constants + HELD_PASS_PX asserted unchanged. --self-check asserts OWN01–OWN06 rows/clips are byte-identical
   (json.dumps) to the orch172 results.json, snapshotted unchanged as evidence/S07/S07h/results-orch172.json.
4. OWN11 (478x850 re-encode): handled exactly as S07i record() — normalized SAM box x record width/height -> native-pixel units;
   px constants (2 px detection, 8 px release, 6 px held-out) stay in native pixels (no rescaling; reported as a limitation).
5. Repeatability 05a–d: OWN05, OWN07, OWN08 valid; OWN06 (05b) reported but flagged invalid (rule premise violated, orch172).
   Report mean, sample SD, min–max, chi2/dof vs weighted mean. Robustness: OWN09 nosheet, OWN10 clutter, OWN11 lowres; OWN12 excluded.
6. Coverage vs 9.79 at 1u/2u and held-out pass count over all measured clips. No Modal/GPU/Meta, no video/frames, no tuning toward 9.79.
