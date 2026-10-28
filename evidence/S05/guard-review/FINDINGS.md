# R-S05guard findings — rm02_deadline.py @ cd42ebc (local-only review)

Reviewed: Build/reconstruction/spike/rm02_deadline.py (1-135), modal_rm02.py (1-142),
evidence/S05/S05b/recovery7/API-SOURCE.md (SDK notes). Installed Modal not importable by
reviewer's Python 3.14.5 (ModuleNotFoundError); SDK text taken from API-SOURCE.md citations only.

## Bounded? Verdict on acceptance 1
Caller budget is bounded ONLY under cooperative cancellation. Not a hard wall-clock bound.
- Repro (wait_for_noncooperative.py, 10s parent kill): wait_for(timeout=0.2) on a coroutine
  that swallows CancelledError -> ran 2.23s and RETURNED 'late' (no TimeoutError) on Py3.14.5.
  Line 35 post-check converts this to TimeoutError (good), but elapsed time is unbounded.
- SDK note: FunctionCall.get coroutine not cancellation-safe (_functions.py:2405-2426 per
  API-SOURCE). Cancelling get at work_end (line 68-69) may discard a late paid result; stop
  still follows, so resource-safe, result-lossy. Acceptable.
- Unknown app id (enter cancelled before app_id): line 112-114 -> incident. Fail-closed. OK.
- Delayed stats: admission loop times out at admission_end (started+150s) -> stop path; late
  stats in verification -> incident. Fail-closed. OK (may abort a container that was starting).
- result/stop/context failures: each collected into errors -> ResourceIncident. OK.
- Evidence-write failure: emit() swallows, stop still attempted, OSError only after confirmed
  stop (line 134). OK. deadline.json write is non-atomic (modal_rm02.py:128) - P3.
- Remote side: function timeout=900, startup_timeout=90, retries=0, max_containers=1 bound
  per-input execution only; queue wait / ephemeral-app lifetime after client death rely on
  client stop / SDK heartbeat - NOT_VERIFIED.

## P2-1 Stop can be skipped entirely after a late overshoot - rm02_deadline.py:96
`before(min(end - EXIT_SECONDS, clock() + STOP_SECONDS), app.stop.aio)`: if any earlier
non-cooperative await (see repro) pushes clock() past end-10, before() raises TimeoutError at
line 33 WITHOUT calling app.stop. Receipt still says stop_requested=True (line 93) though no
request was sent. Fail-closed incident is raised, but the one action that limits spend is
skipped exactly when time overran. Same for verification loop line 102 (P3: no check attempted).
Smallest fix: give stop a floor independent of the exhausted total budget, e.g.
`await before(clock() + STOP_SECONDS, app.stop.aio)` (stop attempt beats strict caller budget),
and set stop_requested only after the call is issued. Test: fake clock already past end with a
recording app.stop -> assert stop called once.

## P2-2 No independent wall-clock enforcement - modal_rm02.py:131
asyncio.run(guarded_probe(...)) has no outer process watchdog. A hung SDK await that ignores
cancellation (or a blocked event loop) is unbounded locally; timers are intent, not enforcement.
Smallest fix (source lane): launch main under a parent with a hard kill at TOTAL_SECONDS+margin
(e.g. subprocess.run(..., timeout=...) wrapper or documented operator command), and require an
out-of-band post-run app-state check (modal app list / app stop by name) in the run procedure
whenever ResourceIncident or the watchdog fires. No new framework.

## P3
- stop_requested set before request (line 93) - misleading receipt.
- Line 119 awaiting cancelled result_task with an exhausted deadline returns immediately,
  leaving a pending task (warning only).

## Verdict (acceptance 3)
- Safe for LOCAL-ONLY progress: yes (no remote calls happen without an explicit operator run).
- Paid-admission readiness: NOT READY until P2-1 fixed + unit check, and P2-2 outer watchdog
  plus out-of-band post-run stop/app-state check exist. Live remote stop remains NOT_VERIFIED
  until first bounded paid run's receipt shows remote_stop_confirmed with an independent check.
- No Gate R / physics / S12 / R-S05 row claim.
