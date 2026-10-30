# S15t-orch165 PLAN
Objective: root-cause and fix live 'Fit display rejected: fit output not ok' (after /fit 200) and /report 422 on the RM04 what-if path; visible fit/report errors; real-API contract test; redeploy DEV.
Owns: Build/web/src/workspace/; Build/web/src/shell/PrivateWorkspace.mjs; Build/web/src/app/api/workspace/; Build/api/workspace/analysis.py; tests/workspace/; tests/shell-workspace/; tests/web-workspace-api/; tests/api-workspace/; evidence/S15t/; Run-System/Runs/S15t-orch165/.
Lane CLAUDE, anthropic/claude-opus-5-5/high; issued 2026-10-30T22:11:54+00:00, deadline 22:41:54Z, cutoff 22:36:54Z.
Checks: node --test 5 suites; python unittest tests/api-workspace; npm run build; stage.py web + railway up.
