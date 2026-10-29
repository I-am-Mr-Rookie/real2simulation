# S13h-orch46 PLAN

Objective: measure the dev upload-to-scene path end to end with timestamps for approved RM04 (<6 min = policy job_deadline_s 360, or measured failure); offline retry tests pass.
Lane CODEX-1; assigned anthropic/claude-opus-5-5/high; OpenCodex-managed, not polled. Base main 1e052d4, branch run/S13h-orch46.
Issued 2026-10-29T21:41:29Z; deadline 22:11:29Z; minute-25 cutoff 22:06:29Z.
Owns: Build/pipeline/; contracts/jobs/; tests/pipeline/; evidence/S13/S13h/; Run-System/Runs/S13h-orch46/.
Route check: Build/web/src/app/api has only lab/route.js; Build/api has health only -> no upload route; measure the pipeline CLI path (finding).
Steps: Build/pipeline/e2e.py driver (UploadService upload -> sha validate -> keyframes -> live segment -> live reconstruct -> validated scene bundle), timing.json per stage. Modal: <=2 jobs, <=$1 total, <=$0.50 each (existing gpu_stages ledger guard), retries 0, containers before/after, billed reconcile read-only via Build/gpu/cost_log.py.
Checks: tests/pipeline full suite + small e2e offline test.
