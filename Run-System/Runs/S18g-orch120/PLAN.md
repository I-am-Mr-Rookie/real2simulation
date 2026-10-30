# S18g-orch120 — library loading integration

- CODEX-2 / S18 / assigned gpt-6.1-sol medium; OpenCodex-managed; not polled.
- Parent project (delegation): `91e441f8-e40c-4ec4-bea2-de7fa1582d97`.
- Canonical root: `C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon`.
- Isolated plain Git worktree `.worktrees/S18g-orch120`, branch `run/S18g-orch120`, base `de2bdaed6c7cea0cc2cd206f41635ff380233499`.
- Issued 2026-10-30T09:22:34+00:00; cutoff 09:47:34Z; deadline 09:52:34Z (15:52:34 Dhaka).

## Objective / reach

Consume S18f guest entries with bounded fetch, byte/SHA verification and explicit
kind handling. Reuse viewer request validation, byte reader/limits and banners;
never manufacture missing geometry or turn metadata into playable evidence.
Reach: new framework-free `Build/library/loader.mjs`, library tests, library README,
`evidence/S18/S18g-LOADER-INTERFACE.md`, and this run's receipts only. Existing
guest callers/schema/fixtures/config/exports need no migration. No viewer/app edits.

Owns: `Build/library/`, `test-data/library-artifacts/`, `tests/library/`,
`evidence/S18/`, `Run-System/Runs/S18g-orch120/`. Canonical controls untouched.

## Checks / risks

1. All actual guest entries: labels/defaults and answer withholding survive;
   real descriptor requests satisfy `checkViewerRequest`; absent assets refuse mount.
2. Unknown kind, invalid URL/hash/length/JSON/labels, stream overflow and unavailable
   entries fail readably without arbitrary fetches or inference.
3. Existing 72 Python library tests plus new loader contract tests; read-only viewer
   regression tests. No installs, GPU/API/model jobs, deployment or credentials.

S18f serves metadata only: no trajectories, PLY bytes or bundle mount. A valid
viewer request is not a renderable bundle. Report that boundary explicitly.
Ponytail full applied: reuse public viewer helpers; no second decoder/renderer,
new dependency, speculative transport, synthetic replacement or app hookup.
