# S06b-orch20 PLAN — Package MapAnything runtime

Lane CODEX-1; anthropic/claude-opus-5-5 high (OpenCodex-managed; not polled). Issue 12:04:00Z, deadline 12:34:00Z, cutoff 12:29:00Z.
Worktree .worktrees/S06b-orch20, branch run/S06b-orch20 from main 4f193cf. Worker start 12:05:15Z.

Objective: GPU runtime on the S06a pinned IMAGE (no in-function pip) + recorded dependency/licence checks; one bounded
A10G warm-start smoke (cap <= $0.50, retries 0, max 1 container) measuring setup vs S05b in-function-pip baseline.

Owns: Build/gpu/; infra/modal/; evidence/S06/; Run-System/Runs/S06b-orch20/. Not Build/reconstruction/spike/ (S05c).

Steps: runtime.py (load_model offline + GPU smoke on visibly synthetic frames + installed-dist licence metadata dump);
licence_audit.py (+tests) classifies the dump; pre billing/app/container read-only; ledger reserve; one run; stop/verify [].
Acceptance: image (S06a layers) used on A10G, CUDA + model load + synthetic forward OK; licence audit recorded with
zero denied (NC/ND/proprietary) or the exceptions listed; cost/timings measured. No scene/Gate R/physical claims.
