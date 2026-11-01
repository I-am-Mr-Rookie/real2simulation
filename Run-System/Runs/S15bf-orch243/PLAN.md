# S15bf-orch243 PLAN
Objective: fix R-D F1 (owner-clip known-size question has chips + free text; owner branch returns a validated owner spec before any result) and F5 (legacy job without u_budget never pairs rescaled g with old-scale u).
Owns: Build/api/workspace/analysis.py; Build/web/src/workspace/; tests/api-workspace/; tests/workspace/; tests/web-workspace-api/; evidence/S15bf/; Run-System/Runs/S15bf-orch243/.
Lane CLAUDE, anthropic/claude-opus-5-5 medium. Issued 2026-11-01T08:12:29+00:00, deadline 08:42:29Z, cutoff 08:37:29Z.
Checks: python unittest test_live_fit/test_analysis/test_jobs; node --test tests/workspace + tests/web-workspace-api; npm run build in Build/web.

