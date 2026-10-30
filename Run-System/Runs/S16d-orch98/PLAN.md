# S16d-orch98

- Objective: add an offline-tested Baseten Spark Open ranking adapter over the existing validated local library, returning only contract-owned search items.
- Project: Meta AI Hackathon `91e441f8-e40c-4ec4-bea2-de7fa1582d97`; canonical event root is the parent of `.worktrees`; branch `run/S16d-orch98`, base `3c54a94`.
- Lane/model: CODEX-2, assigned gpt-6.1-sol/medium; OpenCodex-managed; not polled.
- Issued 2026-10-30T06:52:15+00:00; implementation cutoff 07:17:15Z; deadline 07:22:15Z (13:22:15 Dhaka).
- Owns: `Build/sidebar-tools/`, `tests/sidebar-tools/`, `evidence/S16/`, this run directory. No canonical controls, merge, installs, live inference, deployment, or paid requests.
- Reach: new adapter and tests; additive source/metadata bridge in existing sidebar schema; CONTRACT documentation. Existing patch/rebuild callers must remain compatible. Reuse library validation, bounded reads, pointer resolution and strict JSON parsing; model selects IDs, never authors result metadata or numeric receipts.
- Checks: requested sidebar unittest discovery; adjacent agent/spec and library checks as time permits; malformed provider/config/timeout/HTTP tests; sanitized logs; key-name-only credential presence; timing validator; scoped commit.
- Risks: source catalog is metadata-only/local-processing-only, not runnable or calibrated; descriptors without a verified experiment template must be omitted, not guessed. Real endpoint/model availability and balance remain S16e.
