# R-S05guard2 findings — local stop guard @ e46f23c (direct source review)

Reviewer: CLAUDE lane, independent (other-vendor vs Sol source lane). Local only: no Modal import,
RPC, network, install, runner, job or paid call. Installed SDK read as TEXT at
`C:/Users/HP/AppData/Local/uv/cache/archive-v0/fLq5XQNkIwPHWdoT/Lib/site-packages/`
(venv pyvenv.cfg: CPython **3.11.15**). SHA256 of all 7 API-SOURCE files re-hashed: all MATCH recovery8.

## Acc1 — SDK text vs implementation (VERIFIED from source text)
- ID regex: `modal/cli/app.py:73` `re.match(r"^ap-[a-zA-Z0-9]{22}$")`; watchdog `rm02_watchdog.py:75`
  `re.fullmatch` is equal-or-stricter (rejects trailing \n that SDK `$` would accept). Non-match never
  reaches CLI -> no name lookup (`app.py:85` path unreachable). OK.
- `app stop ID --yes`: `app.py:365-408`; `--yes` = `cli/utils.py:227-229`; skips TaskList/confirm
  (390-406), sends AppStop (407-408). Already-stopped: `SystemExit(msg)` (381-388) -> exit 1, no RPC.
  NotFound/transport -> `__main__.py` prints error, exit 1. Watchdog treats only 0 as ack (105-107),
  nonzero not as error. Correct and honest.
- `app info ID --json`: `app.py:435-479`, keys `app_id`, `lifecycle.state` = `state.plain`; STOPPED ->
  "stopped" (48), STOPPING -> "stopping..." (49). Output enabled by `modal/__main__.py` `enable_output()`;
  rich `print_json` (`_output/rich.py:358-362`), non-tty -> plain JSON. OK.
- `container list --app-id ID --json`: `cli/container.py:42-78` -> `display_table` (`cli/utils.py:189-192`)
  -> `[]` for zero tasks. Note TaskListRequest also carries profile `environment_name` (container.py:55-57).
- SDK retries: stubs default `DEFAULT_MAX_RETRIES=3` without total timeout (`_utils/grpc_utils.py:207,504-507`);
  each CLI process is bounded only by watchdog `process.wait(timeout)`+kill (`rm02_watchdog.py:96-100`). OK.
- Process semantics: `python -m modal` valid (`modal/__main__.py` present). Kill of CLI after send leaves
  dispatch unknown; code keeps `stop_dispatched: NOT_VERIFIED` (36). Honest.
- App ID visibility: `runner.py:420-430` AppCreate (`_init_local_app_new`) precedes `_set_local_app`; a kill
  between them loses the ID -> incident (watchdog 78-79). Correct fail-closed; documented.

## Acc2 — prior P2s
- **P2-1 (late overshoot skipped stop): FIXED.** `rm02_deadline.py:103,113` stop deadline =
  `clock()+STOP_SECONDS` at cleanup entry, independent of exhausted total; `stop_requested` set inside
  `stop()` (108) and `stop_dispatched/acknowledged` only after await (111). Covered by
  `test_already_expired_clock_still_invokes_stop`.
- **P2-2 (no independent wallclock): FIXED locally.** `rm02_watchdog.py:52-61` OS child + wait timeout + kill;
  fresh CLI processes for stop/info/containers (83-121); direct run refused (`modal_rm02.py:11-12`).
  Kill != remote stop: receipt keeps `independent_stop_confirmed` separate; covered by noncooperative test.
- Other paths checked OK: stale dir (31 `exist_ok=False`); missing/malformed/wrong-type ID (73-79);
  preflight-evidence failure before launch (39); later evidence failure still stops (41-45);
  reserve exhaustion never fakes attempt (84-86); kill-wait timeout handled (60,62,65-70);
  nonzero stop still verified (110-123); wrong id/state/containers/bad JSON -> incident (116-123).
  Reserve arithmetic: 2+1+20+15+15=53s < 60s reserve.

## Actionable findings (none P0/P1; no remote-safety hole found in scope)

