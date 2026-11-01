# S15bf checks (fresh, 2026-11-01, worktree .worktrees/S15bf-orch243)
- python -m unittest tests/api-workspace/test_live_fit.py tests/api-workspace/test_analysis.py tests/api-workspace/test_jobs.py -> Ran 28 tests, OK
- PYTHONPATH=tests/api-workspace python -m unittest tests/api-workspace/test_spec_q16.py -> Ran 4 tests, OK (extra, unchanged route branch)
- node --test tests/workspace/*.test.mjs tests/web-workspace-api/*.test.mjs -> tests 133, pass 133, fail 0
- Build/web npm run build (node_modules = junction to canonical Build/web/node_modules, no install) -> EXIT 0
No deploy, no GPU, no paid call, no secrets read.

