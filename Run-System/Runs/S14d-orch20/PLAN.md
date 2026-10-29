# S14d-orch20 PLAN

- Objective: bounded validator-retry loop for Muse scene understanding; max 3 retries; unresolved -> code-owned ask-user question, never fabricated candidates/numbers.
- Model: anthropic/claude-opus-5-5 high. Issue 2026-10-29T12:06:16+00:00, deadline 12:36:16Z, cutoff 12:31:16Z. Started 12:07:11Z.
- Owns: Build/agent/; contracts/agent/; tests/agent/; evidence/S14/; Run-System/Runs/S14d-orch20/.
- Deps: S14a-c DONE on main 4f193cf. No live Meta/Muse calls (billing hold); recorded fixtures + SYNTHETIC mutations only.
- Plan: muse.build_request(feedback) + muse.understand_with_retry + ask_user; tests/agent/test_retry.py; CONTRACT.md S14d section; evidence unittest/mutation/probe.
- Checks: tests/agent unittest; tests/spec regression; mutation spot checks.
