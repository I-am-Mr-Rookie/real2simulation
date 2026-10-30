# S15s-orch164 PLAN
Objective: reach Fit and Report from a finished run in the live workspace (run.done -> Fit -> fit.done -> Open report -> sandboxed report), normal + what-if.
Owns: Build/web/src/workspace/; Build/web/src/shell/PrivateWorkspace.mjs; tests/workspace/; tests/shell-workspace/; evidence/S15s/; Run-System/Runs/S15s-orch164/.
Approach: runView gets a phase->next-step map using existing graph edges (FIT_START, REPORT_OPEN); view.mjs renders one button through existing onAction. PrivateWorkspace already routes both events.
Checks: node --test 4 suites; npm run build; stage.py web + railway up (DEV).

