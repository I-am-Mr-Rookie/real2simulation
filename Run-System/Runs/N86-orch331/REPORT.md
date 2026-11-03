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
DEV browser QA (Koushik asked; controller reissued 30 min): in-app browser, fixture account, own "N86 QA lab" (2 blocks, ball, ramp floating). Clean up the lab: one click sent, "Updated objects", objects on the floor, status and toggle "Tidied by agent · SIMULATED", no em dashes, console errors none. Undo 1 = Before (4 objects), Undo 2 = previous add (3), Redo back; Before/After switch both ways; another edit hides the toggle. 1366x900 and 375x812, no horizontal overflow.
QA fixes (commit 2, CSS only + editor-ui test): unpressed Before/After button had dark ink on dark surface (invisible); at 375px the toggle sat on the SIMULATED badge row and hid "Tidied by". Not yet redeployed: verified by measurement on DEV before the fix, fix verified by tests/build only.
Paid calls: 1 agent turn 2026-11-03T15:27:19Z to 15:27:48Z UTC, default muse-spark-1.3 Standard; reply tagged "fallback model", so the Spark attempt stopped and the Sol fallback (Merge) answered. Units/cost are in the DEV server ledger, not read here.
Local QA setup (before controller redirect): DEV web Clerk vars were exported to the worktree's gitignored Build/web/.env.local; deleted, token file deleted, servers on 3086/8086 stopped, all verified. No secret printed or committed.
Skipped: live check that Spark alone emits lab_update_objects (this turn needed the fallback); tilt straightening (yaw only); block size_m is a cube resize, so wall/table dims are not tool-resizable.
Risks: "Answered by muse-spark-1.3" label shows the requested model, not the fallback that answered (existing N85 behaviour); listing capped ~3600 chars (about 50 objects).
