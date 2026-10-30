# S24a-orch146 REPORT — DONE (draft scope per controller decision)

- Lane/model: CLAUDE, anthropic/claude-opus-5-5/high. Coding quota: OpenCodex-managed; not polled. Tokens/cost: unobservable.
- UTC: issued 2026-10-30T11:45:14+00:00; work stopped/reported 2026-10-30T11:51:54+00:00 (verified DONE; early finish allowed). Base main 8aa3e7f33e02e0ec4196cc0f88bbcad2ef9c5239; worktree .worktrees/S24a-orch146, branch run/S24a-orch146.
- Files: media/script/DEMO_SCRIPT_DRAFT.md (rewritten, v2); Run-System/Runs/S24a-orch146/{PLAN.md,TIMEBOX.json,REPORT.md,check_script.py}.

## Deliverable
9 beats / 3:00, measurement-first (tracking -> reconstruction -> fit -> sealed prediction -> interview -> lab/library -> cost + misses -> close). Per beat: time, shot, burned-in caption, VO, evidence pointer (BENCHMARK row id or JSON), status. Plus: verbatim on-screen label table, Meta-models table with claim limits, shot list with creator/licence/credit line, copy-paste captions block, PENDING register, cut list. Prior PARTIAL gaps (S21 numbers, Gate A wording) closed: Gate A now MET_AMENDED_Q16 verbatim from GATE_A.json; S21 values replace PENDING S21.

## Evidence quoted (generated values only)
- BENCHMARK rows: st03_g_image_relative_uncertainty 0.07367 (n 19); rm02_gravity_direction_bootstrap_sd 0.04393; rm02_gravity_vs_camera_down_prior 11.05; st03_heldout_normalized_rms 0.1982 (diagnostic, 7/466); modal_month_to_date_billed_usd 0.599594; meta_s16e_total_tokens 1176; meta_s16e_latency_s 2.52345; meta_s16e_cost_usd UNAVAILABLE; gate_rs_median UNAVAILABLE.
- GATE_A.json: verdict MET_AMENDED_Q16, label "scale unverified, not setup-validated", 10/10 numeric contract, 0/10 setup validator, 30/30 replay turns, 0 oracle-flagged inventions.
- S16e-orch108-live.json: model meta-models/muse-spark-open-1026, request_count 1, cost_usd null. PD02-summary.json: 439/439 frames, A10G. S14g-fix3-live.json summary: 30 Spark / 10 Wonder calls.
- library-copy.mjs: SIMULATED tags and MYSTERY_COPY quoted verbatim.

## Checks (fresh)
- `python -B Run-System/Runs/S24a-orch146/check_script.py` (repo root): links resolve, every decimal in the script is found in BENCHMARK/evidence JSON (model version names excluded), Gate A/S16e/PD02/S14g asserts, timing 12+28+20+25+25+25+20+15+10 = 180 s and caption start times match beats. Result: PASS links=16 decimals_checked timing=180 captions=9.
- `python Run-System/worker_timebox.py check` on TIMEBOX.json: TIMING PASS.
- Not run: Build/benchmark/crosscheck.py on the script (it checks BENCHMARK/About only, no script input).

## Ponytail (applied)
- Reuse: rewrote the existing DEMO_SCRIPT_DRAFT.md in place (same path) instead of a new script tree; captions/shot list live in the same file; numbers cited by BENCHMARK row id rather than re-derived; label text copied from library-copy.mjs and GATE_A.json.
- Smallest complete: one ~45-line stdlib check script (links + numbers + timing) so the PENDING register's re-quote check is runnable; no SRT export, storyboard, generator or test framework.
- Skipped: SRT/VTT files, video capture/edit (S24c-f), deployed URL (S23), crosscheck.py extension, per-clip people/depicted-rights review.

## Risks / owner items (not written to canonical controls — controller to route)
- **Rights:** evidence/owner/S02/APPROVAL.md approves PD02/RM02/ST03 for local pipeline only and holds *public raw media redistribution*; a public demo video showing clip frames needs a separate owner go-ahead. Script marks it PENDING owner with a plots-only fallback.
- Beats 6-9 screens and URL depend on S23 (needs written judging-deploy go-ahead) and S24c-f captures.
- S14g-fix3 Spark/Wonder calls are from a recorded run on synthetic-room tools; their dollar cost is not in BENCHMARK, so the script states no cost for them.
- If any BENCHMARK/evidence value changes, rerun check_script.py before recording.

## Communication
Silent; one authorized completion message to controller chat. No canonical controls edited; no secrets read; no installs, GPU or API calls.
Next: S24c-f captures; owner decision on public clip frames; S23 URL; then replace PENDING items and rerun check.

