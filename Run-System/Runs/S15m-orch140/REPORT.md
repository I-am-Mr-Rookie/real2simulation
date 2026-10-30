# S15m-orch140 REPORT
Lane CLAUDE; anthropic/claude-opus-5-5/high; coding quota OpenCodex-managed, not polled. Branch run/S15m-orch140 from main 7dde2c9.
UTC: issued 2026-10-30T11:32:27Z, worktree 11:33:36Z, work stopped 2026-10-30T11:39:49Z, deadline 12:02:27Z. **Status: DONE** (all 3 acceptance checks met; early finish allowed for verified DONE).

## Deliverables
- evidence/S15/S15m/PLAN.md — stage map (12 stages -> existing module, host, live/recorded, spend gate), proposed web-proxy + API contracts, recorded-vs-live truth table, spend gates, risks, cut order, wave sequence.
- evidence/S15/S15m/rows.md — 8 QUEUE-format rows (7 core + 1 optional cut-first): S14i, S15n, S04n (wave 1, parallel), S13i, S04m, S04o, S15o, S13j(optional). IDs verified free in QUEUE.md.

## Key findings
1. Bottleneck: web image Node-only; all stage brains except the simulator are Python. Smallest fix: host them in the EXISTING FastAPI API service behind one Clerk-auth web proxy route; no new service/dependency except pinning jsonschema in the API image.
2. Default demo path makes zero paid calls: upload of an approved clips.csv sha is live; keyframes/understand/segment/reconstruct replay the real S13h-orch46 RM04 run labelled RECORDED; interview/validate/browser-run/fit/HTML report are live and $0.
3. RM04 geometry (PLY) bytes are not in git (only scene.json/scene-log/reconstruction.json tracked) -> viewport must show honest unavailability unless optional S13j re-captures bytes under guardrails.
4. Existing pieces reused, not reinvented: UploadService, JobRunner (redis-py-compatible store API), progress.py -> reducer JOB_UPDATE, interview.answers_to_spec/validate_setup, fitter.handle, reports typeset + html-print-fallback, guardrails admission ($30 cap/$5 floor) + gpu_stages.reserve.

## Checks (fresh)
- Local import probe (python -B, no bytecode): interview/fitter/reports/pipeline/guardrails import OK; repo deps Build/{agent,fitter,guardrails,pipeline,reports}+contracts/{agent,experiment,fit}; new third-party only jsonschema (not in API requirements.txt).
- rows.md parse: 8 rows, 12 columns each, 0 duplicate Owns entries.
- Verified in QUEUE.md: S11d, S13h, S14c-h, S17a-f, S20a-d DONE; contracts/jobs/policy.json chunk_bytes 8388608; tests/agent/fixtures/muse exists.
- python Run-System/worker_timebox.py check TIMEBOX.json (result below in commit; see TIMEBOX.json).

## Ponytail
Reuse over new code: every stage mapped to an existing module; one proxy route + routers in the already-deployed API instead of a new service, Python-in-web, or a queue worker; Redis already deployed; replay of an existing real run instead of new GPU spend. Smallest-complete choices: chunk cap from policy.json, error codes from existing reducer. Skipped: live GPU/Muse wiring (optional S13j / blocked by Meta hold), Postgres scene persistence (Redis keys shortcut), PDF compile in image (HTML print fallback), /lab Railway fix (out of scope). Not checked: runBrowserSimulation accepts validate_setup output unchanged; interview scene_root data size; Next route streaming limits on Railway.
Risks: ephemeral API upload FS; internal-token trust model (dev only); Claude quota stalls on 30-min rows.

No code edits, deploys, paid calls or secret reads. Canonical controls untouched. Communication: silent; one completion line to controller.
