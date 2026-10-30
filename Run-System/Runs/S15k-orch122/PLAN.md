# S15k-orch122 PLAN
Lane CLAUDE; anthropic/claude-sonnet-5-5/high (OpenCodex-managed; not polled). Issue 2026-10-30T09:37:43Z, deadline 10:07:43Z, cutoff 10:02:43Z. Branch run/S15k-orch122 from main 27a1197.
Objective: redeploy main to Railway DEV web only, walk the signed-in in-app-browser workflow, record per-stage PASS/NOT-WIRED/FAIL, fix only small defects inside Owns.
Owns: Build/web/src/workspace/, tests/workspace/, evidence/S15/, Run-System/Runs/S15k-orch122/, append-only receipt in infra/railway/dev/deployments.json.
Acceptance: (1) dev web deployed from main, verify run; (2) per-stage record with URLs/screenshots incl. logged-out/other-scene 404, desktop+375px; (3) DONE only if upload->report genuinely completes in browser, else PARTIAL with exact missing wiring.
Boundaries: no new services/variables/credentials, no GPU/API jobs, no personal uploads, no auth change, no production deploy.
