# S05b recovery7 — LOCAL-ONLY deadline/admission guard

- Contract: canonical `Run-System/Runs/S05b/RECOVERY-7.md`; CODEX-1,
  requested existing managed gpt-6.1-sol / medium. Parent remains PARTIAL.
- UTC first inspection: 2026-10-28 14:05:52; implementation cutoff14:20,
  absolute finish14:25. This plan persisted after initial implementation/tests;
  scope was read from the canonical contract before any edits.
- Existing Meta AI Hackathon project91e441f8-e40c-4ec4-bea2-de7fa1582d97;
  app list_threads confirmed this separate chat01a182d4-596a-7460-854f-195ad12f6c74
  belongs to that project. Canonical root is read-only for this worker.
- Only worktree: `C:/Users/HP/.codex/worktrees/s05b-recovery4/2026-10-26 - Meta Global AI Developer Hackathon`;
  existing branch `run/S05b-recovery7`, clean initial status, base8fca36f4bdade0cb9aff00e4cc52df299d1ab6be.

## Objective / exact Owns

Add caller-level setup+queue+startup+execution+cleanup policy to the existing
single RM02 probe, without changing approved inputs/resources/revisions/retries.
Owns: `Build/reconstruction/spike/{modal_rm02.py,test_modal_rm02.py,README.md}`;
adjacent minimal `rm02_deadline.py` and `test_rm02_deadline.py` required to test
without importing the cloud runner; `evidence/S05/S05b/recovery7/`;
`Run-System/Runs/S05b/recovery7/{PLAN.md,REPORT.md}` only.

## Acceptance / approach

1. Reuse installed documented Modal1.6.3 async run/spawn/get/stop/info/stats and
   stdlib asyncio/monotonic. Reserve startup/execution/cleanup before admission;
   observe a running input conservatively or stop. Explicit fresh stopped/zero
   resource snapshots, not client termination, distinguish confirmed stop.
2. Fake-only tests: impossible budgets, slow setup/enqueue/queue, success,
   exception, hangs, unconfirmed stop, cleanup failure and local evidence failure.
3. Fresh spike tests + scene-schema regressions, diff/scope review, report concrete
   Ponytail reuse/smallest-complete-change choices, skips and residual risks.

No runner imports, service calls, browser, jobs, installs, downloads, credentials,
quota polling, fanout, commits, rebases, merges or control writes. Controller owns
integration. No spending or reserve release; historical$2.85/$30 retained.
