# S05b-recovery8 — DONE (local source-lane child only)

**Late-stop omission fixed; independent process watchdog and exact-own-app fresh
stop/verification implemented and locally tested. 42 spike +11 scene tests PASS.
No cloud execution: remote stop/runtime NOT_VERIFIED, parent S05b PARTIAL.**

## Identity, scope and timing

- Handout issued2026-10-28T14:49:41+00:00; minute25 cutoff15:14:41Z;
  deadline15:19:41Z =21:19:41 Asia/Dhaka. First clock14:50:11Z.
  Exact actual work-stop/report times are in TIMEBOX.json; verified local child
  DONE may close early, unlike incomplete outcomes. No deadline reset/padding.
- Requested CODEX-1, managed `gpt-6.1-sol/medium`; actual backend/effort and
  token/subscription costs not independently observable. **OpenCodex-managed;
  not polled**. No model/provider/credential/policy changes.
- App list_threads verified fresh separate chat
  `01a182fd-0856-7fd2-9cf9-8a060a677995`, existing Meta AI Hackathon project
  `91e441f8-e40c-4ec4-bea2-de7fa1582d97`, host local. Launcher cwd is canonical;
  all authored work explicitly used ONLY the prepared s05b-recovery4 worktree,
  branch `run/S05b-recovery8`, initial HEAD`e68b88b6e9dbb320f090a95db1b084cb7d998f54`.
  Initial tracked/untracked status clean. No commits/staging/rebase/merge.
- Canonical RECOVERY-8 read first, current AGENTS/owner transcription/timebox
  policy, queue/state/decisions/budget/rubric and project startup references read.
  Canonical other-vendor FINDINGS.md read directly; cd42ebc guard source inspected.
  Prior recovery5, diagnostic6, recovery7 reports consulted. No PDF rerender.
- Owns only necessary spike source/tests/README, recovery8 evidence and local
  PLAN/REPORT/TIMEBOX. No canonical controls, S07 paths, dependencies or locks edited.

## Concrete Ponytail full/default application

Read/APPLIED installed Ponytail5.3.2 full/default. Structural root cause:
`asyncio.wait_for` is cooperative; after an overshoot the old `before()` skipped
the very stop action needed to limit resources. Reused the existing probe/guard,
input hashing, provider pins, single-job resources, retries0 and egress validation.
Added only stdlib process supervision and atomic JSON, not a scheduler, dependency,
provider wrapper, retry layer or configuration rewrite. One fixed production
entry point launches the existing runner; test seams use isolated local scripts.

## Acceptance evidence

1. **Actual late stop.** Cleanup receives an explicit fresh60s allowance and stop
   gets20s even after the work deadline is exhausted. The independent parent
   bounds the entire child, including this allowance. Stop flags are set at
   invocation, not before an exhausted precheck. RPC dispatch stays NOT_VERIFIED
   until acknowledgement; a late acknowledgement is recorded without claiming
   timely success. Original error type/exception chain and cleanup errors remain.
   Tests cover already-expired fake clocks, real slow cancellation overshoot,
   late stop acknowledgement and evidence failure without skipped stop.
2. **Independent process enforcement.** Parent1200s total starts before client
   imports/setup; child1140s, independently reserved60s for cleanup. A blocked or
   cancellation-resistant child is killed. Killing is explicitly NOT remote stop.
   Parent then starts fresh supported CLI processes: exact-ID stop20s, fresh
   app-info15s, exact-app container query15s, remaining dispatch/kill margin.
   It runs verification even after a failed stop. Matching ID +state stopped +
   successful commands +containers[] are required. Missing/invalid app ID or
   failed confirmation leaves a durable resource incident and no success.
   App ID is opportunistically published during setup; lost publication remains
   an incident, never name/account guessing. Parent/child failures remain failures
   even after resource shutdown is independently confirmed in the local doubles.
3. **Fresh local checks.** Real isolated hung/busy-loop children with published
   and lost IDs exercise the OS-process watchdog. Fresh CLI doubles cover exact
   command arguments, nonzero/already-stopped response, hung stop, running state,
   wrong ID, nonempty containers, malformed JSON, info failure, evidence failures,
   stale attempt directories and exhausted reserve with no false stop-attempt flag.
   Existing resource/input/model revision/retries0/256MiB egress guards remain.

