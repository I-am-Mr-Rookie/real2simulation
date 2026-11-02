# N66-orch310: cross-vendor spend review of N63 (run/N63-orch309, commit 79098785)

Reviewer: Claude Opus (read-only). Scope: `git diff main...run/N63-orch309`, evidence/N62/REVIEW.md, Build/guardrails/daily_cap.py,
Build/api/gpu (queue, reaper). No product code changed, no paid calls, no deploy. Line numbers are on run/N63-orch309.

## Verdict: ACCEPT WITH FIXES

No P0 or P1. Every paid path still reserves on the canonical ledger before spending, settles at or below its reservation
(one P3 edge), and never double charges or releases early. All N62 code fixes are present and each has a test that fails
without it (mutation table below). Three P2s remain: per-room rebuild limit does not stop one user draining the global cap,
the 45 s L4 budget is about the healthy cold start and roughly doubles recorded room cost, and stale or orphaned Modal calls
are not stopped before spawn or after a restart.

## Checks (1) to (6)

| # | Check | Result |
|---|---|---|
| 1 | N62 findings closed with failing-without-fix tests | P1-a CLOSED (main sf3d.py:23 IDLE_S 900, ESTIMATE 1620 s A10G; ledger is conservative whether Modal runs 60 or 900 s idle). P2-a CLOSED (abort poll + cancel, sf3d.py:112-132; early invalidation objects.py:33). P2-b CLOSED as specified (fail_interrupted, shape_upgrade.py:33-42; no auto-resume). P2-c PARTIAL (PNG cleanup shape_upgrade.py:23-26 done; rebuild limit is per room, see P2-1). P3-d CLOSED (generic cancel, sf3d.py:124-132). P3-e bound CLOSED (live_room.py:275); day-boundary part unchanged (P3-3). P3-a/b/c unchanged by design. |
| 2 | Reserve before spend | PASS. SF3D reserves at sf3d.py:100 before enqueue (104), queue start (105) and spawn (110). Room attempts reserve per device before enqueue (live_room.py:252-253, 258). SAM text calls reserve per image in object_lift.sam_text (unchanged; SAM_THREADS 4 -> 8 at room_shell.py:22 is safe because reserve is BEGIN IMMEDIATE, daily_cap.py:66). No unreserved path found. |
| 3 | Cap holds under concurrency | PASS for the ledger. Reserve serializes; unsettled rows count at reservation (daily_cap.py:52-54). SF3D settle max min(wall,600)+900 = 1500 s < 1620 s reserved. Room L4 failure settle min(wall,540)+900 = 1440 s = its L4 reservation; A10G retry reserves its own A10G worst case before spawn, after the L4 cancel is confirmed (CancellationUnconfirmed is not retried, live_room.py:225, 231-236). Concurrent rebuilds of one room each reserve; the loser's thread aborts within 10 s. Edge: P3-1. |
| 4 | No double charge, no early release | PASS. Late settle after reap: ValueError -> RuntimeError(REASON) (sf3d.py:141-144) or ignored (live_room.py:280-281). Abort, timeout, remote error, unconfirmed cancel and ambiguous spawn all keep ESTIMATE_USD (sf3d.py:137). Reaper keeps full reservation for started jobs (api/gpu/__init__.py:104-111). |
| 5 | Cancel and restart stop paid work | PARTIAL. Rebuild aborts the in-flight call within one 10 s poll and terminates containers (tested). Gaps: a stale item waiting in the shared GPU queue still spawns after invalidation (P2-3); restart reports pending items as failed but the orphaned SF3D or room call is never cancelled (P2-3). Both stay inside their reservations. |
| 6 | evidence/N63/live-result.json cost | MATCHES. 182 rows, all settled, none above reservation. Sum of actual = 2.42457689 = spend_delta_upper_usd = row_spend_upper_usd. Modal: L4 failed attempt 0.27051534 = cost(953.459 s, L4) = min(wall 53.459 s, 540)+900 (status wall_s 53.48 is read just after settle); A10G 0.34729192 = cost(44.447 round trip +900 s, A10G) (scene_log upper_bound); 4 SF3D rows 0.36621455, 0.33351652, 0.33387836, 0.3331602 each equal cost(min(wall_s,600)+900, A10G) exactly. Meta: 176 x 0.0025 = 0.44 (16 keyframes x 11 prompts). Reservations: L4 0.4085568, A10G 0.5295168, SF3D 0.5957064 match cost(1440/1440/1620 s). |

Tests: N63 tree, Python 3.14: `pytest tests/gpu/test_sf3d.py tests/reconstruction/test_shape_upgrade.py tests/reconstruction/test_live_room.py
tests/reconstruction/test_semantic_shell.py tests/gpu/test_room_gpu.py` -> 78 passed.

Mutation check (fix removed in a scratch copy of N63 code in this worktree, then restored; not committed):

