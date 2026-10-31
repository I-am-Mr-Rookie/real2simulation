# S15aw-orch216 PLAN

Objective: signed-in workspace result view shows one chart for an owner-clip result: RECORDED track points, SIMULATED prefix fit with 1-sigma band, dashed held-out prediction, and the API's held-out PASS/FAIL. Numbers only from the API.

Owns: Build/web/src/workspace/ (result-chart.mjs new, view.mjs, workspace.css); Build/api/workspace/ (owner_clips.json additive "series", jobs.py additive passthrough); tests/workspace/result-chart.test.mjs; evidence/S15aw/; Run-System/Runs/S15aw-orch216/.

Approach (smallest complete): the API had no per-frame points, so evidence/S15aw/build_series.py freezes them from the existing S07l/S07m pipeline (load, floor(2n/3) prefix quadratic, v3 sigma) into owner_clips.json; owner_measurement passes "series" through; browser maps API numbers to SVG geometry only.

Checks: node --test tests/workspace + tests/web-workspace-api; tests/api-workspace unittest; build_series.py --check (held RMSE reproduces stored value); npm run build; FIXTURE screens.

Timebox: issued 2026-10-31T14:07:51+00:00, cutoff 14:32:51, deadline 14:37:51 (Dhaka 20:37:51).
