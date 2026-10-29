# Controller handoff — ORCH-20261029-1654 -> successor (Oct29 ~15:05Z)

Predecessor chat 01a1874a-f952-7271-a08f-57fcc3448999 retires (context bloat, owner request).
Main be54d45. 121/217 done. No workers running. Python dispatcher OFF; no schedules/heartbeat.

Read first: AGENTS.md, ORCHESTRATOR.md, STATE.md (top entries), QUEUE.md, API_BUDGET.md,
Run-System/WORKER_TIMEBOX_POLICY.md, Run-System/PARALLELISM_POLICY.md.

## Ready now (python Run-System/runs_view.py)
S06e, S13c (Opus high); S04h, S15g (Sonnet high); R-R (Sol high review of S05e gate_r.py).
S02f PARTIAL: do NOT redispatch without an exact new asset/scale/clock lead (orch21 audit).
S04h note: main may fail Railway build (stage.py web allowlist lacks simulator/ +
lab/session-service.mjs; deploy 7e6e079d FAILED) — fix before next main deploy.

## Open owner items (Reviews for Koushik)
- S05e: does a visually identified standard object (A4 sheet, regulation ball) count as
  source-backed for Gate R? Default: S05f Fallback 2 (planes+boxes), scale labelled unverified.
- SAM 3D Objects access CONFIRMED (evidence/owner/S06/SAM3D-ACCESS.md + screenshot); needs a
  >=32 GB Modal GPU (L40S/A100/H100) under standing GPU auth; first worker pins revision + SHA256.

## Dispatch recipe (worked in orch23)
1. python Run-System/worker_timebox.py issue <RID>  (RID = <QID>-orch<N>) right before create_thread.
2. mcp__codex_app__create_thread: target {type:project, projectId 91e441f8-e40c-4ec4-bea2-de7fa1582d97,
   environment {type:local}}, thinking "high", model anthropic/claude-opus-5-5 | anthropic/claude-sonnet-5-5 | gpt-6.1-sol.
3. Prompt template: copy any entry in DISPATCH-orch23.json (timebox, own worktree .worktrees/<RID>
   on run/<RID>, no canonical control edits, PLAN/TIMEBOX/REPORT, Ponytail full 5.3.3, Owns,
   fixture-first/no gate claims, one completion line to the controller chat — change the chat id).
4. Save receipt DISPATCH-orch<N>.json immediately (git add -f; Run-System/Runs is gitignored).
5. Wait: wait_threads with afterCursor, timeoutMs<=120000; guard non-JSON results.

## Acceptance recipe
worker_timebox.py check <wt>/Run-System/Runs/<RID>/TIMEBOX.json -> read REPORT + diff stat (Owns only)
-> git -C <wt> rebase main -> rerun the report's test commands fresh -> git merge --ff-only run/<RID>
-> flip QUEUE row TODO->DONE (one row at a time) -> STATE entry -> runs_view.py -> commit.
Node tests: pass explicit file list (node --test <files>), not a directory.

## Boundaries (unchanged)
GPU: standing auth evidence/owner/S05/GPU-AUTHORIZATION.md, per-job cap, retries 0, ledger, containers [] after.
Modal ~$0.58/$30 month-to-date. Meta: frugal live calls allowed, log every call; $120 stop/$30 reserve.
No AWS (needs owner $50 alert + access), accounts, terms, purchases, publishing, judging/prod deploys.
In-app browser only, never Chrome. Secrets: key names only. Stop-work Nov4 18:00 Dhaka.
