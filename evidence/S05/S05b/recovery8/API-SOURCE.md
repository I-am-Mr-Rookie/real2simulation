# Installed Modal1.6.3 source — read directly, no package import/RPC

Root: `C:/Users/HP/AppData/Local/uv/cache/archive-v0/fLq5XQNkIwPHWdoT/Lib/site-packages/`.
METADATA1–8 identifies Modal1.6.3. Default test Python lacks Modal; nothing installed.
Canonical other-vendor `evidence/S05/guard-review/FINDINGS.md` read directly;
old source `git show cd42ebc:Build/reconstruction/spike/rm02_deadline.py` inspected.
The concrete P2 late-stop and noncooperative-wait findings drive this fix.

## Exact supported future CLI semantics

- `modal/cli/app.py:55–94`: identifier matching `^ap-[a-zA-Z0-9]{22}$` uses exact
  AppGetLifecycle; anything else becomes deployment-name lookup. New parent uses
  that exact regex, never name/account guessing or app-list discovery.
- `modal/cli/app.py:365–408`: `app stop ID --yes` avoids confirmation and issues
  AppStop(source=CLI), awaited before exit. An already-stopped app raises
  SystemExit(message), i.e. nonzero without another AppStop RPC. Exit0 is ack;
  nonzero is not proof of either failure to stop or successful dispatch.
- `modal/cli/utils.py:227–229`: `--yes` is an installed supported flag.
- `modal/cli/app.py:411–479`: `app info ID --json` freshly calls AppGetInfo and
  outputs `app_id`, `lifecycle.state` (APP_STATE_STOPPED maps to `stopped` at48).
- `modal/cli/container.py:41–80`: `container list --app-id ID --json` sends
  TaskListRequest with exact app_id; returns rows for active containers.
- `modal/cli/utils.py:172–194`: table JSON is a list of snake_case-keyed objects;
  zero active containers is exactly `[]`, not missing output or a success code alone.
- `modal/runner.py:419–432`: creates app then enters `_set_local_app` before
  function/image loading. The cooperative ID publisher can observe app_id during
  setup. A lost creation response or blocked loop can still lose publication:
  durable incident, no guessed stop target, no readiness/success claim.
- `modal/app.py:1625–1644`: same-client stop terminates containers/sandboxes and
  prevents new inputs; awaits AppStop. `1682–1711` supports fresh info(refresh=True).
- `modal/_functions.py:2405–2426`: get(timeout=...) is explicitly not cancellation
  safe. Async timeout alone cannot enforce wallclock; the process parent does not
  rely on event-loop cancellation. Same-client refreshed stats are not independent
  confirmation; the parent uses new CLI processes after child exit/kill.

## SHA256 of directly inspected local source

| File | SHA256 |
| --- | --- |
| modal/cli/app.py | 499EF3F1A8D0FD1274D2900415663593CAC1C39B12D54C05AABA60A0A549B62A |
| modal/cli/container.py | BB2451D3C9307DE2F0688B658F18D960EE7D2801006005AAE9393D6641BF5E38 |
| modal/cli/utils.py | D6D9032EAB55A98BE3E312E845A3AE3BF725F162713E91D09C87538394B6B630 |
| modal/app.py | 12339BAF9710796915A973BFF2BBB704EF9DB98849F52298D563C02DC0F4CE9F |
| modal/runner.py | 5B77F2E6E0BD9DF93BB783AFB89A52A3415349917AEB7E07EE9A77F1FEC7631A |
| modal/_functions.py | FB219D68391BD883CA0EEE135A5F771E9896114D90BF76C11AB4A49448E21372 |
| modal-1.6.3.dist-info/METADATA | 3FF41159714509006F8F5F591BBEAE80EB94F85235361EDF439DFF755DB24364 |

These establish source shapes only. All CLI outcomes in tests are explicit local
doubles. No Modal import, RPC, runner execution, job, install, model/media transfer,
paid reservation or runtime/remote-stop verification occurred. Remote NOT_VERIFIED.
