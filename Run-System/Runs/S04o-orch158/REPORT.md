# S04o-orch158 REPORT — DONE (QUEUE acceptance met; browser walk deferred to S15o by controller)

Lane CLAUDE; model anthropic/claude-opus-5-5 medium (assigned); coding quota OpenCodex-managed; not polled. Tokens/cost: unknown (not observable). Railway DEV deploy only; no Meta/GPU call, no secrets read.
UTC: issued 2026-10-30T20:07:23Z; work ~20:08Z–20:21Z; deadline 20:37:23Z. Branch run/S04o-orch158 (worktree .worktrees/S04o-orch158), base main 131168ed; commits cbce5c0, a09fe75, + report commit.

## Changed
- Build/web/src/shell/PrivateWorkspace.mjs — mounts S15n `createController` (BFF /api/workspace/*). `probeApi` (GET jobs/s04o-probe; API JSON answer incl. 404 = live; 401/403/5xx/non-JSON/network = unavailable). Live: LIVE notice, fixture notice hidden, `renderUpload` (its error slot nulled — job panel already renders state.error once, per S15n limit), Workspace gets onAction/interview/run/instruments/fit/report. Unavailable/checking: honest notice + original FIXTURE notice, no onAction (controls disabled), no numbers. `routeAction`: Q_* -> reduceInterview (+ ctl.submitAnswers when complete), I_* -> reduceInstruments (I_MEASURE fails honestly: no instrument service deployed), RUN_START/FIT_START/REPORT_OPEN -> ctl.run/fit/openReport, other events -> ctl.dispatch. Questions loaded once on interview.active (ctl.loadQuestions -> Q_LOADED).
- Build/web/src/workspace/controller.mjs (Owns extended by controller for this fix) — matched S13i API routes (Build/api/workspace/jobs.py, unedited): PUT uploads/{id}/chunks/{offset}; no POST /jobs, job comes from complete `{upload, job, provenance}` (provenance kept in snapshot); progress GET jobs/{id}?after=R with first read always run (inline replay may already be ready). Fail-closed error mapping unchanged.
- tests/workspace/controller.test.mjs — routes/assertions updated to S13i paths; added malformed-complete (no job_id) -> PROCESSING_FAILED and chunk 402 -> SPEND_PAUSED cases.
- tests/shell-workspace/private-workspace.test.mjs — 4 tests (probe classification + BFF path/credentials; routing never fabricates data).
- evidence/S04o/DEPLOY.md. dev-scenes.mjs and page.jsx unchanged (not needed).

## Ponytail (full) applied
Reuse: controller.mjs, upload-view, interview/instrument/runcontrol reducers, react.mjs createWorkspace props, existing stage.py + railway up. Root-cause fix in shared controller instead of a hidden path-translation adapter. No new state machine, no React rewrite. Shortcut noted in code: no instrument service -> I_FAIL. Skipped: browser simulator wiring for run (controller.run reports DEPENDENCY_UNAVAILABLE without `simulate`); report HTML render (reportView expects r2s.report/1, controller stores {status,html} -> honest "rejected").

## Checks (fresh, after final code)
- `node --test "tests/workspace/*.test.mjs" "tests/shell-workspace/*.test.mjs" "tests/web-private/*.test.mjs" "tests/web-workspace-api/*.test.mjs"` -> 104/104 pass.
- `npm run build` (Build/web) -> Compiled successfully; all routes.
- DEV deploy: stage.py web (111 files, rev a09fe75) + railway up -> **197153d3-5f88-4287-8e21-d7cf77cb4d27 SUCCESS** (replaced 3f707632, earlier SUCCESS of cbce5c0). deployments.json line for controller in evidence/S04o/DEPLOY.md.
- Logged-out live HTTP after final deploy: BFF 401 UNAUTHORIZED, /workspace 404, other-owner scene 404, / 200 => (2) unchanged.

## Deferred to S15o (controller-accepted blocker)
ChatGPT in-app browser unavailable in this worker chat ("Browser is not available: iab"; listBrowsers=[]); Chrome not used. Not verified: signed-in BFF->API round trip, live/unavailable notice in a real session, approved RM04 upload, screenshots, 375px no horizontal scroll. Route fix is unit-tested only, not live.

## Risks
- If WORKSPACE_INTERNAL_TOKEN mismatches, API 401 -> page shows honest "unavailable" (by design).
- Job snapshot from complete assumed same shape as progress doc.job (both S13g job_snapshot per code read); unverified live.
- reportView/controller report shape mismatch remains (report view will show rejected, not fabricated) — S15o should confirm.

Communication: silent; one nonterminal blocker message + one completion message to controller (owner-authorized channel).

