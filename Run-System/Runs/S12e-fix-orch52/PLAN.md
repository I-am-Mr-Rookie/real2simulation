# S12e-fix-orch52 — PLAN

- Objective: fix R-RS F1–F4 (evidence/reviews/R-RS/REVIEW.md) in S12 scoring/overlay; one regression per reproduction; regenerate gate-rs.json from existing tracked results only.
- Lane CODEX-1, step S12; assigned anthropic/claude-opus-5-5/high (OpenCodex-managed; not polled). Parent project 91e441f8-e40c-4ec4-bea2-de7fa1582d97, canonical root event folder; worktree .worktrees/S12e-fix-orch52, branch run/S12e-fix-orch52 from main 4b950c6.
- Window: issued 2026-10-29T22:05:53Z, cutoff 22:30:53Z, deadline 22:35:53Z (Dhaka 04:35:53 Oct30).
- Owns: Build/real2sim/, contracts/overlay/, tests/prediction/, evidence/S12/, Run-System/Runs/S12e-fix-orch52/. Not touched: evidence/reviews/, Build/pipeline, Build/measurement, canonical controls.
- Checks: (1) tests/prediction all new regressions pass; (2) every reproduction replayed and refused; (3) regenerated gate-rs.json still NOT_MET with identical measured values; Gate M NOT_MET in all S12 JSON.
- No GPU/Modal/Meta/AWS jobs, no installs.
- Note: PLAN written after the code edits in this session (worktree was created first); content matches the controller contract.
