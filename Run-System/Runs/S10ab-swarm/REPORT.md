# S10ab-swarm report

- **RID/status:** S10ab-swarm / DONE (S10a and S10b leaves only)
- **Lane:** CODEX-1 medium; synthetic-only owner authorization.
- **Timebox:** issued `2026-10-28T17:11:15Z`; work stopped `2026-10-28T17:17:30Z`; deadline `2026-10-28T17:41:15Z`. `TIMEBOX.json` is adjacent.
- **Commit:** `ff7d96c` (product/evidence commit); report/timebox are committed separately below.

## Changed paths

- `Build/simulator/apparatus.mjs` — portable validated-snapshot boundary and deterministic box placement.
- `Build/simulator/rk4.mjs` — fixed-step RK4 stepper/integrator with finite, dimension and range guards.
- `tests/simulator/simulator.test.mjs` — S10a placement/trust-boundary tests and S10b analytic, determinism, immutability, invalid-input tests.
- `evidence/S10/swarm/S10ab-validation.md` — synthetic evidence and explicit limits.

## Ponytail choices applied

- Reused the repository's plain browser ESM convention; added no dependency, UI, Rapier, contact solver, or config.
- Kept the apparatus boundary to the smallest schema subset needed by placement and used a private `WeakSet` brand rather than accepting a caller-supplied `validated` flag.
- Kept dynamics/state shape caller-owned; no arbitrary defaults or duplicate physics model.

## Fresh checks

- `node --test tests/simulator/simulator.test.mjs` — **3/3 pass**, exit 0.
- `$env:PYTHONPATH='tests\\spec'; python -m unittest test_experiment_validation test_setup_validation` — **27/27 pass**, exit 0.
- `python contracts/scene/validate_scene.py test-data/synthetic/scene/room-v1/scene.json` — **PASS**, exit 0; synthetic and not Gate R evidence.

## Limits / skipped work

No real S09/S07 integration, browser runtime claim, Rapier/contact/default physics, model/media access, deployment, or Gate R/M/P/RS/S12 work. The JS validator is only the portable apparatus-snapshot subset; the Python scene validator remains authoritative for full scene bundles. All fixtures/results are synthetic.

## Communication compliance

Worked silently; no owner question or cross-chat message was needed. No shared controls, manifests, lockfiles, credentials or unrelated files were edited.

