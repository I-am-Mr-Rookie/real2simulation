# F1-F6 disposition (local-only)

| Finding | Disposition and exact evidence |
|---|---|
| F1 transient stopping | FIXED locally: existing `invoke` reused inside same-app info+container polling, original deadline/reserve unchanged, 1s maximum polling sleep. `test_transient_state_and_containers_are_polled_on_exact_same_app` covers both lifecycle and container lag and asserts exact commands/ID twice; persistent-running test requires original-bound TimeoutError incident. |
| F2 Windows3.11 timing | FIXED: 19-test baseline errors3 saved in baseline-py311; real timer test constants scaled10x (production unchanged), publication test event-synchronized. Both fresh full spike runs47 PASS; no skips. |
| F3 startup clock skew / lost late result | RETAINED documented fail-closed limit, acceptable for this child only; paid-readiness HOLD. Parent `supervise` starts monotonic before Popen, passes relative `RM02_CHILD_BUDGET`, kills on parent work cutoff, and rejects nonzero/watchdog-fired clients even after confirmed cleanup. Unmodified `modal_rm02.main` hashes frames before guarded_probe and writes NPZ/result metadata afterward non-atomically. `test_late_result_file_cannot_turn_killed_client_into_success` saves synthetic result then blocks; parent kills, independently confirms cleanup, still raises Client failed. Does NOT prove preservation of real results. Absolute child budget/write margin and atomic runner outputs require future separately owned work before paid admission. |
| F4 preflight vs lost-ID ambiguity | RETAINED conservative incident; no inference of no remote work. `test_preflight_failure_without_id_remains_unknown_not_shutdown_success` exits9 before receipt; resource incident, stop not attempted, no CLI calls. Existing lost/malformed-ID tests also remain. Watchdog cannot safely distinguish lost-create response, never guesses/enumerates IDs. Operator reconciliation required; optional runner phase receipts outside Owns. |
| F5 UTF-8 CLI | FIXED at existing subprocess seam with PYTHONIOENCODING=utf-8. `test_cli_json_uses_utf8_even_with_cp1252_parent_environment` inherits cp1252 parent then verifies decoded lambda in CLI JSON. All CLI doubles now emit non-ASCII info JSON. |
| F6 local bytes ignore | FIXED with only `/evidence/S05/S05b/recovery8/attempt-*/local/`. audit.json records `git check-ignore -v` positives for result/partial bytes and negatives for source, input, worker/watchdog/GPU-result receipts and recovery9 evidence. Actual unchanged runner writes under this recovery8 entry point. |

Remote verification, CLI/auth environment, lifecycle timing, headroom/no-paid-overage,
licensed-input admission and physical success NOT_VERIFIED. No Modal import/real
CLI/RPC/network/install/job. Parent S05b PARTIAL; Gate R NOT_RUN, S05c/physical holds
unchanged. $2.85/$30 unchanged. No paid-readiness release.

Scene contract default3.14:11 PASS. Additional unrequired scene suite on bare3.11
cannot import jsonschema (scene-py311.txt); no install or path injection attempted.
This does not affect either complete stdlib-only spike suite's47 PASS.
