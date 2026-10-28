# S05b recovery7 — PARTIAL / LOCAL-ONLY

**Local guard implemented; 21 spike + 11 scene regressions PASS. Remote stop and
runtime NOT_VERIFIED. Parent S05b PARTIAL; scheduler cause UNKNOWN.** No paid run.

## Contract / identity / time

- Canonical RECOVERY-7.md, current AGENTS.md and saved OWNER_INSTRUCTIONS read;
  original scanned PDF not reopened. Current canonical controls read-only.
- CODEX-1, requested existing managed **gpt-6.1-sol / medium**. Runtime backend/
  effort not independently introspected or changed. Coding quota:
  **OpenCodex-managed; not polled**. Observable token count/cost: unknown.
- UTC first inspection14:05:52, final checks14:15:56, report closeout14:17
  on2026-10-28; implementation complete before14:20, deadline14:25.
- App `list_threads` verified separate chat01a182d4-596a-7460-854f-195ad12f6c74
  in existing Meta AI Hackathon project91e441f8-e40c-4ec4-bea2-de7fa1582d97.
  Launcher association is observed, not inferred from filesystem location.
- Prepared worktree only:
  `C:/Users/HP/.codex/worktrees/s05b-recovery4/2026-10-26 - Meta Global AI Developer Hackathon`;
  existing `run/S05b-recovery7`, HEAD8fca36f4bdade0cb9aff00e4cc52df299d1ab6be.
  Clean initial status. No commits/rebase/merge/staging or canonical control edits.
- PLAN persisted after initial implementation/tests; exact scope was read before
  edits. This sequencing deviation is disclosed, not retroactively timestamped.

## Changes / applied Ponytail full/default

Read/APPLIED installed Ponytail5.3.2 full/default. Structural omission: old
`probe.remote()` had no caller queue/setup deadline; function900s/startup90s
excluded queue wait. Reused the exact remote probe, pins, four approved hashed
RM02 inputs, manifest, existing1-app/1-input resources, retries0 and result format.

- `Build/reconstruction/spike/modal_rm02.py`: one guarded async invocation instead
  of unbounded remote wait. Retains recovery5 frame reads, isolates prospective
  recovery7 receipts/results, creates local output directory after confirmed cleanup.
- Adjacent **minimal stdlib** `rm02_deadline.py`: needed so tests can import the
  policy without importing the Modal runner or triggering cloud setup. No scheduler,
  framework, dependency, configurable region/resource fallback or parallel job.
- Total1200s monotonic budget starts before app setup. Reserve90s startup +900s
  execution +60s cleanup BEFORE admission. Setup/enqueue + observed running input
  must finish by150s; very fast completed result also accepted. Slow/no observed
  admission fails closed; ambiguity is not scheduler diagnosis.
- Result deadline1140s. Cleanup attempts app stop even without returned call ID;
  stop acknowledgement gets up to20s, refreshed stopped app + zero runners,
  running inputs and backlog required by1190s. Context exit by1195s leaves5s
  for dispatch/unwinding. No repeated stop/retry or renewed GPU consent.
- Receipt separates stop_requested/stop_acknowledged/remote_stop_confirmed,
  caller exception, cleanup failures and resource incident. Unknown setup response,
  missing verification or failed cleanup cannot return success. Local evidence
  failure cannot skip app stop, and prevents successful export afterward.
- Existing AST/resource/egress checks reused. New fake tests exercise policy,
  not model/Modal behavior. README and illustrative cost test correct stale992s
  deadline arithmetic: $0.340464 for1200s using historical test rates is **not**
  current/all-in billing or a guaranteed resource/cost bound.

Installed Modal1.6.3 source was read as text, not imported. Exact API source paths,
line references and limitations: [API-SOURCE.md](../../../../evidence/S05/S05b/recovery7/API-SOURCE.md).
Read-only source hashes: app.py
`12339BAF9710796915A973BFF2BBB704EF9DB98849F52298D563C02DC0F4CE9F`;
_functions.py `FB219D68391BD883CA0EEE135A5F771E9896114D90BF76C11AB4A49448E21372`;
types.py `43EDCDDD23F1093D8552360BBC582224691CAB971A8DC7096338C4C0456F208B`.

## Fresh verification

[Complete final command output](../../../../evidence/S05/S05b/recovery7/verification.txt):

| Command | Result |
| --- | --- |
| `python -B -m unittest discover -s Build/reconstruction/spike -p 'test_*.py' -v` | **21 PASS**,6.037s, exit0 |
| `python -B -m unittest discover -s contracts/scene -p 'test_*.py' -v` | **11 PASS**,5.449s, exit0 |
| `git diff --check` | PASS, exit0 |
| Fresh diff/status/branch/HEAD inspection | Only owned sources/evidence; existing branch/base retained |

Tests cover impossible/nonfinite budgets, slow setup/no launch, slow enqueue/no
returned handle, no-admission queue cutoff, completed result without running
snapshot, normal success, remote exception, hanging result, stop failure,
acknowledgement without confirmation, context cleanup failure, unknown setup
state, broken evidence storage and hanging cleanup. Existing approved resource,
revision/model, torch family and256MiB egress guards remain.

During development one subsecond cleanup timing test overran by1.8ms under Windows
dispatch. Fixed the test's unrealistic10ms exit headroom to50ms and retained an
explicit5s production unwind margin; final tests pass. This is evidence AGAINST
claiming hard real-time guarantees. Also corrected a PowerShell Tee-Object
parameter-set error; final saved verification uses literal-path Add-Content and
records each actual process exit code. No failed attempt is called a passing run.

## Limits / skipped work / next action

**Policy is locally tested, not a provider hard stop.** `asyncio.wait_for` depends
on cooperative SDK cancellation and event-loop dispatch; cancellation-resistant
RPCs/local shutdown, partitions or process death can overrun caller timing and
leave remote resources unknown. Modal source explicitly marks result-get
coroutines non-cancellation-safe: client cancellation is never our stop proof.
The refreshed API evidence criterion is conservative but actual remote stop
behavior remains NOT_VERIFIED. Missed running snapshots can reject healthy jobs.

Skipped: all runner imports, cloud/service/browser operations, paid compute,
CPU reinstall, footage/model downloads/uploads, installs, credentials/environment
values, auth/settings/policy/provider changes, quota polls, S07 writes, fanout,
shared control regeneration and Git integration. No physical/S12 unlock.
No source-hunt or repeated identical paid retry is authorized by this run.

Retain **$2.85 historical reservations** and unchanged **$30 authority**; no reserve
released, purchases or new paid reservation. Zero jobs launched in this run;
no current billing/rate inference. GateR NOT_RUN/S05c locked; calibration/rights
holds unchanged. Controller should review/integrate this scoped local guard,
retain remote-stop/runtime validation as an unresolved prerequisite, and reconcile
exact billing before any separately scoped continuation. No new owner question.

## Communication / handoff

Only higher-priority mandatory brief work/Ponytail announcement; otherwise quiet.
Evidence on disk, questions in this owned report for controller relay, no duplicated
chat report. One authorized terminal status + absolute report pointer callback to
sole controller01a182c4-9378-7da0-9fbc-99a5a379380c; no old-controller message.
Controller must force-add only exact ignored PLAN/REPORT paths if integrating;
worker changes no ignore rules or canonical controls.
