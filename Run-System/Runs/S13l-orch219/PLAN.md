# S13l-orch219 PLAN

- Objective: settle the 3 unsettled standalone Modal reservations (S13j Plan 1) via Build.guardrails only, then re-run RM04 MapAnything reconstruction through gpu_stages (reserve <= $0.50), bytes local only.
- Lane CLAUDE, anthropic/claude-opus-5-5/high. Issued 2026-10-31T14:27:21Z; deadline 14:57:21Z; cutoff 14:52:21Z.
- Owns: evidence/S20/runtime/ (guardrails code paths only, canonical checkout); evidence/S13l/; Build/pipeline/recorded/ (new manifest only); .gitignore; Run-System/Runs/S13l-orch219/.
- Steps: (1) append app-id bind events (reserve_gpu append pattern, admission.lock); (2) modal-settlement/1 receipts from read-only billing; settle serially; (3) gpu_stages RM04; confirm stopped + billed vs reserved; (4) manifest with shas, no bytes.
- Checks: reservations.project before/after; settlement exit 0; worker_timebox check.
