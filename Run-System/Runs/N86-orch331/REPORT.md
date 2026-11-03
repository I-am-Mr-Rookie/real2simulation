# N86-orch331 REPORT: Clean up the lab
Status: DONE (build only; no browser QA by instruction, Koushik reviews on DEV).
Changed:
- Build/api/agent/lab_handlers.py: new lab_update_objects (atomic batch). Shared _apply helper is the exact lab_update_object item path (same _find, update_object params/SI/relative moves); batch applies all in memory, one validateScene+save, else "nothing was changed; updates[i]: ...". Registered in HANDLERS.
- Build/agent/core.py: lab_update_objects schema (items reuse the lab_update_object property schema, required params, max 50), REQUIRED map, one cleanup sentence in INSTRUCTIONS (existing rules untouched).
- AgentPanel.jsx: "Clean up the lab" card + chip, sends at once (fixed CLEANUP text + rounded object list: the agent has no scene-read tool), "Best with Muse Wonder" hint, log/history show the title, draft kept; step name "Updated objects"; status "Tidied by agent · SIMULATED".
- history.mjs tidyView + LabEditor.jsx: whole agent turn is one setScene, so one Undo step; Before/After toggle = undo/redo of that step, labelled "Tidied by agent · SIMULATED", hidden after any other edit. CSS for hint/toggle.
Checks:
- python -m pytest tests/agent: 213 passed, 464 subtests (new: valid batch equals single updates; one invalid item rejects all for python-param, validateScene and unknown-id errors; schema/registration).
- node --test tests/lab-editor: 56/56 (new: cleanup card send, listing budget <= MAX_TEXT, single Undo + Before/After).
- Other node suites: api-storage, pwa, shell-workspace, viewer, web-guide, web-private, web-workspace-api, workspace, web-library all 0 fail. lab: 1 fail (contact-integration: worktree cannot resolve @dimforge/rapier3d-compat; passes on main). simulator: oracle fails also on main (4). library: hung >5 min, not run to completion (untouched area).
- npm --prefix Build/web run build: exit 0.
Paid calls: none.
Skipped: browser QA (by instruction), live model check that Muse models emit the nested lab_update_objects schema; tilt straightening (yaw only, existing tool limits); block size_m is a cube resize so wall/table dims are not resizable via tools.
Risks: listing capped ~3600 chars (about 50 objects fit, extra noted "N more not listed"); Before/After relies on scene object identity in history.
