# S05b-recovery9 local review fixes

- Issued 2026-10-28T15:23:32+00:00; cutoff 15:48:32Z; deadline 15:53:32Z / 21:53:32 Dhaka.
- CODEX-1; requested managed gpt-6.1-sol / medium. OpenCodex-managed; not polled.
- Fresh desktop chat 01a1831c-0155-7a73-b280-9c79423a8810; app list_threads verified existing project 91e441f8-e40c-4ec4-bea2-de7fa1582d97. Launcher canonical cwd; every write explicitly targets prepared s05b-recovery4 checkout, branch run/S05b-recovery9, initially clean.
- Owns only spike rm02_watchdog.py, test_rm02_watchdog.py, test_rm02_deadline.py, README.md; one narrow .gitignore path; evidence/S05/S05b/recovery9/; this run's PLAN/REPORT/TIMEBOX. No commits/control edits/network/Modal imports/real CLI.

## Smallest complete change (Ponytail full/default)
Reuse existing bounded invoke and receipt logic: poll exact same app info/containers inside original reserve, preserve incident/ack distinctions, UTF-8 CLI environment. Reuse local child/CLI doubles for transition, exhaustion, Unicode and fail-closed limits. Fix only test timing assumptions, not production budgets. Ignore only generated attempt local bytes. Document F3/F4 limits and keep paid-readiness hold rather than changing unowned runner.

## Checks
Capture baseline target-3.11 deadline failure with a parent cap; run focused regressions and both full spike suites under 90s parent caps using -E -s -B, plus scene contract suites. Check narrow ignore positives/negatives, diff/Owns, production constants, and TIMEBOX before callback. All four contract criteria required for early child DONE; parent remains PARTIAL. $2.85/$30 unchanged.
