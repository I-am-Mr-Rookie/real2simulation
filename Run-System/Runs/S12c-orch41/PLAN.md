# S12c-orch41 PLAN
Lane CODEX-1 · anthropic/claude-opus-5-5/high · issued 2026-10-29T21:26:43+00:00 · deadline 21:56:43Z · cutoff 21:51:43Z · base main 03e6c2f.
Objective: immutable, hashed predicted held-out traces (projectile real ST03 + SYNTHETIC bounce) from prefix-only params; spy proves no held-out read.
Owns: Build/real2sim/; Build/simulator/; tests/prediction/; tests/simulator/; evidence/S12/; Run-System/Runs/S12c-orch41/.
Checks: tests/prediction (spy/invariance/tamper/ST03 regen); simulator+lab node suites vs main baseline; python -m Build.real2sim.predict.

