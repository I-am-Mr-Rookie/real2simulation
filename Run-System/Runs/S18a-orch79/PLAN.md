# S18a-orch79

- Objective: versioned local-only library manifest, immutable content-addressed JSON artifacts, validator and accepted-evidence example; no routes or compute.
- Parent project: Meta AI Hackathon `91e441f8-e40c-4ec4-bea2-de7fa1582d97` (delegated contract; no new project created).
- Assigned: CODEX-2, gpt-6.1-sol / medium; OpenCodex-managed; not polled.
- Issued 2026-10-30T05:45:09+00:00; implementation cutoff 06:10:09Z; deadline 06:15:09Z (12:15:09 Dhaka).
- Branch `run/S18a-orch79`, worktree `.worktrees/S18a-orch79`, base `dc74261`.
- Owns: Build/library/; test-data/library-artifacts/; tests/library/; evidence/S18/; this run directory. Canonical controls untouched; controller integrates.
- Checks: schema plus semantic validation of example; hostile/mutated manifests, provenance, artifacts and approvals rejected; existing receipt tests remain green.
- Reuse: scene validator JSON parsing, owner-grant/licence helpers, viewer byte limits; JSON Schema and unittest already used by project. No dependency installs.
- Example: S06d RM02 accepted scene descriptor only, not missing/ignored PLY media; measured reconstruction output, SCALE_UNVERIFIED, Gate M/RS NOT_MET, no publication authority.
