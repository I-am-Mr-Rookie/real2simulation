# S15ac-orch189 PLAN

- Objective: QUEUE S15ac - interview rendered as a right-panel agent question card (Q21 owner spec); centre keeps scene/stage with a non-blocking "Agent needs your answer" state; web redeployed to Railway DEV.
- Lane/model: CLAUDE, anthropic/claude-opus-5-5 high (OpenCodex-managed; not polled). Issued 2026-10-31T06:19:27Z, deadline 06:49:27Z, cutoff 06:44:27Z.
- Owns: Build/web/src/ (not workspace/controller.mjs or workflow.mjs); tests/workspace/; tests/shell-workspace/; evidence/S15ac/; Run-System/Runs/S15ac-orch189/.
- Approach (smallest complete): new pure module Build/web/src/shell/agent-card.mjs over the unchanged interviewView/reduceInterview; PrivateWorkspace stops passing interview to <Workspace> (centre panel drops out with no view.mjs change) and passes the card into renderShell's right panel; badge + pending count in workspace-shell.mjs; CSS in workspace.css.
- Checks: node --test 4 suites; npm run build; static 375/1280 render; Railway DEV web redeploy.
