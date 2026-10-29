# S15f-orch23 plan
Objective: workspace run, pause and seeded-replay controls following the S10 replay contract. Lane CLAUDE, anthropic/claude-sonnet-5-5/high (OpenCodex-managed, not polled). Branch run/S15f-orch23, worktree .worktrees/S15f-orch23.
Owns: Build/web/src/workspace/; tests/workspace/; evidence/S15/; Run-System/Runs/S15f-orch23/.
Design (smallest complete): reuse S15a RUN_* edges and S10 `replay.mjs` (injected, not imported); new pure `runcontrol.mjs` + `run-view.mjs`; one optional `run` prop in react.mjs/view.mjs; CSS; fixture runner in fixtures.mjs.
Acceptance: run, pause and seeded replay follow the simulator contract; same-seed replay reproduces identical traces in tests (real replay.mjs, fixture runner); 375px check in the in-app browser.
