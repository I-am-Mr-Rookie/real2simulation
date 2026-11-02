# N62-orch307: cross-vendor spend review of N59 (run/N59-orch304, commit 9f14195a)

Reviewer: Claude Opus (read-only). Scope: `git diff main...run/N59-orch304`, focus files plus Build/guardrails/daily_cap.py and
Build/api/gpu lease/reaper. No product code edited, no paid calls, no deploy.

## Verdict: ACCEPT WITH FIXES

No P0. The ledger path is sound: every SF3D call reserves the A10G worst case before enqueue/spawn, settles at or below the
reservation, and reaper/late settle cannot release or double charge. The one P1 is caused by N59's Modal deploy running ahead
of main, and merging N59's sf3d.py closes it, so merge soon. Fix the P2s next; none of them can push the ledger over the cap.

## Checks (1) to (6)

| # | Check | Result |
|---|---|---|
| 1 | Reserve before spend | PASS. sf3d.py:100 reserves before enqueue (104) and spawn (110). Background upgrades only call generate_remote (shape_upgrade.py:68). Shell SAM uses object_lift.sam_text, which reserves per image (object_lift.py:80). Reconstruction attempts reserve per device (live_room.py:252-253, unchanged). No unreserved path found. |
| 2 | Cap cannot be exceeded | PASS for the ledger. reserve() is BEGIN IMMEDIATE (daily_cap.py:66), so concurrent upgrades serialize. SF3D settle is always <= reserve: worst settle is min(wall,600)+900 = 1500 s A10G = $0.5516 vs ESTIMATE_USD 1620 s A10G = $0.5957 (computed from cost_log). Rebuild invalidation and restart leave rows reserved or reaped at full. Real provider spend can still differ from the ledger: see P1, and P3-e for the day boundary. |
| 3 | No double charge or early release | PASS. Reaper settles a started job at its full reservation (api/gpu/__init__.py:104-111) and swallows ValueError. A late runner settle gets ValueError and becomes RuntimeError(REASON) (sf3d.py:130-133), so the result is dropped and nothing is charged twice. Timeout, unconfirmed cancel, remote error and ambiguous spawn all keep ESTIMATE_USD (sf3d.py:126). A never-started job settles at 0, which is correct because nothing was spawned. |
| 4 | Cancel and invalidate stop paid work | PARTIAL. Client timeout cancels with terminate_containers=True (sf3d.py:117). A shell rebuild skips the remaining items but does not cancel the call already in flight (P2-a). An API restart orphans the in-flight call (bounded by its reservation) and leaves states pending (P2-b). |
| 5 | Cost bound matches GPU and the 660 s budget | PASS. BACKGROUND_BUDGET_S = 300+300+60 = 660 is enforced (sf3d.py:98). Reserve uses A10G, the dearer GPU. Settle uses the torch device name, with unknown treated as A10G (sf3d.py:87-89). min(wall, STARTUP_S+TIMEOUT_S) caps queue and network waits. The Modal GPU list is ["L4","A10G"] only. |
| 6 | Per-user limits | NOT BYPASSED by N59: upgrades create no uploads, and SF3D runs at most 4 per shell (room_shell.py:25, 492). Pre-existing gaps remain: shell rebuild is unthrottled, and room artifacts are outside the 1 GB quota (P2-c). |

Tests: `pytest tests/reconstruction/test_shape_upgrade.py tests/gpu/test_sf3d.py tests/reconstruction/test_live_room.py` in the N59 worktree:
41 passed (no cache written).

## Findings

### P1
**P1-a. The deployed r2s-sf3d idle window (900 s) is ahead of main's ledger constants (60 s), which under-records DEV clicks now.**
- Where: main Build/gpu/sf3d.py:25 (`IDLE_S = 60`), :29 (ESTIMATE = 660 s A10G = $0.2427), :118 (settle `wall + 60`).
  N59 REPORT says it deployed the 900 s scaledown_window.
- Scenario: until N59 merges, DEV runs main. A clicked object finishes in 90 s on L4. The ledger records cost(150 s L4) = $0.0426,
  but the container stays warm 990 s, about $0.28. That is roughly $0.24 to $0.31 unrecorded per click, so 30 to 40 clicks
  put real Modal spend about $10 past the ledger. The cap can be broken without any ledger row showing it.
- Minimal fix: merge N59's sf3d.py constants (IDLE_S 900, ESTIMATE 1620 s) before more DEV clicks. If the merge must wait,
  redeploy r2s-sf3d from main (scaledown 60). Not verified: the live Modal scaledown_window. This finding relies on N59's
  REPORT; `modal app` inspection was not run.

