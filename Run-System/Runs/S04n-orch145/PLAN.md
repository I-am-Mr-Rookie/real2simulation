# S04n-orch145 PLAN
Lane CODEX-2 (army: Claude), assigned anthropic/claude-opus-5-5/medium; OpenCodex-managed, not polled. Base main 1235cca.
Objective: QUEUE S04n — web BFF `/api/workspace/[...path]` per evidence/S15/S15m/PLAN.md §2.
Owns: Build/web/src/app/api/workspace/; tests/web-workspace-api/; evidence/S04n/; Run-System/Runs/S04n-orch145/.
Acceptance: (1) signed-out 401, no upstream call; (2) forwards only owner+token headers, no cookies, no-store; 8 MiB chunk PUT / 1 MB JSON else 413; (3) missing WORKSPACE_API_URL -> 503 DEPENDENCY_UNAVAILABLE; build PASS.
No paid calls, no deploys, no secret values.

