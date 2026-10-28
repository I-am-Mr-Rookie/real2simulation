# S05b-recovery8 — local-only guard repair

Issued 2026-10-28T14:49:41+00:00; implementation cutoff15:14:41Z;
hard deadline15:19:41Z /21:19:41 Asia/Dhaka. CODEX-1, requested managed
gpt-6.1-sol/medium. Existing project91e441f8-e40c-4ec4-bea2-de7fa1582d97;
separate chat01a182fd-0856-7fd2-9cf9-8a060a677995 verified in app list_threads.
Prepared run/S05b-recovery8 at e68b88b; initial tree clean.

Objective: fix late stop and bound a hung client independently, with exact-own-app
fresh CLI stop/state/container checks in source only; no cloud execution.

Owns: Build/reconstruction/spike necessary guard source/tests/README (pins read-only),
evidence/S05/S05b/recovery8/, this PLAN/REPORT/TIMEBOX. No controls/git mutation.

Apply Ponytail full/default: reuse existing guard/resource/input policies, Python
stdlib subprocess timeout and atomic os.replace. No new dependency/scheduler.
Tests: expired clocks and slow cancellation, hung isolated child, ID loss, fresh
independent stop/confirmation failure, evidence failure, existing spike+scene suite.
SDK1.6.3 read as installed text only. Never import Modal/runner or execute RPC here.
