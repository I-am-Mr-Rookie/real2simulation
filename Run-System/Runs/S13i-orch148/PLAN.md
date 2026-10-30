# S13i-orch148 PLAN

- Run: S13i (QUEUE; S15m rows.md row S13i). Lane CODEX-1, model anthropic/claude-opus-5-5/high (OpenCodex-managed; not polled).
- Parent project Meta AI Hackathon 91e441f8-e40c-4ec4-bea2-de7fa1582d97; worktree .worktrees/S13i-orch148, branch run/S13i-orch148 from main 0b9f688.
- Issued 2026-10-30T11:50:50Z; cutoff 12:15:50Z; deadline 12:20:50Z (Dhaka 18:20:50).
- Objective: Build/api/workspace/jobs.py APIRouter (resumable upload + job status/progress, behind require_owner) with a RECORDED-replay executor over evidence/S13/S13h; approved-sha gate.
- Owns: Build/api/workspace/jobs.py; tests/api-workspace/test_jobs.py; evidence/S13i/; Run-System/Runs/S13i-orch148/.
- Checks: tests/api-workspace (S14i 7 + new), tests/pipeline.
- No mount in app.py, no image/deploy, no GPU/API spend, no installs.

