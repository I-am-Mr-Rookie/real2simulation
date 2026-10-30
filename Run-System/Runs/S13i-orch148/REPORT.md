# S13i-orch148 REPORT — DONE

- Lane CODEX-1; model anthropic/claude-opus-5-5/high (coding quota: OpenCodex-managed; not polled). Tokens/cost: unknown (not observable); API/GPU spend $0.
- UTC: issued 2026-10-30T11:50:50+00:00; worker start 2026-10-30T11:51:54Z; work stopped 2026-10-30T11:59Z (DONE early, verified).
- Base main 0b9f688; branch run/S13i-orch148; worktree .worktrees/S13i-orch148. Parent project 91e441f8-e40c-4ec4-bea2-de7fa1582d97.

## Changed (Owns only)
- Build/api/workspace/jobs.py — router + approved_shas + load_recording + recorded_runner + default_store.
- tests/api-workspace/test_jobs.py — 7 tests.
- evidence/S13i/README.md, tests-api-workspace.txt, tests-pipeline.txt.
- Run-System/Runs/S13i-orch148/{PLAN.md,TIMEBOX.json,REPORT.md}.

## Acceptance
1. Resumable upload via UploadService (create / GET resume point / PUT chunk / duplicate retry / complete); non-approved sha -> 422 INVALID_INPUT; other owner -> 404 on upload GET/PUT/complete and job GET. PASS.
2. RM04 sha -> JobRunner + progress replay labelled "RECORDED S13h-orch46", live:false, original UTC (e.g. validate 2026-10-29T21:44:56.313Z). Missing recording -> failed DEPENDENCY_UNAVAILABLE. PASS — with finding: S13h never ran understand, so replay honestly stops at understand (DEPENDENCY_UNAVAILABLE); job never reaches ready. See evidence/S13i/README.md; controller decision needed.
3. Test: recorded executor run with modal/boto3/botocore import-blocked, non-loopback socket connect and Popen forbidden; fresh subprocess shows no modal/boto3/botocore/requests/understand/gpu_stages/e2e modules loaded; source has no such imports. PASS.

## Fresh checks
- python -B -m unittest discover -s tests/api-workspace -t tests/api-workspace -> 14 OK (S14i 7 still pass).
- python -B -m unittest discover -s tests/pipeline -> 53 OK.
- Guard sanity: loopback_only blocks ('93.184.216.34', 443).

## Ponytail (full) — reuse / smallest complete change
- Reused: UploadService (S13b) unchanged; JobRunner/MemoryStore/StageError/_now (S13d) — replay = workers returning recorded shas + a clock iterator, no new runner; progress via JobRunner.progress (S13g); require_owner/error (S14i); score.approved + APPROVAL/REGISTRY constants for the sha gate (tracked registry hashes, no 25 MB file hashing).
- Redis: redis-py client only when REDIS_URL set (import guarded inside default_store); MemoryStore otherwise.
- Skipped: scene resolver (hand-off, no ready job exists); live executor; queue worker (replay inline, shortcut comment); job cancel/list routes (not asked); app.py mount/image/deploy (S04m).

## Risks / limits
- RM04 replay cannot reach ready/viewer without a recorded understand stage (contract order). Biggest item for S15o.
- Without REDIS_URL, jobs live in per-process memory; without WORKSPACE_UPLOAD_DIR, uploads go to OS temp (ephemeral).
- UploadService has no cross-process lock (existing S13b shortcut).
- Approval gate trusts registry sha256 + S02 grant; clips.csv owner_approved column is NO for all rows (pre-existing inconsistency, not changed).

## Communication
Silent run; one completion line to controller chat 01a1882d-3481-7ce3-8f88-45c942e341cd. No owner questions.

Next: S04m mount + redis requirement; controller decides understand gap (S13j capture vs contract recorded-skip).

