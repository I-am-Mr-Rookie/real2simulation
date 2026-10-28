# R-S05guard-native — F3/F4 lifecycle guard review (read-only, other-vendor)

Reviewer: native Claude inside Codex (Anthropic; exact model ID not observable). Base `f409018`, branch `run/R-S05guard-native`. Source unchanged.
Scope: `Build/reconstruction/spike/{modal_rm02.py,rm02_watchdog.py,rm02_deadline.py}` + tests + `Run-System/Runs/S05b-swarm12/REPORT.md`.

## Verdict
Guards are fail-closed on every path checked EXCEPT finding A (narrow false no-remote classification). Finding B makes real Windows-venv runs always report an incident (safe direction, but blocks clean classification). Not live-job readiness; no headroom/gate claim.

## Findings
**A [P2, F3] Preflight classification ignores present-but-malformed `worker.json`.** `rm02_watchdog.py:108-116`: when `preflight_candidate`, any `worker.json` parse/ID-format failure is swallowed; `:171-173` then classifies `no_remote_creation_confirmed=True, resource_incident=False`. Reproduced with existing doubles (`probe_preflight_contradiction.py`): `worker.json` present with `app_id` `"not-an-app-id"` or `""` + valid `preflight_failed` receipt -> `preflight_validation_failed: true, resource_incident: false, errors: []`. Any worker.json is app/call evidence contradicting preflight_failed. The `"function_call_id" not in state` term is dead (state never gets that key) and gives false assurance. Production reachability is low (child only writes worker.json inside guarded_probe after the `remote_creation_started` phase replace), but the stated contract ("no app/call evidence") is not enforced.
Smallest fix: replace `and "function_call_id" not in state` with `and not worker_path.exists()` (lexists if symlinks matter); add a test for malformed/empty ID with preflight_failed -> ResourceIncident.

**B [P2, F3/F4 operability] PID equality fails under a Windows venv redirector.** `:86` requires receipt `pid == child.pid`. Measured (Python 3.11 venv, Windows): Popen PID 33728 vs child `os.getpid()` 28572 (`sys.executable != sys._base_executable`). Result: `phase_invalid` -> `resource_incident=True` on EVERY run, including confirmed-stop successes and real preflight failures. Safe direction, not a false clear. Fix options: drop PID equality (fresh dir + random per-attempt token already bind the receipt), or require a non-redirector interpreter and assert it before launch. Launcher kill DOES terminate the grandchild (measured; job object) — no orphan client.

**C [P3, F3] Kill-in-finally not tracked.** If `child.wait` raises OSError, `child_returncode` stays absent (`.get` -> None != 0 passes) and the `finally` kill does not set `watchdog_fired`. A valid preflight_failed receipt then still classifies no-remote. Practically harmless (child already past last phase write), but contradicts swarm12's "no kill ambiguity" claim. Fix: require `isinstance(child_returncode, int)` and record a kill flag.

## Confirmed OK (by reading + tests)
- Missing remote ID: absent/invalid `worker.json` without valid preflight receipt -> `app_id:unknown_remote_state` -> incident. guarded_probe: no ID after attempted setup -> `setup:unknown_remote_state`.
- Exact-ID stop: regex `ap-[a-zA-Z0-9]{22}`, `app stop <id> --yes`; independent fresh `app info --json` + `container list --app-id` runs even after stop failure; loop bounded by original reserve, never extended; nonzero/garbled output fails closed (no retry).
- Queue+execution bound: budget validated before `app.run`; spawn and running-input admission must occur by `end-90-900-60`; result wait to `end-60`; Modal `timeout=900, startup_timeout=90, retries=0, max_containers=1`; parent kills child at `deadline-reserve`; child deadline = that -10s. Queued-but-not-running past admission -> TimeoutError -> stop.
- No false clearing: `resource_incident=False` only via independent stop confirmation or preflight path (A, C are the exceptions). Errors never cleared; cleanup-with-errors still raises.
- No hidden launch: `modal_rm02.py` refuses direct run without watchdog env; module-level Modal objects are local definitions; `remote_creation_started` written before `modal.enable_output`/`app.run`; phase-write failure leaves conservative state.

## Unverified
Modal CLI JSON schemas (`app_id`, `lifecycle.state`, container list shape) for SDK 1.6.3 — schema drift fails closed (false incident), not verified here. Cross-process `time.monotonic` comparability assumed (QPC system-wide on Windows).

