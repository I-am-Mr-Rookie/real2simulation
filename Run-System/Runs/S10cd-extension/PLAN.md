# S10cd-extension plan

- Objective: real Rapier contacts and common contact-aware output around accepted free-fall/projectile RK4 trajectories.
- Owns: contacts.mjs, contact-runs.mjs, contacts.test.mjs, evidence/S10/extension-contacts/, this run folder.
- Acceptance: actual WASM init/manifolds; explicit finite parameters; stable IDs and same RK4 samples; deterministic tests; cleanup.
- Ponytail: reuse existing RK4 and pinned dependency; no trajectory edits or parent lab integration.
