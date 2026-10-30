# S21c-orch135 PLAN

- Objective: QUEUE S21c — held-out prediction errors (Gate RS metric, image-height fraction, Q15=A) from accepted S12 evidence only.
- Lane/model: CODEX-2 (army: Claude), anthropic/claude-opus-5-5 high; OpenCodex-managed, not polled.
- Issued 2026-10-30T11:15:35+00:00; deadline 11:45:35Z; cutoff 11:40:35Z. Base main e9e226f.
- Owns: BENCHMARK.md; Build/benchmark/; evidence/S21/; Run-System/Runs/S21c-orch135/.
- Approach: reuse S21b pattern (errors.py ref/markdown, manifest check+leakage, resolve pointers, null() fail-closed).
- Checks: python -B -m unittest discover -s Build/benchmark -p "test_*.py"; manifest check; worker_timebox check.
