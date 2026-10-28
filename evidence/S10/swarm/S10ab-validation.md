# S10ab swarm validation

Synthetic-only evidence. This does not unlock real-scene integration or Gate R/M/P/RS/S12.

- **S10a:** `validatePlacementSnapshot` performs a closed, portable v1 snapshot check and brands only its returned frozen object in a private `WeakSet`; `placeApparatus` rejects raw/forged objects, validates box pose/dimensions, projects support to the validated plane, and bounds-checks the resulting vertices.
- **S10b:** `rk4Step` and `integrateRK4` implement deterministic fixed-step classical RK4. Caller supplies state, dynamics, `dt`, and steps; inputs are not mutated and finite/dimension/range checks fail closed.
- **Smoke:** exponential ODE `y'=y`, `dt=.01`, 100 steps gives `e` within `1e-8`; repeated integration is byte-for-byte deterministic; malformed snapshot, forged snapshot, zero `dt`, non-finite derivative/state, and fractional steps are rejected.

The boundary is intentionally a small browser-portable validator for the apparatus snapshot subset. It is not claimed to replace the Python scene contract validator, and no browser runtime or physical simulation result is claimed.
