# S13b-orch23 PLAN

- Run: S13b — implement bucket upload validation (controller contract S13b-orch23).
- Model: anthropic/claude-opus-5-5 high, lane CODEX-1; coding quota OpenCodex-managed; not polled.
- Issued 2026-10-29T14:32:07Z; deadline 2026-10-29T15:02:07Z (Dhaka 21:02:07); minute-25 cutoff 14:57:07Z.
- Branch/worktree: run/S13b-orch23 at .worktrees/S13b-orch23 from main f37121c.

Objective: one upload service on the S13a contract (chunk_decision, schema, policy) with a local
filesystem storage backend (stand-in for a bucket). No real bucket/account/credential/Modal/spend.

Owns: Build/pipeline/; contracts/jobs/; tests/pipeline/; Run-System/Runs/S13b-orch23/.

Acceptance (QUEUE): interrupted upload resumes; unauthorized/invalid input rejected.
Checks: python -m unittest tests.pipeline.test_uploads tests.pipeline.test_contracts.
Evidence is SYNTHETIC bytes only; no gate, real-scene or physical claim.
