# S10hi-gate

Objective: expand the actual four-template analytic/seeded replay acceptance over explicit parameter and horizon cases, preserve every measured or rejected case, and diagnose sampled Rapier contact jitter/fallback without weakening the 0.5% threshold or claiming UI/physical Gate P.

Owns:
- Build/lab/acceptance.py
- tests/lab/test_acceptance.py
- evidence/S10/acceptance/
- Run-System/Runs/S10hi-gate/

Issued: 2026-10-28T18:34:51Z; deadline: 2026-10-28T19:04:51Z; minute-25 cutoff: 2026-10-28T18:59:51Z.
Base: bd5df5f; branch: run/S10hi-gate.

Reuse: S08 template factories and analytic oracles, `Build/lab/regression.py` quantity/export conventions, the existing Node RK4 transport, and `replay-check.mjs`. No new integrator, oracle, dependency, UI, manifest, or control-file changes.

Acceptance: explicit gravity/parameter/horizon cases for all four templates; dimensional characteristic scales with a near-zero zero-answer guard; every case remains visible as pass/rejected/error; actual seeded replay is checked per valid case. Contact diagnostics use the existing same-state Rapier adapter at a dt sweep and report unavailable/rejected honestly; no rebound or physical claim.

Prerequisite boundary: this worker does not invent S10g UI integration or required reviews. Evidence records whether the checkout exposes a verifiable S10g UI path; simulation acceptance is not UI/physical Gate P.
