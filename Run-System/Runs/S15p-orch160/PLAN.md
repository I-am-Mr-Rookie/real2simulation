# S15p-orch160 PLAN
Objective: wire workspace run via runBrowserSimulation, accept API /fit and /report shapes, honest instruments; tests, build, web DEV redeploy.
Owns: Build/web/src/shell/PrivateWorkspace.mjs; Build/web/src/workspace/controller.mjs; Build/web/src/workspace/navigation.mjs; tests/workspace/; tests/shell-workspace/; evidence/S15p/; Run-System/Runs/S15p-orch160/.
Checks: node --test workspace + shell-workspace + web-private + web-workspace-api; npm run build; railway up dev + logged-out HTTP.
