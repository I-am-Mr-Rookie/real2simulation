# S21e-orch137 PLAN
Objective: finish BENCHMARK.md (summary first, gates incl. Gate A, honest limits) without touching generated tables; generate app About data from evidence JSONs with a regeneration test.
Owns: BENCHMARK.md; Build/benchmark/; Build/web/src/about/; Run-System/Runs/S21e-orch137/.
Base main b82b1a6. Model anthropic/claude-opus-5-5/medium; OpenCodex-managed, not polled.
Checks: python -B -m unittest discover -s Build/benchmark -p "test_*.py".