**F1 P2 (operability; fail-closed) — single-shot independent verification.** `rm02_watchdog.py:111-121`
calls info+containers exactly once immediately after `app stop`. SDK has transient
`APP_STATE_STOPPING` -> "stopping..." (`modal/cli/app.py:49`), and the child lane itself polls because state
lags (`rm02_deadline.py:117-125`). Repro `watchdog_single_shot_repro.py` (local CLI double): first info
"stopping...", later "stopped" -> **ResourceIncident after 1 info call with ~4.5 of 5 s reserve unused**.
Impact: on the watchdog-fired/kill path (where it matters most) a real stop will likely be reported as an
incident, forcing manual investigation; never unsafe. Remedy (minimal): loop info+containers with
`time.sleep(1)` while `invoke` still has reserve (it already raises TimeoutError at exhaustion), confirm
on first full match; add one test with transient "stopping...".

**F2 P2 (verification gap) — suite fails on the actual Modal interpreter.** Controller "spike 42 PASS" ran on
Py3.14.5 (QPC clock). Target venv is CPython 3.11.15 with Windows `GetTickCount64` 15.6 ms monotonic.
`test_rm02_deadline` fails **5/5 runs on 3.11** (3 errors: `test_app_id_published_before_noncooperative_setup_finishes`,
`test_real_local_timer_bounds_hanging_get`, `test_slow_cancellation_overshoot_preserves_timeout_and_stops`),
3.14 5/5 OK (`py311-rerun.txt`). Root cause (repro `py311_timer_repro.py` + `-X dev` outputs): 10-80 ms real
timers with asyncio debug (IsolatedAsyncioTestCase) on a 15.6 ms tick -> cleanup verification TimeoutError;
×10 scaled constants pass on 3.11. Production budgets are seconds, so this is a test-timing defect, not a
source defect — but the guard is unverified on its runtime interpreter. Remedy: scale those three tests'
patched constants ≥10× (or fake clock) and add the venv-3.11 run to checks.

**F3 P3 — child budget clock skew / late-result loss.** Parent clock starts before Popen
(`rm02_watchdog.py:28,48,56`); child budget restarts after imports/frame hashing (`modal_rm02.py:121-131`,
`rm02_deadline.py:22`) and cleanup is relative (`:103`, up to +60 s). Npz/result writes occur after
`asyncio.run` (`modal_rm02.py:141-145`, non-atomic). A result arriving near work_end can be killed mid
cleanup/write -> paid result lost, receipt "Client failed"; parent still stops. Remedy: pass absolute
deadline (or subtract startup latency) and leave a write margin; atomic write of result json.

**F4 P3 — preflight failures indistinguishable from lost app ID.** Assertion failures before
`app.run` (`modal_rm02.py:121-130`) leave no worker.json -> "Independent stop unconfirmed" incident.
Fail-closed but noisy. Remedy: write `{"phase":"before_app_run"}` to the receipt immediately before guarded_probe.

**F5 P3 — CLI subprocess encoding.** `rm02_watchdog.py:92` inherits Windows cp1252 stdout; rich JSON
uses `ensure_ascii=False` (`rich/json.py:31`). Non-ASCII description/error -> UnicodeEncodeError -> false
incident. Current app name ASCII. Remedy: `env=dict(os.environ, PYTHONIOENCODING="utf-8")` for CLI.

**F6 P3 — large result path not ignored.** `git check-ignore` returns nothing for
`evidence/S05/S05b/recovery8/attempt-x/local/a.npz`; up to 256 MiB npz (`modal_rm02.py:101,143`) would be an
untracked repo file. Remedy: ignore `attempt-*/local/` before any run.

**Assumption (not defect):** `containers == []` is only meaningful in the same Modal environment
(container.py:55 uses profile env); both child and CLI inherit one env/profile. Unverified live.

## Verdict
- Local source review: **PASS with findings** — prior P2-1/P2-2 fixed; no fail-open defect found; F1/F2
  should be fixed before the paid probe (operability + target-interpreter verification).
- Live remote stop, provider lifecycle timing, ephemeral-app behavior after client kill (heartbeat,
  `runner.py:63-68,434-440`), headroom/billing, licence, paid readiness: **NOT_VERIFIED**.
- No Gate R, R-S05 parent, physical, or leaf DONE claim.

