# Read-only installed API evidence — LOCAL-ONLY

Source root:
`C:/Users/HP/AppData/Local/uv/cache/archive-v0/fLq5XQNkIwPHWdoT/Lib/site-packages/`.
`modal-1.6.3.dist-info/METADATA` lines1–8 identifies version1.6.3. Files read
as text only; no Modal package or runner was imported and no RPC was executed.

| Installed source | Used semantics |
| --- | --- |
| `modal/app.py:434–497,1714` | Async context-managed `App.run`; public synchronized App wrapper. |
| `modal/_utils/async_utils.py:52–58` | Public regular async methods expose `.aio`. |
| `modal/_functions.py:2221–2251` | One `spawn` enqueues asynchronously and returns a FunctionCall handle. |
| `modal/_functions.py:2405–2426` | `get(timeout=...)` bounds result polling; defaults indefinite; coroutine is explicitly **not cancellation-safe**. App stop remains mandatory. |
| `modal/_functions.py:2256–2272` | `get_current_stats` snapshots running inputs, runner/container count and backlog; SDK's own retry duration is bounded by the outer caller deadline. |
| `modal/app.py:1625–1648` | App stop requests termination and prevention of new inputs; acknowledgement alone is not independent verification. |
| `modal/app.py:1673–1711` | `info(refresh=True)` fetches current metadata rather than cached lifecycle. |
| `modal/types.py:1075–1123,1128–1145` | String enum state `stopped`, refreshed app lifecycle; stats fields at189–195. |
| `modal/_functions.py:2464–2484` | Call graph is best-effort/delayed; deliberately NOT used as a critical admission/stop oracle. |
| `modal/runner.py:371–540` | Setup and teardown do async network operations; context teardown itself must consume caller time. |

The default Python3.14 environment has no installed Modal distribution
(`importlib.metadata.PackageNotFoundError`); the existing uv cached distribution
above was located from diagnostic6's already-saved source pointer, without any
install or cloud import. Standard-library tests run with that default Python.

## Limits

Source-supported API shapes are not runtime/provider proof. Running-input polling
can miss a fast job; completed results are accepted, otherwise ambiguity fails
closed. The fixed150s admission cutoff conservatively reserves the full90s+900s
after setup/enqueue; no scheduler-cause inference. There is one app/one input,
not another scheduling framework. asyncio relies on cancellation cooperation and
OS/event-loop dispatch: timeouts are not hard real-time guarantees. No claim of
guaranteed remote stop, current rates, exact billing, model output or physical success.

Remote stop/runtime: NOT_VERIFIED. Parent S05b: PARTIAL. No new paid run authorized.
