# S10e-extension PLAN

- Objective: Add the smallest pure ESM simulated ramp and nonlinear pendulum trajectory API on the accepted fixed-step RK4 core, with a trusted S08 export-envelope consumer, tests, and evidence.
- Owns: `Build/simulator/extended-templates.mjs`; `tests/simulator/extended-templates.test.mjs`; `evidence/S10/extension-templates/`; `Run-System/Runs/S10e-extension/`.
- Base: `main` at `03d57f6982e21c5d914a53a7a2007c73689b5a5a`; branch `run/S10e-extension`.
- Checks: direct ramp and pendulum dynamics/oracles; real Python `export_validated_setup.py` artifact consumption; zero horizon, invalid/sparse/overflow inputs, determinism, immutability, nonlinear convergence and energy sanity; diff and timebox checks.
- Ponytail: reuse `rk4Step` and the existing S08 artifact envelope; no dependency, duplicated integrator, schema copy, contact solver, or edits outside Owns.
- Skips: physical calibration, real-scene/Gate P evidence, contacts, lab integration, deployment, spend, and changes to peer-owned trajectory/control files.
