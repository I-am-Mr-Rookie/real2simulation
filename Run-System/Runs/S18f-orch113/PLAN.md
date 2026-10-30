# S18f-orch113

Implement a read-only anonymous guest catalogue and SHA-256 artifact endpoint.

- CODEX-2; assigned gpt-6.1-sol / medium; OpenCodex-managed; not polled.
- Parent project: Meta AI Hackathon `91e441f8-e40c-4ec4-bea2-de7fa1582d97`,
  inherited delegation; no new session/project launch or independent binding claim.
- Canonical root: `C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon`.
- Isolated plain Git worktree `.worktrees/S18f-orch113`, branch `run/S18f-orch113`,
  main base `9f44117` (full SHA in report). Canonical controls/main are read-only.
- Issued 2026-10-30T09:07:22+00:00; cutoff 09:32:22Z;
  deadline 09:37:22Z / 15:37:22 Asia/Dhaka. DONE may finish early only after verification.
- Owns: `Build/library/`, `test-data/library-artifacts/`, `tests/library/`,
  `evidence/S18/`, `Run-System/Runs/S18f-orch113/`.

## Smallest complete scope

Reuse `validate_file`, `checked_ref`, `bounded`/existing size constants and
`safe_defaults`; follow FastAPI `create_app` pattern without touching health/web.
Revalidate custody per request (no stale authority cache). Derive content-addressed public simulation
setup projections in memory, not raw acceptance objects shared with Mystery-g.
No source writes, provider imports, new inference, installs, or deployment.

Reach: new handler/factory, focused library tests, library README + S18g interface,
run receipt/evidence. Existing builders/schema/callers/artifacts remain unchanged.
Risks to prevent: arbitrary-hash/path disclosure, answer leakage via alternate
catalogues/defaults, cache corruption, unvalidated entries, false playable/scale claims.

## Acceptance

1. Anonymous manifest and artifacts return correct labels/defaults/hash/headers;
   unavailable Apollo/bounce/RM05 remain unavailable and descriptors metadata-only.
2. Invalid/unknown IDs, tampering, oversize and escaped references fail closed;
   no Mystery-g answer/audit records served, including known raw source hashes.
3. Fresh no-provider/no-network test and full `python -B -m unittest discover
   -s tests/library -t tests/library`; baseline 64 tests passed. Persist evidence,
   timebox check and named-file commit, no canonical merge/control writes.
