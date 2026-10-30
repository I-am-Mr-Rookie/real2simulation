# S15s-orch164 REPORT — DONE
Lane CLAUDE, anthropic/claude-opus-5-5/medium. UTC start 2026-10-30T21:45:59Z, end 2026-10-30T21:51:44+00:00. Coding quota: OpenCodex-managed; not polled. Tokens/cost: unknown (not observable). No Meta/GPU call, no secrets, no Chrome.

## Change (commit 01db492f on run/S15s-orch164, rebased onto main 0efe2ff9)
- Build/web/src/workspace/runcontrol.mjs: `runView(...).next` = `{event:'FIT_START',label:'Fit'}` in run.done, `{event:'REPORT_OPEN',label:'Open report'}` in fit.done, else null.
- Build/web/src/workspace/view.mjs: stage panel renders one `data-slot="next-step"` button (after fit panel, before report) sending `{type: run.next.event}` via existing onAction. Only when the host passes `run` (live PrivateWorkspace), so fixture/public views are unchanged.
- PrivateWorkspace.mjs: unchanged (already maps FIT_START -> ctl.fit(), REPORT_OPEN -> ctl.openReport()). Instruments not enabled; ctl.fit uses stored run observations.
- What-if label: existing view.mjs `ws-whatif` note (run/fit/report phases) + PrivateWorkspace note; test asserts it on run.done, fit.done and report.open.

## Tests
- tests/workspace/controller.test.mjs: what-if test now reaches fit/report by clicking the rendered Fit / Open report buttons through the real host router (routeAction), real browser simulator (browserSimulate(runBrowserSimulation)), fake BFF fetch; asserts fit.done, report.open, report request carries WHAT_IF_LABEL, sandboxed iframe rendered, no next-step in report.open, and runView.next null in upload.idle/interview.active/run.ready/run.running/run.paused/run.failed/fit.running/fit.failed/report.open. New normal-path test: run.done -> FIT_START -> fit.done -> REPORT_OPEN -> report.open via runView.next + routeAction.
- tests/shell-workspace/private-workspace.test.mjs: REPORT_OPEN outside fit.done makes no request.
- `node --test "tests/workspace/*.test.mjs" "tests/shell-workspace/*.test.mjs" "tests/web-private/*.test.mjs" "tests/web-workspace-api/*.test.mjs"`: 112 pass, 0 fail (before rebase); after rebase workspace+shell 97 pass 0 fail. Build/web/node_modules junction to canonical, removed afterwards.
- `npm run build` (Build/web): exit 0.

## Deploy (Railway DEV, web only)
- `python infra/railway/dev/stage.py web %TEMP%\s15s-web-orch164` -> 111 files, source_revision 01db492f0ab3bed8b51fd103e8935b5d5f0daab4; `railway up --detach --project b07b0d66-... --environment c5823a28-... --service 49f2938d-...` from that dir.
- web deployment d4663452-8223-4d7d-8919-2b72219d7e0a SUCCESS (previous 0144fdf3 REMOVING). https://web-dev-cd80.up.railway.app/ -> 200; signed-out /workspace -> 404 (by design, auth CONTRACT uniform 404).
- For controller (deployments.json not edited): web {deploymentId d4663452-8223-4d7d-8919-2b72219d7e0a, previousDeploymentId 0144fdf3-5747-4979-ba23-0fd8a2f91a6d, sourceRevision 01db492f0ab3bed8b51fd103e8935b5d5f0daab4, providerStatus SUCCESS}.

## Ponytail
Reuse: existing graph edges, routeAction mapping, onAction/button pattern (same as retry), existing what-if note, fakeFetch/toRunReady harness, stage.py/railway up procedure. Smallest change: 1 map + 1 field + 1 render line; no new state machine, no PrivateWorkspace edit.
Skipped: browser walk (controller's job); live /fit and /report API not exercised by me (no signed-in session in this run) — unverified on DEV; sidebar/navigate not enabled; evidence/S15s/ not needed.
Risks: next-step button sits below the fit table (may need scrolling on 375px); live /report behaviour on DEV unverified until controller walk.
Communication: silent; one completion message to controller.

