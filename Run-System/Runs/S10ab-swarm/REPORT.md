# S10ab-swarm report

- **RID/status:** S10ab-swarm / DONE (S10a and S10b leaves only)
- **Lane:** CODEX-1 medium; synthetic-only owner authorization.
- **Timebox:** issued `2026-10-28T17:11:15Z`; deadline remains `2026-10-28T17:41:15Z`; rework verified at `2026-10-28T17:22:05Z`. `TIMEBOX.json` is adjacent.
- **Commit:** `ff7d96c` (product/evidence commit); report/timebox are committed separately below.

## Changed paths

- `Build/simulator/apparatus.mjs` — consumes only the exact Python `validate_setup` export envelope and places the S08 body against scene bounds/colliders.
- `Build/simulator/export_validated_setup.py` — calls the existing full `validate_setup(spec, scene, scene_root)` before exporting exact spec+scene JSON.
- `Build/simulator/rk4.mjs` — fixed-step RK4 with finite/dense state, dimension, callback and positive-dt guards; no arbitrary upper dt cap.
- `tests/simulator/simulator.test.mjs` — S10a actual-envelope boundary plus S10b convergence/order, determinism, immutability, zero-step and invalid-input tests.
- `tests/simulator/test_s10_adapter.py` — valid exact export and invalid S08 spec rejection.
- `evidence/S10/swarm/S10ab-validation.md` — synthetic evidence and explicit limits.

## Ponytail choices applied

- Reused the repository's plain browser ESM convention; added no dependency, UI, Rapier, contact solver, or config.
- Reused the existing Python scene and experiment validators through a single trusted export adapter; JS only consumes the explicit producer/validation envelope and does not claim to replace Python authority.
- Deep-freezes the cloned validated payload before branding; mutation-after-consume is rejected and placement remains unchanged. Producer labels are explicitly TRUSTED TRANSPORT preconditions, not authentication or public-JSON forgery protection.
- Kept dynamics/state shape caller-owned; no arbitrary defaults or duplicate physics model.

## Fresh checks

- `node --test tests/simulator/simulator.test.mjs` — **3/3 pass**, exit 0.
- `$env:PYTHONPATH='tests\\spec;tests\\simulator'; python -m unittest test_s10_adapter` — **2/2 pass**, exit 0; invalid spec cannot enter export.
- `python contracts/scene/validate_scene.py test-data/synthetic/scene/room-v1/scene.json` — **PASS**, exit 0; synthetic and not Gate R evidence.

## Limits / skipped work

No real S09/S07 integration, browser runtime claim, Rapier/contact/default physics, model/media access, deployment, or Gate R/M/P/RS/S12 work. JS is not an authority claim; Python `validate_setup` remains authoritative. All fixtures/results are synthetic.

## Communication compliance

Worked silently; no owner question or cross-chat message was needed. No shared controls, manifests, lockfiles, credentials or unrelated files were edited.

