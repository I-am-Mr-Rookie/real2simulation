# S05b-recovery9 — DONE (local child contract only)

**F1/F2/F5/F6 fixed locally; both full spike suites47 PASS, default scene11 PASS.
F3/F4 explicitly retained fail-closed limits. Parent S05b PARTIAL; NOT paid-ready.**

## Identity / scope / time

- Requested CODEX-1, existing managed gpt-6.1-sol / medium; actual backend/effort,
  token usage and subscription cost not independently observable. Coding quota:
  **OpenCodex-managed; not polled**. No route/policy/credential changes.
- Fresh separate desktop chat01a1831c-0155-7a73-b280-9c79423a8810; app list_threads
  verified existing project91e441f8-e40c-4ec4-bea2-de7fa1582d97. Launcher canonical
  cwd; every write/command used prepared s05b-recovery4 checkout explicitly.
- Branch run/S05b-recovery9, initial clean HEAD ac1ad81c5c29056ddeca5436c24165be60061b63.
  No canonical writes, staging, commit, rebase, merge, fanout or shared-control edit.
- Issued2026-10-28T15:23:32+00:00; first inspection15:23:58Z; implementation cutoff
 15:48:32Z; hard deadline15:53:32Z =21:53:32 Dhaka. Task work stopped15:30:05Z,
  after all four local criteria verified; report/TIMEBOX closeout afterward.
  Original full1800s window preserved; verified child DONE is the permitted early exit.
- CONTRACT read FIRST, current canonical AGENTS/owner transcription/timebox policy,
  manual protocol and relevant current control/startup excerpts inspected; no PDF
  rerender. Prior recovery8/recovery7/diagnostic6 reports and independent guard2
  REPORT/FINDINGS read at actual on-disk paths.

## Acceptance / F1-F6

1. **F1 FIXED:** reuse existing bounded `invoke`, poll exact same app info AND
   containers until matching ID + stopped + empty containers, within original
   reserve. No repeated stop, enumeration, ID guess or reserve extension. Receipt
   adds verification_attempts; acknowledgement and independent confirmation remain
   distinct. Focused regressions cover lifecycle transition, container lag, exact
   repeated arguments and persistent-state reserve exhaustion with resource incident.
   **F5 FIXED:** same CLI seam passes explicit UTF-8 environment. Local Unicode
   JSON test succeeds despite inherited cp1252; no real CLI was invoked.
2. **F2 FIXED:** baseline actual3.11 deadline suite reproduced19 tests/errors3.
   Real test-only budgets scaled10x above Windows15.6ms ticks; publication test
   now uses event synchronization, not relative sleep ordering. Also scaled the
   remaining slow-cleanup timer test, avoiding the same sub-tick assumption.
   Production1200/90/900/60/20/10-second budgets unchanged. No skipped tests.
   Fresh full suites47 PASS on both default3.14.5 and required3.11.15, each with
   `-E -s -B` and90s parent subprocess cap. Scene default11 PASS.
3. **F6 FIXED:** exactly one ignore rule,
   `/evidence/S05/S05b/recovery8/attempt-*/local/`, matching unchanged actual entry
   point. `audit.json` proves local result/partial bytes ignored and source/input/
   worker/watchdog/GPU-result receipts NOT ignored.
   **F3 RETAINED:** parent starts earlier than relative child clock; late cleanup/
   non-atomic writes may lose results. New synthetic late-result test proves
   file presence cannot override killed-client failure after confirmed cleanup.
   **F4 RETAINED:** preflight failure without receipt and lost app-ID remain
   conservative unknown-remote-state incidents; new explicit preflight test proves
   no shutdown success or guessed CLI call. Detailed source evidence/disposition:
   [limits.md](../../../../evidence/S05/S05b/recovery9/limits.md).
   Acceptable ONLY as this local child contract's fail-closed limits, not paid
   admission. No unowned runner refactor or silent scope expansion.
4. Evidence, commands, exact runtime versions, hashes, Owns audit and timing receipt
   saved. All local owned acceptance complete. Parent remains PARTIAL, not203-leaf,
   Gate R, reconstruction, calibration or physical success.

## Fresh commands / evidence

Run from prepared checkout; `checks.py` uses subprocess.run(timeout=90) and records
the exact interpreter + `-E -s -B -m unittest discover ... -v`, exit and full log.

| Command | Result / evidence under evidence/S05/S05b/recovery9/ |
|---|---|
| `python -B evidence/S05/S05b/recovery9/checks.py baseline-py311 <target-python> deadline` |19 tests/errors3; baseline-py311.txt/.json (failure retained) |
| `python -B evidence/S05/S05b/recovery9/checks.py spike-py311 <target-python> spike` |47 PASS,33.312s parent elapsed; spike-py311.txt/.json |
| `python -B evidence/S05/S05b/recovery9/checks.py spike-default python spike` |47 PASS,26.786s; spike-default.txt/.json |
| `python -B evidence/S05/S05b/recovery9/checks.py scene-default python scene` |11 PASS,2.918s; scene-default.txt/.json |
| Additional `... checks.py scene-py311 <target-python> scene` |ImportError: bare3.11 lacks jsonschema; scene-py311.txt/.json. Scene acceptance verified on default; target scene dependency parity NOT_VERIFIED. No install/path injection/test skip. |
| `python -B evidence/S05/S05b/recovery9/audit.py` |PASS: branch/Owns, diff-check, constants, unchanged runner/dependencies, narrow ignore positives/negatives, source SHA256 and runtime versions; audit.json |
| `python -B Run-System/worker_timebox.py check Run-System/Runs/S05b-recovery9/TIMEBOX.json` |See timebox-check.txt; arithmetic only, controller still reviews acceptance |

`<target-python>` is the exact required existing interpreter:
`C:/Users/HP/AppData/Roaming/uv/python/cpython-3.11-windows-x86_64-none/python.exe`.
Version3.11.15 / GetTickCount64 resolution0.015625s; default3.14.5 /
QueryPerformanceCounter resolution1e-7s (audit.json). Focused regressions execute
inside BOTH full suites, not merely source-inspected assertions.

## Ponytail full/default / smallest complete change / risks

Installed5.3.2 full/default read/APPLIED. Root cause fixed once in existing CLI
invoke/verification seam; existing receipt, timeout/kill and local double patterns
reused. Stdlib only, no dependencies/framework/abstraction. Test timing changes
stay in tests; unowned runner, requirements, inputs and guard production constants
unchanged. Exact changed tracked paths are the four owned spike files plus the
single ignore rule; only recovery9 evidence and this run PLAN/REPORT/TIMEBOX added.

Skipped: Modal/runner imports, real CLI/RPC/network/browser, jobs/install/download/
upload, model execution, reservations, credentials, purchases, provider changes,
remote shutdown/live billing/headroom/licence admission, and Git integration.
**$2.85/$30 unchanged.** Remote state/lifecycle/CLI-auth NOT_VERIFIED. Parent death,
OS/filesystem stalls and network partitions remain outside local supervision proof.
F3 absolute-budget/write-margin/atomic-result work requires separately owned runner
follow-up before paid admission; F4 needs operator reconciliation on unknown IDs.
Parent S05b PARTIAL; Gate R NOT_RUN; S05c and physical/calibration holds unchanged.

Communication: mandatory Ponytail announcement only; otherwise silent, no blocker
coordination needed. One authorized terminal status/absolute-report-pointer message
to controller01a182c4-9378-7da0-9fbc-99a5a379380c. No duplicated chat report.
Run records are ignored by existing rules; integrator must preserve these exact
local PLAN/REPORT/TIMEBOX paths. No commits or control updates authorized here.
