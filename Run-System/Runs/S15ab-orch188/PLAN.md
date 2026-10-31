# S15ab-orch188 PLAN

Objective: private workspace shell per Q21 owner spec (evidence/ui/Q21-OWNER-SPEC.md): collapsible left icon rail (Ctrl+B, persisted),
center project, rightmost header button toggling a right Agent & tools panel (Ctrl+J, real tools only, Alt+1..4), 375px drawers.
Owns: Build/web/src/shell/workspace-shell.mjs (new), Build/web/src/shell/PrivateWorkspace.mjs, Build/web/src/workspace/view.mjs (section ids only),
Build/web/src/workspace/workspace.css, tests/shell-workspace/shell-toggle.test.mjs, Run-System/Runs/S15ab-orch188/.
Not touched: controller.mjs, workflow.mjs, interview reducer, API calls. Model: anthropic/claude-opus-5-5/high.
Checks: node --test workspace/shell-workspace/web-private/web-workspace-api; npm run build; Railway DEV web redeploy.
