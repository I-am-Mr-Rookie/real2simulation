# S10ab swarm validation

Synthetic-only evidence. This does not unlock real-scene integration or Gate R/M/P/RS/S12.

- **S10a:** `export_validated_setup.py` calls the existing full Python `validate_setup(spec, scene, scene_root)`, including experiment schema/numeric checks, authoritative scene schema, colliders, bounds and stability. The JS module consumes only that exact producer/validation envelope and places the S08 body with scene geometry attached. Invalid spec export is covered by a Python regression.
- **S10b:** `rk4Step` and `integrateRK4` implement deterministic fixed-step classical RK4. Caller supplies state, dynamics, `dt`, and steps; inputs are not mutated and finite/dimension/range checks fail closed.
- **Smoke:** exponential ODE `y'=y`, `dt=.01`, 100 steps gives `e` within `1e-8`; repeated integration is byte-for-byte deterministic; malformed snapshot, forged snapshot, zero `dt`, non-finite derivative/state, and fractional steps are rejected.

The JS side is not an authority claim or replacement for Python validation; it consumes the explicit trusted export boundary. No browser runtime or physical simulation result is claimed.
