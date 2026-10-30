# S20-fix-orch63

Parent project: Meta AI Hackathon `91e441f8-e40c-4ec4-bea2-de7fa1582d97`.
Canonical root: `C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon`.
Lane/model: CODEX-2 / assigned gpt-6.1-sol high; OpenCodex-managed; not polled.
Issued 2026-10-30T04:26:17+00:00; implementation cutoff 04:51:17Z;
deadline 04:56:17Z (10:56:17 Dhaka). Base main 5646131.

Objective: repair R-C H1/H2/M1/M2/L2 offline: global durable locked GPU
admission, source-ledger projection, strict snapshot keys/AWS liabilities,
and conservative headroom rounding. Preserve existing per-run/job bounds.

Owns: Build/guardrails/; infra/failover/; tests/guardrails/; evidence/S20/;
Build/pipeline/gpu_stages.py; tests/pipeline/test_gpu_stages.py;
Run-System/Runs/S20-fix-orch63/. No canonical controls or Build/agent edits.

Reach: admission/accounting/failover callers, GPU reserve callers, synthetic
guardrails/pipeline fixtures, contract docs and regression evidence. No cloud,
installs, secrets or actual credit/billing verification. M3 record_muse deferred.

Checks: all six R-C regressions (G1/G3/C1/X1/A15/R1), pipeline and guardrails
unittest discovery, repository-ledger projection inventory, timebox validator.
Reuse existing liability_usd/require_reconstruction; stdlib lock + atomic replace.
Missing/corrupt/unverified runtime state must pause, never bootstrap zero credit.
