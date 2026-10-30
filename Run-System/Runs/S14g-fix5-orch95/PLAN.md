# S14g-fix5-orch95 PLAN

- Lane CODEX-1, step S14; assigned anthropic/claude-opus-5-5/high (OpenCodex-managed; not polled). Project 91e441f8-e40c-4ec4-bea2-de7fa1582d97.
- Issued 2026-10-30T06:37:44Z; deadline 07:07:44Z (Dhaka 13:07:44); minute-25 cutoff 07:02:44Z. Base main 2cd5747.
- Objective: close R-A RECHECK-fix4 F1-R2 with a STRUCTURAL unit-binding rule at runtime and, independently, in the oracle; corpus + offline Gate A replay. $0, offline.
- Owns: Build/agent/ (not record_muse.py); contracts/agent/; tests/agent/ (not test_muse.py); evidence/S14/; Run-System/Runs/S14g-fix5-orch95/.
- Checks: (1) all reviewer strings + asymmetries refused at every visible surface and by the oracle, benign "This one fits the scene." / "Please double-check the fit." pass; (2) agent suite green; (3) offline replay counts fallbacks among 30 saved live turns and reports gate_a honestly (Q16=A amended label).