| Fix removed | Result |
|---|---|
| abort poll (sf3d.py:113) | test_replaced_batch_cancels_inflight_call_and_retains_bound hangs to the 90 s budget then fails (slow, see P3-4) |
| generic cancel (sf3d.py:124) | test_failed_call_settles_once_at_full_bound FAILED |
| fail_interrupted body | test_restart_read_fails_pending_without_resuming[x2], test_dead_local_supervisor_... FAILED |
| PNG unlink (shape_upgrade.py:26) | test_prepare_removes_only_previous_batch_crops FAILED |
| early prepare(d, []) (objects.py:33) | test_shell_rebuild_invalidates_before_detection FAILED |
| rebuild limit (objects.py:154) | test_shell_rebuild_limit_counts_failures_and_resets_next_dhaka_day FAILED |
| room failure bound (live_room.py:275) | test_failed_reconstruction_transport_wait_is_bounded_by_reservation FAILED |

## Findings

### P2
**P2-1. Rebuild limit is 20 per room per day, so one user can still drain the global $10 cap (N62 P2-c not effectively closed).**
- Where: Build/api/room/objects.py:149-156 (counter in the room's status.json, limit MAX_DAILY = 20 from Build/api/storage/files.py:27).
- Scenario: a rebuild records about $1.77 (N63: SAM $0.44 + 4 SF3D about $1.37) and reserves up to $0.44 + 4 x $0.5957 = $2.82.
  Five or six rebuilds of one room (limit 20) use the whole $10 day and every other user gets DAILY_CAP. More rooms multiply the limit.
- Minimal fix: count rebuilds per owner, not per room (e.g. a row in the files store via store.check_daily, or an owner-keyed
  counter under the same LOCK) with a small limit such as 3 per user per day. Keep the existing test, add one for two rooms.

**P2-2. ROOM_START_BUDGET_S = 45 is about a healthy cold start, so L4 is often cancelled and the A10G retry pays again.**
- Where: Build/reconstruction/live_room.py:33, 220, 227 (timeout -> "no GPU capacity" -> retry_on_a10g true).
- Evidence: N63's own successful A10G attempt had a 44.447 s client round trip (cold start 9.8 s + model load 18.3 s +
  inference 3.3 s). The L4 attempt hit 45 s and was cancelled at 53.48 s. Ledger per room: L4 $0.2705 + A10G $0.3473 = $0.6178
  vs about $0.27 for an L4-only success, and $0.94 of reservation headroom. It is a latency for spend trade not recorded as an owner decision.
  It also mislabels a slow healthy L4 as "no GPU capacity".
- Minimal fix: either raise the budget to cover a healthy L4 cold start plus inference (about 75 s), or keep 45 s and, when
  cancel(terminate_containers=True) is confirmed, settle that attempt at cost(min(wall,540), L4) without the 900 s idle (the
  container is terminated). Note the trade in REPORT so Koushik can choose.

**P2-3. Paid work can start or continue after it is no longer wanted.**
- (a) Stale queue item spawns: sf3d.py:105 (jobs.start blocks up to 1800 s, api/gpu/__init__.py:138-169) then spawns at :110 and
  only checks abort at :113. If a rebuild happens while the item waits behind another GPU job, it spawns a new call, cancels it at
  once and records the full $0.5957. Fix: one line before spawn, `if abort and abort(): raise RuntimeError("SF3D cancelled (shell rebuilt)")`
  (spawned is still False, so it settles 0; finish() still runs).
- (b) Restart orphans: fail_interrupted (shape_upgrade.py:33-42) fixes the status only. The in-flight SF3D call (up to 600 s + 900 s
  idle) and an in-flight room reconstruct keep running on Modal; the reaper books their full reservations, so the cap holds, but
  the calls are not stopped. Fix: store `handle.object_id` in the gpu_jobs row (or shape-upgrades.json) right after spawn; in
  fail_interrupted and in _reap, best-effort `modal.FunctionCall.from_id(id).cancel(terminate_containers=True)`.

### P3
- **P3-1. Successful room settle can exceed its reservation by seconds.** live_room.py:263, 274 settle scene_log upper_bound =
  client round trip + 900 s, where the round trip includes from_name and spawn before the 540 s get timeout (:220). Worst case is a
  few seconds above the 1440 s reservation, recorded without a cap check. Fix: `min(log upper total, estimate)` at :274.
- **P3-2. Wrong reason after a failed rebuild.** objects.py:33 writes an empty batch before detection; if detection then fails
  (e.g. CapExceeded), the old thread's finally starts the empty batch and fail_interrupted marks the old pending shapes
  "SF3D interrupted (server restart)" though nothing restarted. Fix: pass the reason ("shell rebuild" when work.process == _PROCESS).
- **P3-3. Day boundary unchanged** (N62 P3-e): spend books on the reservation day; matters Nov 4 -> 5 and Nov 8 -> 9 ($10/$20).
  LOCK, _running and the rebuild counter are per process; safe only with one uvicorn worker.
- **P3-4. Slow negative test.** test_sf3d.py:107-113 uses the default 90 s budget, so without the abort fix it hangs 90 s before
  failing. Fix: pass timeout_s=1 or a fake monotonic clock.
- **P3-5. Abort settles at the full estimate** even when cancel is confirmed (sf3d.py:137). Conservative; uses cap headroom only.

## Not checked
Live Modal deployment (scaledown_window, terminate behaviour), provider bills vs ledger, Railway replica count, a real
restart, web UI. Findings come from reading code, the N63 evidence file and local tests; no paid jobs were run.

