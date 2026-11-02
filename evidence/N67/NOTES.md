# N67: N66 spend-review fixes

Scope: N63 code merged on main, base `df47d2de`. Offline tests only. No provider calls, GPU jobs, deploys, purchases or account changes.

## Changes and regression coverage

| Finding | Change | Regression test |
|---|---|---|
| P2-1 | Three rebuild attempts per owner per Dhaka day, across rooms. The existing shape-upgrade LOCK covers check and persistent owner-counter update before detection. Failures consume attempts. On first use, same-day legacy per-room counts are summed, not refunded. | `test_shell_rebuild_limit_is_three_per_owner_across_two_rooms` (fresh and legacy counters); `test_shell_rebuild_limit_counts_failures_and_resets_next_dhaka_day` |
| P2-2 | L4 result budget is 75 s. Only a confirmed terminating cancellation removes the 900 s idle term; settlement uses the requested device rate and at most 540 s wall time. CancellationUnconfirmed retains the full reservation and prevents fallback. | `test_healthy_l4_cold_start_has_time_to_finish`; `test_confirmed_room_cancel_settles_capped_wall_without_idle`; `test_unconfirmed_cancel_does_not_retry_or_release_reserved_headroom` |
| P2-3a | Check abort again immediately before SF3D spawn, after waiting in the shared queue. A stale item settles zero and finishes its queue row. | `test_replaced_queued_batch_never_spawns_and_settles_zero` |
| P2-3b | Persist SF3D and room Modal object IDs in the GPU-job row before waiting. Post-ready shape batches also persist the ID, so fail_interrupted can cancel pending calls. The lease reaper cancels after its DB transaction commits. Cancellation is best effort and never releases an orphan's reservation. A spawn returning after its row was reaped is cancelled too. Completed shapes are not cancelled on reads. | `test_spawn_id_persisted_before_wait`; `test_room_spawn_id_persisted_before_wait`; `test_room_already_ready_reservation_held_until_async_result_and_gpu_activity`; `test_restart_cancels_saved_shape_call_without_releasing_reservation`; `test_reaper_cancels_saved_call_and_keeps_full_reservation`; `test_spawn_after_reap_is_cancelled_without_releasing_reservation`; `test_completed_shape_calls_are_not_cancelled_on_read` |
| P3-1 | Successful room ledger settlement is min(log upper bound, reservation estimate). | `test_successful_reconstruction_settlement_cannot_exceed_estimate` |
| P3-2 | A pending batch belonging to this process reports shell rebuild, not server restart. A batch from another process retains the restart reason. | `test_failed_rebuild_reports_shell_rebuild_not_server_restart`; existing restart-read tests |
| P3-4 | Abort tests explicitly use timeout_s=1. The inflight test now allows the new pre-spawn check before simulating invalidation. | `test_replaced_batch_cancels_inflight_call_and_retains_bound`; `test_replaced_batch_unconfirmed_cancel_retains_full_estimate` |

## Reproduce

```powershell
uv run --python 3.12 --with pytest --with-requirements Build/api/health/requirements-test.txt python -m pytest tests/gpu tests/reconstruction tests/api-storage tests/guardrails/test_daily_cap.py -q --disable-warnings --tb=short
node --test tests/api-storage/proxy_files.test.mjs
```

`environment.json` records Python and package versions. Application/test dependencies use the repository pins in requirements-test.txt and its included requirements.txt; pytest itself has no repository pin and resolved to the recorded version.
`tests.log` and `node-tests.log` contain the final command output. `mutations.json` records 15 deliberately removed/reverted fixes, each caught by its named regression test. Source bytes were restored after each mutation. The abort-loop mutant failed in 3.672 s including pytest startup, rather than waiting the default client budget.

## Tradeoff and limits

- The L4 budget adds up to 30 s before an A10G capacity retry. It allows the synthetic healthy 60 s cold start to finish without cancellation; this is not live GPU performance evidence.
- Cancel-by-ID is best effort, including lookup/transport errors. Restart/reaper cancellations retain the full reservation even when confirmed. SF3D's existing conservative failed/aborted settlement is unchanged.
- The counter and supervisor LOCK still require one API process/worker. Replica count was not checked. Spend still belongs to its reservation day, including the existing day-boundary behavior (N66 P3-3).
- Spawn and local persistence cannot be atomic across Modal and SQLite/files; a crash between them can still leave an unknown call. Started-job reservations remain booked at the full bound on lease expiry.
- No live cancellation, provider bills, deployed configuration, browser/UI, or production behavior was checked. No web code changed, so no web build was run.
