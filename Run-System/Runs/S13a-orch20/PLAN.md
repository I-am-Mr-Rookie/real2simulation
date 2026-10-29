# S13a-orch20 plan

- Run: S13a (controller contract S13a-orch20). Lane CODEX-1, model anthropic/claude-opus-5-5/high (OpenCodex-managed; not polled).
- Issued 2026-10-29T12:05:40+00:00; deadline 2026-10-29T12:35:40+00:00; minute-25 cutoff 12:30:40Z. Work started 2026-10-29T12:07:01Z.
- Base: main 4f193cf; worktree .worktrees/S13a-orch20, branch run/S13a-orch20.
- Objective: versioned resumable-upload + job-stage contracts (file limits, retry semantics, stage events), contracts/tests only.
- Owns: Build/pipeline/; contracts/jobs/; tests/pipeline/; Run-System/Runs/S13a-orch20/.
- Reuse: S04g shell job DTO (Build/web/src/shell/integration.schema.json: error codes, revision rule, retry = new job id) and S06a GPU contract id (S06a-gpu-image/v1) for the reconstruct stage. Installed jsonschema as validator.
- Acceptance checks: (1) schema+policy versioned, examples validate, limits consistent; (2) upload resume/duplicate/conflict rules tested; (3) stage-event sequence + retry rules tested and projected onto a shell-schema-valid job snapshot.
- Out of scope: live services, bucket writes, deploys, installs, real media, gate claims.
