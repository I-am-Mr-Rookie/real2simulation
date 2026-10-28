# S05b-swarm12 — DONE (local F4 lifecycle distinction only)

Implemented the smallest safe F4 distinction. The child now emits an atomic per-attempt lifecycle phase receipt bound to a random token and child PID. A valid `preflight_failed` receipt is classified as local validation failure with `no_remote_creation_confirmed`; it never claims remote stop and never invokes cleanup. Missing, malformed, stale/replaced, or non-preflight receipts remain conservative unknown-remote-state incidents. Existing exact-ID stop/independent verification, deadline, payload, optimization-safe validation and fail-closed protections are retained.

## Changed paths
- `Build/reconstruction/spike/rm02_watchdog.py`
- `Build/reconstruction/spike/modal_rm02.py`
- `Build/reconstruction/spike/test_rm02_watchdog.py`
- `Build/reconstruction/spike/README.md`
- `evidence/S05/S05b/swarm12/`
- `Run-System/Runs/S05b-swarm12/{HANDOUT.txt,TIMEBOX.json,REPORT.md}`

## Fresh checks
- Focused lifecycle tests: normal 3/3 PASS; optimized 2/2 PASS.
- Modal runner tests: normal 9/9 PASS; optimized 9/9 PASS.
- `git diff --check`: PASS.
- No live provider import, remote call, paid job, credential access, model/checkpoint download, deployment, or publication.

## Ponytail full/default applied
Reused the existing atomic JSON receipt, child environment, exact-ID verifier and synthetic subprocess seams. Added no dependency, framework, generic abstraction, broad listing, ID guessing, or remote behavior. Documentation and tests cover the new trust boundary. Skipped full watchdog suite because its long-running Windows timing doubles were unstable and left child processes/locks during this window; the new focused and modal normal/optimized suites are green. This limitation means the complete regression suite remains not fully verified.

Parent S05b remains PARTIAL; this does not establish paid readiness, Gate R, reconstruction, calibration, physical success, or remote lifecycle success.

## Correction / final verification addendum (written after work stop; no product changes)

Work stopped at the last verification/timebox commit: **2026-10-28T17:28:09Z / 23:28:09+06:00**, before the hard deadline **2026-10-28T17:31:12Z**. This addendum preserves the original report above; it does not replace Owns, skills, timing, limitations, or earlier evidence.

Safety correction: preflight success is accepted only with exact version/token/PID types, mutually exclusive phase history, `preflight_failed`, nonzero child exit, no watchdog/kill ambiguity, no app/call evidence, and no other errors. Contradictory `worker.json` app ID, zero exit, phase-write loss, malformed/wrong-type/replaced receipts, and PID/token mismatch remain incident paths. `errors` is never blindly cleared. `modal_rm02.py` records `remote_creation_started` immediately before `modal.enable_output`; preflight evidence does not cover later creation.

Fresh complete results: watchdog source suite **54/54 normal PASS, exit 0** and **54/54 optimized PASS, exit 0**; Modal suite **9/9 normal PASS, exit 0** and **9/9 optimized PASS, exit 0**. Earlier failures were reproduced as Windows timing/process-lock failures from the 3.5-second test seam; only the test seam default was increased to 8 seconds, with production constants unchanged. No live/paid admission occurred. Claude review failed `ECONNREFUSED`; independent-review hold remains.
