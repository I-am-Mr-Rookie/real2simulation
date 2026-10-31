# S07n-orch186 REPORT — DONE
Lane CLAUDE, step S07; model anthropic/claude-opus-5-5 medium. UTC start 2026-10-31T05:23:53+00:00, end 2026-10-31T05:28:01+00:00. Coding quota: OpenCodex-managed; not polled. Tokens/cost: unknown (not observable); $0 cloud (no GPU/Modal/Meta).

## Delivered (worktree .worktrees/S07n-orch186, branch run/S07n-orch186)
- evidence/S07/S07n/fall_time_height.py — deterministic script; evidence/S07/S07n/results.json, table.md (script output); README.md (rules, table, verdict).

## Result (script output, MEASURED conditional)
- OWN01 hero: ABSTAIN — S07g track ends f54 still falling; lower bounds only t ≥ 0.267 s, h ≥ 0.374 m. Real t/h for OWN01 needs track extension past f54 (new SAM/GPU run, out of scope).
- Release+impact inside track: OWN02 t 0.467±0.027 s, h 0.911±0.008 m, g_ht 8.36±0.98; OWN03 0.400±0.027, 0.781±0.012, 9.77±1.34; OWN07 0.433±0.027, 0.923±0.010, 9.84±1.24; OWN09 0.433±0.027, 0.851±0.010, 9.07±1.14. g_ht vs stored v1 fit |z| ≤ 1.10.
- Abstain: OWN04/05 impact outside track (lower bounds), OWN06 release outside track, OWN08 pre-release not static, OWN10/11 no fall.
- Verdict: approximate for demo (t ±6–7 % from ±1-frame endpoints; h stat u 1–2 % excludes scale/plane/perspective/rolling-shutter/blur systematics).

## Checks (fresh)
- python -B evidence/S07/S07n/fall_time_height.py → self-check OK (synthetic g 9.734 ± 1.065 vs 9.8), in-run asserts passed for 4 measured rows (t = n/30, PTS span within 1 %, h = ½ g_ht t², u > 0).
- python -B evidence/S07/S07n/fall_time_height.py --self-check → OK.
- python Run-System/worker_timebox.py check Run-System/Runs/S07n-orch186/TIMEBOX.json → see commit.

## Ponytail
- Reuse: S07k measure_v2 (TRACKS, locate, MOVE/STATIC/SCALE/WIDTH_TOL/DECEL thresholds), S07i measure_own01 constants (EDGE_M/U, BOX_EDGE_U_PX, DETECTION_STD_PX, CLOCK_U, G_LOCAL) and its m/px uncertainty formula; S07l centroid-vs-box drift idea as the pixel systematic. Stored fits read from S07h/S07k results.json, not refit.
- Smallest complete: one ~180-line script, stdlib only; no new tracking, no video, no fitting, no shared-code edits.
- Skipped: v3 (S07m) comparison column (v1/v2 suffice); rolling-shutter/blur correction (reported as unquantified systematic); OWN01 track extension (needs GPU).
- Risk: one post-first-run rule fix (scale-frame width outlier, triggered by OWN01 hand-in-box at f46) — recorded in README; it changed OWN09 h. Endpoint rules are heuristic; ±1 frame may understate ambiguity for blurred impacts.

## Communication
Silent; one completion message to controller only. No canonical controls edited.
Next: S24m (demo copy) may cite OWN03/OWN07 as approximate system-derived t/h; OWN01 needs a track extension run if the hero clip must show t/h.

