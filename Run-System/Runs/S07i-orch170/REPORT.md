# S07i-orch170 REPORT — DONE

Lane CLAUDE; model anthropic/claude-opus-5-5 (high); coding quota OpenCodex-managed, not polled.
UTC start 2026-10-30T23:18:02Z (worktree from main 84b3ccc), end 2026-10-30T23:28:45+00:00. Tokens/cost: not observable; Modal $0 (no job run).

## Result
1. **OWN01 g = 10.96 ± 0.77 m/s² (1σ), MEASURED** (owner clip, user-declared 0.2028 m scale, phone clock not externally
   verified) vs local 9.79: +1.17, 1.5σ. Budget: fit 0.67, scale 0.08, timing 0.06, model (centroid vs box centre) 0.37.
   Fall f47–54 only (0.233 s; SAM lost the book f55–60, landing not included); train f47–51 (5 frames), held-out
   f52–54 residuals −2.1/−16.9/−36.1 px → **held-out FAILS**. Diagnostic 10.73 ± 0.41 difference explained
   (colour scale under-read 7 %, earlier/shorter SAM window). Details: evidence/S07/S07i/README.md, result-own01.json.
2. **Batch**: modal_track.py `--batch` → one admission, one container (track_batch), per-clip outputs; windows fixed in
   evidence/S07/S07i/fall-windows.json (OWN02–OWN11, 176 frames); **OWN12 excluded** (no free fall: book held, camera pans).
   Worst case $0.397 ≤ $0.40 via BATCH_TIMEOUT_S=780 (+300 s startup); expected ≈ $0.13. Dry run: dry-run.txt.
   Controller command (canonical root, after merge):
   `$env:S20_MODAL_RESERVATION_USD='0.40'; uv run --python 3.12 --with modal==1.6.3 --env-file .env modal run Build/measurement/runtime/modal_track.py --batch evidence/S07/S07i/fall-windows.json --approval evidence/S07/S07g/OWNER-APPROVAL.md`
3. run_sam_track.ps1: root via [IO.Path]::GetDirectoryName + Push-Location -LiteralPath, `--env-file .env`; `-Batch` switch.

## Files
Build/measurement/runtime/modal_track.py; tests/measurement/test_modal_track.py; evidence/S07/S07g/run_sam_track.ps1;
evidence/S07/S07i/{README.md, measure_own01.py, result-own01.json, fall_windows.py, fall-windows.json, dry-run.txt}; Run-System/Runs/S07i-orch170/{PLAN.md, TIMEBOX.json, REPORT.md}.

## Checks (fresh)
- python -m unittest discover -s tests/measurement -t tests/measurement → 86 tests OK (1 skipped, pre-existing); 4 new BatchTest.
- measure_own01.py --self-check OK; fall_windows.py --self-check OK; batch dry run (S07B_DRY=1, fake modal) 10 clips OK.
- run_sam_track.ps1 parses (0 errors); resolved root has .env (presence only, not read).

## Ponytail (full) — reuse / smallest change
- Reused free_fall.fit/evaluate_held_out + uncertainty.propagate_uncertainty unchanged; S07g yellow() threshold imported, not copied.
- Batch = thin track_batch wrapper over the unchanged single-clip body (renamed track_one) + main_batch reusing plan/_frames/admit_standalone; only body change: per-clip mkdtemp prefix (fixed /tmp/prefix would collide on clip 2).
- Skipped: model load-once refactor (reload per clip costs ~20 s each, inside bound), Modal CLI dry run (fake-modal harness used), runtime README update.

## Limits / risks
- Window/scale/detection allowances (2 px, 0.5 mm, 0.1 % clock) are declared, not measured; fitter flags plane_verified/verified set by declaration (evidence strings say so) — not Gate M.
- Fall-window rule was revised twice before tracking (jitter triggers; cfr decode off-by-one) — no tracking or g existed for those clips.
- Batch untested live: 16 GiB peak VRAM for 21 frames (OWN07 22 frames); 22.9 MB payload; Modal prices are list prices as of today.
- Communication: silent; one completion message to controller.