Installed Modal1.6.3 was read **as text**, never imported. Its exact CLI app-ID
regex matters: nonmatching identifiers are treated as names. `app stop --yes`
and fresh info/container JSON semantics were read directly, not guessed from
review citations. Source paths/line references/SHA256 and limitations:
[API-SOURCE.md](../../../../evidence/S05/S05b/recovery8/API-SOURCE.md).

## Changed files / fresh verification

- `Build/reconstruction/spike/rm02_deadline.py`: late cleanup, honest stop fields,
  app-ID publication during setup.
- New `rm02_watchdog.py`: stdlib parent, bounded fresh exact-ID CLI stop/checks,
  unique attempt directory and atomic receipts, durable initial incident receipt.
- `modal_rm02.py`: refuses accidental direct entry before Modal import, uses
  parent-provided receipt/budget; all remote resource/input/revision settings unchanged.
- `test_rm02_deadline.py`, new `test_rm02_watchdog.py`, `test_modal_rm02.py`, README.
- This directory's PLAN/REPORT/TIMEBOX and recovery8 evidence only.

| Fresh check | Result / saved evidence |
| --- | --- |
| `python -m unittest discover -s Build/reconstruction/spike -p 'test_*.py' -v` | **42 PASS**,8.839s, exit0; [full log](../../../../evidence/S05/S05b/recovery8/spike-tests.txt) |
| `python -m unittest discover -s contracts/scene -p 'test_*.py' -v` | **11 PASS**,2.826s, exit0; [full log](../../../../evidence/S05/S05b/recovery8/scene-tests.txt) |
| `git diff --check` | PASS |
| requirements.in /requirements-linux-py311.txt vs HEAD | unchanged, empty diff |
| Authored source hashes | [SOURCE-HASHES.txt](../../../../evidence/S05/S05b/recovery8/SOURCE-HASHES.txt) |
| Canonical worker_timebox.py check | Result saved in recovery8/timebox-check.txt; arithmetic only, not acceptance proof |

Final source tests contain no Modal/runner import or cloud calls. Their CLI
outputs are explicit synthetic local doubles, not fabricated provider receipts.
No failing test was represented as passing. Historical source proof of CPU imports
was reused, not relabelled as a fresh runtime check.

## Limits / skipped work / next

**This child is DONE only for source/local acceptance.** No model/runtime/GPU,
actual remote stop, provider timing or paid readiness verified. Parent death,
OS/filesystem stalls, network partitions and provider lag can still leave remote
state unknown. An event-loop block before ID publication cannot be repaired by
guessing an app name: operator reconciliation is required. Conservative90s
admission can reject a healthy slow job. Child result files alone are not success;
require matching independent parent receipt/exit0 and ordinary output checks.

README documents exact future admission prerequisites: existing standing owner
permission within scope (no redundant per-job consent), actual headroom/no paid
overage and reservation reconciliation, approved licensed inputs, same-environment
Modal1.6.3/Python3.11 CLI/auth availability and JSON semantics, writable receipts,
full1200s session allowance plus reporting, and a human incident-recovery path.
Controller should review/integrate the source; **this run authorizes no paid
attempt or CPU reinstall**. Do not execute the future procedure from this receipt.

Skipped: browser/service/API/RPC work, runner/cloud imports, all jobs and installs,
model/media/download/upload, CPU reinstall, new reservations, secrets/env values,
fanout, quota polling, auth/provider/policy changes and Git/control integration.
No actual blocker or new owner question. **$2.85 retained /$30 authority unchanged**;
exact billing unknown. GateR NOT_RUN, S05c locked; physical/calibration/S12 holds remain.

Communication: only mandatory Ponytail announcement; no optional status narration.
Evidence on disk, no duplicated chat report. One authorized terminal status/absolute
REPORT pointer callback to controller01a182c4-9378-7da0-9fbc-99a5a379380c.
Run PLAN/REPORT/TIMEBOX are ignored by existing rules; integrator must preserve/force-add
only these exact owned paths if accepting. No ignore-rule changes made.
