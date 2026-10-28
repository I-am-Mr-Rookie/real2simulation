# S10g-service plan

- Objective: implement the bounded local synthetic lab bridge/service and loopback API with trusted S11 fit/reveal.
- Owns: `Build/lab/session-service.mjs`, `Build/lab/session-bridge.py`, `Build/web/src/app/api/lab/route.js`, `tests/lab/session-service.test.mjs`, `tests/lab/test_session_bridge.py`, `evidence/S10/service/`, `Run-System/Runs/S10g-service/`.
- Base: `bd5df5fcfa502433fd5df4d0ec24010efb604d2b`; branch `run/S10g-service`.
- Reuse: existing S08 `regression_case`/validated export, Node RK4 engine, Python S11 `handle`, and S10 Mystery-g trusted handoff. No new dependencies.
- Acceptance: actual four-template bridge start, ballistic actual fitter and redacted mystery pre-fit, loopback/prod guard, bounded clean errors and regression tests.
- Skip: browser integration, deployment, physical calibration, public upload and shared-control edits.
