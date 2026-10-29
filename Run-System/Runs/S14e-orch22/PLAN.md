# S14e-orch22 PLAN

- Objective: Muse Spark trial check (offline adapter): after a lab trial, Spark comments on the trial; every number in its reply must reference the actual simulator/fitter tool outputs of THAT trial, produced in tests.
- Model: anthropic/claude-opus-5-5 high. Issue 2026-10-29T12:26:31+00:00, deadline 12:56:31Z, cutoff 12:51:31Z. Worktree created 12:28:55Z.
- Owns: Build/agent/; contracts/agent/; tests/agent/; evidence/S14/; Run-System/Runs/S14e-orch22/.
- Deps: S14a-d DONE on main 0ca50f2. NO live Meta/Muse calls (billing hold, API_BUDGET.md); hand-written SYNTHETIC Spark replies only.
- Plan: Build/agent/trial.py (S10 session-bridge start/fit -> [simulator, fitter] tool outputs; Spark request via muse.build_request(instructions=...); validate_check; check_trial bounded retry; tool-only fallback). tests/agent/test_trial.py runs the real S10 simulator + fitter. CONTRACT.md S14e section. Evidence: unittest, mutation, probe.
- Checks: tests/agent unittest; tests/spec regression; mutation spot checks.
