# S15bg-orch244 plan
Objective: no fixture wording announced on a live signed-in workspace (R-D F6).
Owns: Build/web/src/shell/; Build/web/src/auth/dev-scenes.mjs; tests/shell-workspace/; evidence/S15bg/; this run dir.
Change: pure `workspaceHeading(api, scene)` in PrivateWorkspace.mjs: live = "Private workspace", checking = "Workspace", unavailable (fixture) = scene.title. Fixture notice hidden while checking. dev-scenes.mjs untouched (fixture title is correct in genuine fixture mode). document.title is the static layout title "Real2Simulation", no fixture wording.
