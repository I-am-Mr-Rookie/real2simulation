# S14f-orch23 PLAN — Enforce tool-only numbers in replies

- Controller contract S14f-orch23; issued 2026-10-29T14:32:47Z; deadline 15:02:47Z; minute-25 cutoff 14:57:47Z.
- Model: anthropic/claude-opus-5-5 high (assigned); coding quota OpenCodex-managed, not polled.
- Base: main f37121c; branch run/S14f-orch23; worktree .worktrees/S14f-orch23.
- Objective: one code path from model reply to user text; an untraced number is blocked and replaced by a
  code-built tool-backed response; traced numbers pass unchanged.
- Owns: Build/agent/; contracts/agent/; tests/agent/; evidence/S14/; Run-System/Runs/S14f-orch23/.
- Approach (Ponytail): reuse S14a validate_response/render and S14e tool_only; add safe_reply + generic
  tool_backed in Build/agent/tools.py; trial.tool_only reuses tool_backed. Close obvious number-word gaps
  ("one point five", ordinals) in the existing word regex.
- Acceptance: unittest — untraced number blocked + replaced by tool-backed text whose every number is a ref;
  traced reply passes unchanged; mutation spot checks kill fallback removal.
- Offline adapter + visibly SYNTHETIC fixtures; 0 live Meta calls. No gate/real-scene/physical claim.
