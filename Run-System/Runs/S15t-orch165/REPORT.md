# S15t-orch165 REPORT — DONE
Lane CLAUDE, anthropic/claude-opus-5-5/high (OpenCodex-managed; not polled). UTC start 2026-10-30T22:12:49Z, end 2026-10-30T22:25:59+00:00. Branch run/S15t-orch165 (worktree .worktrees/S15t-orch165), rebased onto main d3cd9681. Tokens/cost: unknown (unobservable); no Meta/GPU call.

## Root causes (reproduced with REAL RM04 what-if observations, real FastAPI routes)
1. **Fit display rejected**: Build/web/src/shell/PrivateWorkspace.mjs passed `fit: s.state.fit` (the reducer's revealed {gravity,...}) to Workspace, but fit-view `parseFit` takes `{ times, output }` (request times + raw fitter output) -> `output` undefined -> 'fit output not ok'. API /fit was fine (200, status ok).
2. **/report 422**: controller `fitRequest` sent only times/positions, so `fitter.api.handle` omitted `model_selection`; Build/reports `render_html` reads `fitter["model_selection"]` -> KeyError -> 422 "report did not validate: 'model_selection'". Repro: evidence/S15t/rm04_fit_request.mjs + rm04_api.py (pre-fix output: `fit 200`, `report 422 ... errors: ["'model_selection'"]`). The hand-made fake apiFit() in controller.test.mjs hid both.
3. **Report error invisible**: a report 422 leaves phase fit.done; the stage panel only showed errors in *.failed phases (the job aside had it, off the main panel).

## Changes (fixed once in shared code)
- Build/web/src/workspace/controller.mjs: `fitRequest` adds `degree: 2, select_model: true` (same as the S15 fit fixture contract; fitter accepts both); snapshot `fitInput = { times: req.times, output: r.data }`.
- Build/web/src/shell/PrivateWorkspace.mjs: `fit: s.fitInput`.
- Build/web/src/workspace/view.mjs: stage-panel error ("CODE: reason") also in fit.done (report failure), reusing the S15r stageError line.
- tests/workspace/controller.test.mjs: fit request keys now include degree/select_model; asserts fitInput.
- NEW tests/web-workspace-api/fit-report-contract.test.mjs + tests/api-workspace/route_cli.py: real S15r RM04 spec response -> real browser simulator (what-if) -> real controller, whose /fit and /report go to the REAL analysis routes via FastAPI TestClient; real /fit output -> real fitView (no error, gravity row, residual count) -> real /report 200, request label === verbatim what-if label, report html contains it. Upload/job/questions are SYNTHETIC transport stubs only.
- evidence/S15t/: repro scripts, rm04-fit-request.json, rm04-fit-response.json (status ok; gravity -9.81 m/s^2 SIMULATED, from a what-if run, not measured).
- Not changed: analysis.py, Next proxy, Build/fitter, Build/reports (no API redeploy needed).

## Checks (fresh)
- node --test tests/workspace tests/shell-workspace tests/web-private tests/web-workspace-api (after rebase): 113/113 pass. Pre-rebase incl. tests/simulator: 230 tests, 5 fail = contacts.test.mjs (worktree lacks Build/simulator/node_modules; 9/9 pass with a temporary junction, removed) + 4 R14/clean simulator tests that fail identically on canonical main (pre-existing, untouched).
- python -B -m unittest discover -s tests/api-workspace -t tests/api-workspace: 21 OK.
- npm run build (Build/web, node_modules junction to canonical, removed afterwards): exit 0.

## Deploy (Railway DEV, web only)
- `python infra/railway/dev/stage.py web %TEMP%\s15t-web-orch165` -> 111 files, source_revision 1f6c012dcefde8b27ee4abe5bf9d92bb8c62701d; `railway up --detach` (project b07b0d66, env c5823a28, service 49f2938d) from that dir.
- web deployment b1805418-6caa-44db-8f15-133918341eff SUCCESS (previous d4663452 REMOVED); https://web-dev-cd80.up.railway.app/ -> 200.
- For the controller (not edited by me): deployments.json web {deploymentId b1805418-6caa-44db-8f15-133918341eff, previousDeploymentId d4663452-8223-4d7d-8919-2b72219d7e0a, sourceRevision 1f6c012dcefde8b27ee4abe5bf9d92bb8c62701d}. API not redeployed (unchanged; api 81a74b99 / verify.py pin unchanged).

## Ponytail
Reuse: existing fitter options (degree/select_model) instead of changing analysis.py or Build/reports; existing parseFit {times, output} contract; existing stageError line; S15r rm04 spec evidence + test_spec_q16 resolver/AUTH for the TestClient. Smallest change: 3 source lines + 1 snapshot field. Skipped: browser walk (controller's job); making /report tolerate fits without model_selection (Build/reports not owned; request fix is the root cause); per-file Python fixture regeneration check (contract test calls the live route each run instead).
Risks: contract test needs `python` with fastapi on PATH (spawned); Live DEV UI not walked by me. Communication: silent; one completion line to controller.
