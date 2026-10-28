# Exact stopped-app inspection

One authenticated read-only service inspection; no follow, app start, job or retry.
UTC start 2026-10-28T13:19:30.469935Z; end 13:19:34.285074Z; exit 0.
Local subprocess timeout 60s; did not expire. Installed Modal metadata: 1.6.3.

Normal cached-client command (canonical .env consumed by uv; no values read,
printed, copied or injected into remote work):

```powershell
uv run --offline --no-project --no-sync --env-file C:/Users/HP/DOCUME~1/HACKAT~1/2026-1~1/.env -- C:/Users/HP/AppData/Local/uv/cache/archive-v0/fLq5XQNkIwPHWdoT/Scripts/python.exe -B -m modal app logs ap-7TvkSZJ4Wk6Ym0t0yZ3lsM --since 2026-10-28T12:41:00+00:00 --until 2026-10-28T12:52:00+00:00 --source system --tail 30 --timestamps --show-function-id --show-function-call-id --show-container-id
```

Actual complete bounded stdout:

```text
2026-10-28 18:51:08+06:00 Stopping app - user stopped from CLI.
2026-10-28 18:51:10+06:00 Stopping app - user stopped from SDK.
```

Actual stderr:

```text
warning: `--no-sync` has no effect when used alongside `--no-project`
```

This is normal read-only log retrieval, NOT paid compute. No dependency install
or sync was requested; offline cached executable reused. Help was checked locally
before this single inspection. No private API, direct RPC or alternate surface.

The stop events correspond to 12:51:08Z and 12:51:10Z. No function/call/container
IDs, scheduling reason, enqueue timestamp, allocation event or startup event were
returned. This is **only system-source logs**, not all logs or an account resource
inventory; 30-entry cap did not truncate the two returned lines. Absence is not
proof that no worker ever existed, no billing occurred, or no other telemetry is
available to Modal. Historical app/container snapshots are reused, not refreshed.

Owner's later in-turn update restricts any remaining service inspection to the
signed-in ChatGPT in-app browser only. This CLI inspection preceded that update;
no further service inspection occurred afterward. No Chrome or HF access used.
