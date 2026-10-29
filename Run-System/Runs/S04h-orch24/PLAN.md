# S04h-orch24 PLAN
Objective: fix the web Railway staging allowlist (current main fails build), redeploy dev web, and verify guest route, Clerk sign-in surface and API/worker health at E4 (agent-observed).
Owns: infra/railway/dev/; evidence/S04/s04h/; Run-System/Runs/S04h-orch24/. (No Build/web edits were needed.)
Checks: (1) stage.py web allowlist test + local emulated-Docker build green; (2) Railway dev web deploy SUCCESS; (3) live probe + in-app browser checks.
Lane/model: anthropic/claude-sonnet-5-5 high; OpenCodex-managed, not polled.
