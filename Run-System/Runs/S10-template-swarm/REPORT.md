# S10-template-swarm REPORT

- **Status:** DONE — simulation-only S10 trajectory child complete; this is not a parent product or physics-gate pass.
- **Issued/deadline:** 2026-10-28T17:30:16Z / 2026-10-28T18:00:16Z. Verified DONE and stopped 2026-10-28T17:42:06Z before deadline.
- **Branch/base:** `run/S10-template-swarm`, base `8efd3651bd957b3b36099981b63c11c9409e7950`.
- **Owns changed:** `Build/simulator/trajectories.mjs`, `tests/simulator/trajectories.test.mjs`, `evidence/S10/trajectories-swarm/`, this run directory.

## Result

Added `freeFallTrajectory` and `projectileTrajectory` as one small pure ESM kernel. Both require explicit finite dense position/velocity, gravity, positive fixed `dt`, safe integer step count, and exact `source: simulated` plus `inputProvenance: synthetic`. They call the accepted main `rk4Step` boundary, emit integer-step time-series samples, deep-freeze returned data, and classify initial versus sampled stop-plane crossings without fabricated exact event times. Added a trusted branded S08 export consumer that deep-freezes the validated clone, requires the real synthetic scene contract, maps explicit template fields, and floors only a sub-ulp duration horizon without altering `dt`. Ramp/pendulum were skipped as not needed for the requested minimum.

## Fresh checks

After rebasing onto accepted core `FF525274e` (full hash in parent/main history), ran `node --test tests/simulator/trajectories.test.mjs`: **6 passed, 0 failed**. `git diff --check`: PASS. The tests use the actual main RK4 import, execute the real Python `export_validated_setup.py` against the synthetic fixture, then consume that artifact in JS. They cover S08 analytic comparison, projectile motion, sparse vectors, overflow horizon, initial/sample stop planes, labels, deterministic finite output, deep immutability, and forged branded-clone rejection.

## Ponytail application

Used the existing RK4 helper rather than duplicating an integrator; added no dependency, adapter, abstraction layer, hidden defaults, or unrelated template features. Kept event handling sample-based because exact crossing interpolation was not requested and would overstate precision.

## Limitation / parent action

No core or export adapter was duplicated or edited. The trajectory child is integrated against the accepted main core and real export boundary, but it remains simulation-only: no contacts, bounce, real-scene measurement, physical approval, Gate P, Gate M, S12, or production claim follows.

OpenCodex-managed; not polled. No credentials, paid job, download, deployment, publication, or schedule used.
