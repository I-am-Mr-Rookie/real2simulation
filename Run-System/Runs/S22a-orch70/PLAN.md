# S22a-orch70 PLAN

- Objective: write the Gate D QA protocol + checklist (read-only product inspection; no product code).
- Lane/model: CLAUDE, assigned anthropic/claude-opus-5-5/medium; OpenCodex-managed, not polled.
- Base: main a2fa169b6068bff272e72e58cfc3674f6d8068c4; branch run/S22a-orch70; worktree .worktrees/S22a-orch70.
- Window: issued 2026-10-30T05:09:38Z, cutoff 05:34:38Z, deadline 05:39:38Z.
- Owns: evidence/qa/claude/; Run-System/Runs/S22a-orch70/.
- Acceptance: (1) protocol covers guest, fresh-account x3, 375px/auth, retry/spend-cap/report, capture format for S22b-i;
  (2) pass/fail tied to JUDGE_RUBRIC.md + final plan Gate D; (3) dependency-gated steps marked BLOCKED-BY <row>.
- Expected status: PARTIAL (deps S15k/l, S16, S17f, S19d, S20c/d not DONE; Gate D unverifiable). No deploys.
