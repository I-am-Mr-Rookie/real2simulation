# S18i-orch132 PLAN

- Objective: measure guest-library load times (manifest + artifact fetch/validate + loader.mjs) for every entry; report how many demos open < 3 s.
- Owns: Build/library/ (new load_times.py, load_times.mjs); tests/library/test_load_times.py; evidence/S18/S18i-load-times.json; Run-System/Runs/S18i-orch132/.
- Lane/model: CODEX-2 (army: Claude), anthropic/claude-opus-5-5/medium; OpenCodex-managed, not polled.
- Issued 2026-10-30T11:08:17Z; deadline 11:38:17Z; cutoff 11:33:17Z.
- Checks: benchmark run on idle machine; tests/library discover; worker_timebox check.
- Not in scope: Build/web (S04j), changing guest.py request-time validation (design decision; reported as bottleneck).
