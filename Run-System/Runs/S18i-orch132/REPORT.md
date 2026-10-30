# S18i-orch132 REPORT — DONE (measurement); product target NOT met: 0/3 openable demos open < 3 s

- Lane/model: CODEX-2 (army: Claude), anthropic/claude-opus-5-5/medium. Coding quota: OpenCodex-managed; not polled. Tokens/cost: unknown (unobservable); $0 spend, no GPU/network/deploy.
- UTC: issued 2026-10-30T11:08:17Z, worker start ~11:10:58Z, stopped 2026-10-30T11:24:08+00:00. Branch run/S18i-orch132 from main 392683f.

## Result (evidence/S18/S18i-load-times.json, measured_at 2026-10-30T11:21:26Z)
Conditions: Windows 11, Intel 4-core (Model 126), Python 3.14.5, Node v24.18.0; local uvicorn on 127.0.0.1 + Node fetch + real Build/library/loader.mjs; 5 warm reps, 3 fresh-process cold runs; OS file cache not flushed; single benchmark run on an otherwise idle worktree (a first run overlapping a profiler was discarded).

| Measure | median | p95/max |
|---|---|---|
| fresh-process import guest | ~1.9 s | 2.0 s |
| first load_guest (cold) | 5.1 s | 5.8 s |
| warm load_guest in-process | 6.1 s | 8.0 s |
| server start (TCP ready) | 2.6 s | — |
| cold first GET manifest | 4.2 s | — |
| warm GET manifest | 4.5 s | 5.7 s |
| open projectile trace (manifest+artifact+validate) | 9.0 s | 10.0 s |
| open pendulum trace | 9.1 s | 10.5 s |
| open Mystery-g metadata | 9.4 s | 15.4 s |

- 18 manifest entries: 3 openable (2 playable traces + Mystery-g metadata-only), 15 UNAVAILABLE (render instantly from manifest; loader does no GET; not counted as demos).
- **0 of 3 openable demos open under 3 s; 6-demo target not met** (also only 3 openable demos exist).
- Root cause (cProfile of one load_guest): every manifest AND artifact request re-runs full load_guest: 5 validate_file calls → ~95 bounded custody/evidence file reads + sha256 (~58% time) and jsonschema check_schema+validation per catalogue (~35%). An open = 2 requests = 2 full revalidations. guest.py deliberately avoids caching (revocation must hit next request; README requires an explicit invalidation design), so I did not change it.
- Next action (owner/controller choice): precompute a sealed guest projection (manifest+objects) at build time and serve it with a cheap stat/hash freshness check, or cache Draft validators (check_schema once) + fingerprint-keyed custody cache. Either needs S18f/S18g owner of guest semantics and a regression test that revocation still fails closed.

## Files
- Build/library/load_times.py (orchestrates cold subprocesses, warm in-process reps, local server, writes JSON); Build/library/load_times.mjs (HTTP timing through loader.mjs, asserts each load's id/availability).
- tests/library/test_load_times.py (nearest-rank stats self-check).
- evidence/S18/S18i-load-times.json; evidence/S18/S18i-library-tests.txt; Run-System/Runs/S18i-orch132/{PLAN.md,TIMEBOX.json,REPORT.md}.

## Checks (fresh)
- `python -B -m Build.library.load_times` → summary above, exit 0 (~2.2 min).
- `python -B -m unittest discover -s tests/library -t tests/library` → Ran 83 tests, OK (82 prior + 1 new).
- `python Run-System/worker_timebox.py check Run-System/Runs/S18i-orch132/TIMEBOX.json` → TIMING PASS (timebox-check.txt).

## Ponytail
- Reuse: real create_app/load_guest + loader.mjs (no reimplemented loader/validator), stdlib statistics/socket/subprocess, installed uvicorn; no new deps.
- Smallest complete: one manifest GET per rep shared by entries (first version re-fetched per entry → ~36 min run; killed). Cold = fresh process / first request; TCP-only readiness probe so cold isn't pre-warmed.
- Skipped: web /library route timing (S04j not merged to my base; Build/web untouched); browser rendering/Three.js mount time; OS cache flush; deployed/Railway latency; any guest.py optimisation (design-owned).
- Risks: n=5 so p95≈max; 4-core laptop timings are noisy; numbers are local and not deployment latency.

## Communication
Silent; one completion line to controller chat as authorized.

