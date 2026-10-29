# S13f-orch30 PLAN
Lane CLAUDE (anthropic/claude-opus-5-5/high; OpenCodex-managed, not polled). Parent project Meta AI Hackathon 91e441f8-e40c-4ec4-bea2-de7fa1582d97.
Issued 2026-10-29T15:42:44Z; deadline 16:12:44Z; cutoff 16:07:44Z. Base main 90d6f45. Worktree .worktrees/S13f-orch30, branch run/S13f-orch30.
Objective: connect segment (SAM3.1, S07b) and reconstruct (MapAnything scene_job, S06d) to the S13d JobRunner; validated outputs; readable/retryable failures.
Owns: Build/pipeline/, contracts/jobs/, tests/pipeline/, Run-System/Runs/S13f-orch30/.
Checks: (1) offline fakes: validated outputs, readable StageErrors, retry + out:<key> reuse with no duplicate paid dispatch; (2) <=2 Modal GPU jobs on one approved clip, cap <=$1, retries 0, ledger, billed reconcile, containers [] after.
