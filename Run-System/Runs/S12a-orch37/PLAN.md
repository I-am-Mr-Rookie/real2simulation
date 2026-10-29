# S12a-orch37 PLAN (worker 01a18968, issued 2026-10-29T20:44:39Z)

- Lane CODEX-1, anthropic/claude-opus-5-5/high; OpenCodex-managed, not polled. Deadline 21:14:39Z (Dhaka 03:14:39); cutoff 21:09:39Z.
- Objective: smallest boundary module freezing the held-out suffix before any fit; tests proving no leakage; evidence/S12 boundary record with Gate M NOT_MET.
- Owns: Build/real2sim/; tests/prediction/; evidence/S12/; Run-System/Runs/S12a-orch37/.
- Reuse: Build.fitter.select_model; accepted S07b orch14 ST03 track; recovery3 presentation map; S07f Gate M record.
- Checks: unittest tests/prediction, tests/measurement, tests/fitter; python -m Build.real2sim.boundary; worker_timebox check.
- Duplicate-dispatch note: worker 01a18967 (issued 20:43:22Z) used the same worktree/branch; its PLAN/REPORT are in commit f74b383.