### P2
**P2-a. Shell rebuild invalidates the batch but does not cancel the SF3D call already in flight.**
- Where: Build/reconstruction/shape_upgrade.py:62-65 checks the batch only before each item; :68 blocks in generate_remote for up to 660 s.
- Scenario: a user clicks Build lab shell while upgrade 1 is running. The new batch is written, and the old call still runs up to
  660 s plus 900 s idle. Its paid mesh is then dropped by _update (:29-30). Each rebuild wastes up to one call: $0.33 to $0.37
  recorded, $0.5957 reserved. Bounded and on the ledger, but not stopped.
- Minimal fix: add an `abort=None` callable to generate_remote. Poll `handle.get(timeout=10)` in a loop until timeout_s and
  call `handle.cancel(terminate_containers=True)` when `abort()` is true. Pass
  `lambda: _read(d,"shape-upgrades.json")["batch"] != work["batch"]`. Keep the full-estimate settle on unconfirmed cancel.

**P2-b. An API restart mid-upgrade leaves objects "pending" forever.**
- Where: shape_upgrade.py:56-57 (`started_at` set means never rerun), :50 (in-process supervisor only); api/room/__init__.py:83 reports
  pending as-is.
- Scenario: Railway restarts during upgrade 2 of 4. The gpu_jobs row is reaped at the full reservation, so spend is fine. Items 2
  to 4 show "SF3D shape improvement pending" indefinitely, which is a false status. A restart between status done and thread start
  does the same with no spend. The orphaned Modal call runs up to 1500 s and is covered by its reservation.
- Minimal fix: in the status/result read, report any pending item as `failed` with "SF3D interrupted (server restart)" when
  `started_at` is set, or when the job is done, and `str(d) not in shape_upgrade._running`. Do not auto-resume, because that
  would pay again for an item whose orphaned call already billed.

**P2-c. Per-user spend and storage are unthrottled on shell rebuild. This predates N59, and N59 adds file growth.**
- Where: Build/api/room/objects.py:144-152 (POST /rooms/{id}/shell has no per-user limit); Build/api/storage/files.py:84
  (quota sums only `files` rows, not rooms/<owner>/ artifacts); shape_upgrade.py:16-19 (each batch writes new
  `{batch}-{id}.png` crops and never deletes old ones).
- Scenario: one signed-in user rebuilds the same room repeatedly. Each rebuild is hosted SAM detection plus up to 4 SF3D calls
  (about $1 to $2 recorded), so roughly 5 to 10 rebuilds use the global $10/day cap and lock out every other user. The 20 uploads
  and 1 GB limits are never touched. Disk grows by one PNG set per rebuild.
- Minimal fix: count each shell rebuild against the user's daily uploads (store.check_daily plus a row), or cap at N per room
  per day. In prepare(), delete the previous batch's PNGs.

### P3
- **P3-a. Serial calls each charge a full 900 s idle** (sf3d.py:125). Four upgrades in one warm window record about 4 x 900 s of
  idle where real idle is about 900 s once (around $0.8 over-recorded per room). This is conservative, but it uses cap headroom.
  Fix (optional): leave as is, or charge idle only when no other sf3d job is queued.
- **P3-b. Click cost about 7x.** IDLE_S is shared, so the interactive click path (objects.py:112, 90 s budget) now records
  cost(wall+900). A 90 s L4 click goes from $0.043 to $0.281. The N31 comment marked 60 s as a pending owner decision; 900 s matches
  the 15-minute AGENTS rule. Fix: note the owner decision, or use a separate low-idle function for clicks.
- **P3-c. SF3D joins the shared GPU queue** (sf3d.py:103-105, api/gpu/__init__.py:139-153) even though it runs on its own
  Modal app. Other users' reconstruct/track jobs wait up to 660 s per queued upgrade. Reservations are held during the wait (up to
  1800 s), which can cause false DAILY_CAP refusals. Fix: acceptable for one queue; or reserve after start() and write the id to
  the row.
- **P3-d. A non-timeout handle.get error does not attempt cancel** (sf3d.py:113-115). A gRPC or network error may leave the call
  running. This is bounded by the retained estimate. Fix: best-effort `handle.cancel(terminate_containers=True)` in a generic except.
- **P3-e. Unchanged ledger edges.** live_room.py:275 settles a failed reconstruction at an unbounded
  `cost(time.time()-call+900)`, which can record above its reservation if remote() hangs; apply the same min(wall, 540) bound.
  Spend is booked on the reservation day, so a call reserved before Dhaka midnight bills into the next day (matters Nov 8 to 9,
  $20 to $10). LOCK and _running are per-process: safe with the single uvicorn process
  (infra/railway/dev/api.Dockerfile:22), but they break with replicas or --workers > 1.

## Not checked
Live Modal deployment config, provider bills vs ledger, Railway replica count, web editor polling (out of spend scope),
and behaviour under a real restart. Not reproduced: these findings come from reading the code plus the 41 passing tests.

