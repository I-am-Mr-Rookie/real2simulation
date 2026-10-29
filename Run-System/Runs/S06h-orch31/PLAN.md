# S06h-orch31 PLAN
Objective: checkpoint GPU runtime + fallback evidence (measured vs estimated vs billed, per-scene timing, Modal MTD, chosen path, risks) from EXISTING evidence; CPU only, $0, no GPU job.
Owns: Build/gpu/; infra/modal/; evidence/S06/; Run-System/Runs/S06h-orch31/ (only evidence/S06/ + run dir written).
Model: anthropic/claude-opus-5-5 medium. Issued 2026-10-29T15:47:18+00:00, deadline 16:17:18Z, cutoff 16:12:18Z.
Checks: CHECKPOINT.json generator asserts; Build/gpu unittest; worker_timebox.py check.

