# S18b-orch90

Objective: precompute an offline free-fall display library from accepted evidence,
without claiming calibrated real-clip motion or running new compute.

Issue 2026-10-30T06:21:50+00:00; cutoff 06:46:50Z; deadline 06:51:50Z.
Parent project Meta AI Hackathon 91e441f8-e40c-4ec4-bea2-de7fa1582d97;
controller 01a1882d-3481-7ce3-8f88-45c942e341cd. Requested CODEX-2,
gpt-6.1-sol/medium; OpenCodex-managed; not polled.
Base main 1dfc4e2; branch run/S18b-orch90; plain isolated Git worktree.

Owns: Build/library/; test-data/library-artifacts/; tests/library/;
evidence/S18/; Run-System/Runs/S18b-orch90/. No canonical control writes.

Reach: manifest schema, validator callers (example/CLI/tests), offline builder,
content-addressed fixtures, README, run evidence. Preserve existing v1 real-clip
approval/hash/ledger checks. Add only local synthetic provenance needed for actual
S10 free-fall records; never invent a clip ID or successful GPU ledger.

Reuse: S18a ref/digest/validation, existing accepted S06d RM02 descriptor and
S10hi-gate acceptance JSON. Copy original bytes, select free-fall cases through
numeric pointers; include exact Gate M and SCALE_UNVERIFIED warnings.
Real RM02 is reconstruction/display only, not a measured free-fall fit.

Checks: requested library unittest discovery; validator CLI on offline manifest;
deterministic rebuild, corruption/label/provenance rejection, diff/scope checks.
No dependencies, GPU/API spend, routes, deployment, media copy or publication.
