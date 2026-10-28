# S05b recovery8 — source-lane deadline review fixes, LOCAL ONLY

Fresh separate desktop chat, existing Meta AI Hackathon project91e441f8-e40c-4ec4-
bea2-de7fa1582d97, managed gpt-6.1-sol/medium, CODEX-1. Full30m deadline/issue/
minute25 cutoff explicitly IN launch handout and TIMEBOX.json. Follow strict
WORKER_TIMEBOX_POLICY; incomplete -> nonterminal blocker/remaining useful work,
not early terminal PARTIAL. Verified all child criteria DONE may finish early;
parent S05b remains PARTIAL. No time padding/scope/permission expansion.

Canonical root C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon.
Use ONLY prepared s05b-recovery4 checkout/run/S05b-recovery8, basee68b88b.
Read current canonical AGENTS/OWNER_INSTRUCTIONS and exact accepted findings
evidence/S05/guard-review/FINDINGS.md (partial other-vendor reviewe39aec4);
sourcecd42ebc and installed Modal1.6.3 source text directly, not citations alone.
APPLY Ponytail full/default and relevant debugging/testing guidance.

Objective: smallest complete local fix for late-stop omission and independent
wallclock/resource-stop enforcement gap, WITHOUT executing a paid/cloud job.
Review repro shows asyncio.wait_for cancellation isn't an independent time bound;
controller freshly reproduced late return2.21s vs requested0.2s under10s parent cap.

Owns ONLY Build/reconstruction/spike/ source/tests/README necessary for guard
fix (requirements/locks/model/resource pins read-only), evidence/S05/S05b/recovery8/,
Run-System/Runs/S05b/recovery8/{PLAN.md,REPORT.md,TIMEBOX.json}.
No canonical controls, commits/rebases/merges, fanout, browser/service/API calls,
runner/Modal import invoking cloud, installs, CPU/GPU/model/media transfer/job.

Acceptance:
1. Late SDK overshoot cannot skip the actual app-stop attempt just because prior
   work deadline expired; receipt distinguishes attempt/dispatched/acknowledged/
   independently confirmed stop. Preserve original failure; emergency cleanup
   gets reserved independent bounded time, not hidden indefinite budget growth.
   Test already-expired clocks/slow cancellation; don't merely claim requested
   stop before invoking it. Atomic local receipt if smallest useful fix.
2. Independent out-of-event-loop watchdog/procedural enforcement for total setup+
   queue+execution+cleanup is present and locally testable with an isolated
   noncooperative/hung child. Killing client ALONE is not remote stop. Use actual
   supported SDK semantics for fresh out-of-band stop/state verification of exact
   own app (not broad account/name guessing); inspect local SDK as text, no RPC.
   Unknown app ID/failed independent verification -> durable resource incident,
   no success or paid-ready claim. No generic scheduler/dependency/framework or
   unapproved source uploads/configuration/resource changes. Choose simplest
   complete design, report genuine impossible prerequisite NONTERMINAL.
3. Fresh deterministic tests cover success, timeout/hang, app-ID publication loss,
   independent stop failure/confirmation, late-stop attempt, evidence failure and
   unchanged input/resource/retries0/pinned revision/egress guards. Spike and scene
   regressions; runtime/remote stop still NOT_VERIFIED. Document exact future
   admission prerequisites; no new paid attempt or CPU reinstall authorized here.

At minute25 no new implementation, use remaining verification/report work. If
guard cannot be safely completed, send exact nonterminal blocker before deadline
and continue remaining local checks; don't broaden safeguards or invent success.
REPORT concrete Ponytail reuse/minimal complete changes/checks/skips/risks, actual
UTC/route visibility, TIMEBOX.json checked by canonical worker_timebox.py.
No coding quota poll, model/provider/credential/global-policy change;2.85/$30
unchanged, no new reservation/physical GateR/metric/S12 result.
Owner authorizes nonterminal blocker coordination and ONE terminal report-pointer
callback to controller01a182c4-9378-7da0-9fbc-99a5a379380c. Otherwise quiet.
