# N67-orch311
Status: DONE. N66 requested spend fixes applied to merged N63 code.
Base: main `df47d2de`; branch `run/N67-orch311`.
| Finding | Result | Regression test |
|---|---|---|
| P2-1 | FIXED: 3 rebuild attempts per owner/Dhaka day, shared LOCK, persistent count, legacy attempts preserved | `test_shell_rebuild_limit_is_three_per_owner_across_two_rooms`; `test_shell_rebuild_limit_counts_failures_and_resets_next_dhaka_day` |
| P2-2 | FIXED: 75 s L4 budget; confirmed termination removes idle; unconfirmed retains full bound | `test_healthy_l4_cold_start_has_time_to_finish`; `test_confirmed_room_cancel_settles_capped_wall_without_idle`; `test_unconfirmed_cancel_does_not_retry_or_release_reserved_headroom` |
| P2-3a | FIXED: stale queued SF3D item never spawns, settles zero | `test_replaced_queued_batch_never_spawns_and_settles_zero` |
| P2-3b | FIXED: persist both call IDs before get; restart/reaper best-effort cancel, full reservation retained | `test_spawn_id_persisted_before_wait`; `test_room_spawn_id_persisted_before_wait`; `test_restart_cancels_saved_shape_call_without_releasing_reservation`; `test_reaper_cancels_saved_call_and_keeps_full_reservation` |
| P3-1 | FIXED: successful room settle capped at estimate | `test_successful_reconstruction_settlement_cannot_exceed_estimate` |
| P3-2 | FIXED: failed same-process rebuild reports shell rebuild | `test_failed_rebuild_reports_shell_rebuild_not_server_restart` |
| P3-4 | FIXED: abort negative tests use timeout_s=1 | `test_replaced_batch_cancels_inflight_call_and_retains_bound`; `test_replaced_batch_unconfirmed_cancel_retains_full_estimate` |
Python 3.12.12, repository-pinned dependencies: requested four pytest targets PASS, 174 tests, 2 subtests (11 warnings).
Node API-storage proxy tests: PASS, 3 tests. git diff --check: PASS.
Regression mutation checks: PASS, 15/15 reverted fixes detected; abort-loop mutant failed in 3.672 s including runner startup.
Tradeoff: allow up to 30 s more L4 wait before retry, avoiding cancellation of the synthetic healthy 60 s cold start.
Paid jobs/API calls: 0; cost: $0. No deploys, pushes, purchases or submissions.
Skipped: live GPU/cancellation, provider bills, browser/UI, web build (no web changes), deployment/replica checks.
Risks: one API process required; reservation-day accounting unchanged; cancellation best effort; spawn-to-persist crash window remains conservatively booked.
Evidence: `evidence/N67/NOTES.md`, `environment.json`, `tests.log`, `node-tests.log`, `mutations.json`.
