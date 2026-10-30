# S07j-orch173 PLAN
Lane CLAUDE, anthropic/claude-opus-5-5/high (OpenCodex-managed; not polled). Issued 2026-10-30T23:44:12Z, deadline 2026-10-31T00:14:12Z, cutoff 00:09:12Z.
Objective: fix S07i batch CUDA OOM (load SAM once per container) + reviewed standalone envelope 2 (no release of old rows) + re-track command for OWN07-OWN11. No Modal run.
Owns: Build/measurement/runtime/; Build/guardrails/standalone.py; tests/measurement/; tests/guardrails/; evidence/S07/S07j/; Run-System/Runs/S07j-orch173/.
Checks: measurement + guardrails unittest discovery; worker_timebox check.
