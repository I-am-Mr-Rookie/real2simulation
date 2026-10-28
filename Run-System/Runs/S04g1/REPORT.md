# S04g1 — DONE

## Objective and changes

Harden only `infra/railway/dev/` deployment acceptance. `verify.py` now checks
exact JSON service on all six API/worker endpoints; exact health status `ok`,
except worker readiness `unavailable`. Version endpoints require service/revision,
not status: owning API/worker contracts intentionally omit status there.
Pinned deployed revision300cd2096f9e32bcdf3433520b36b67f709df0d5, HTTP codes,
exact dependencies and web/auth fallback checks are unchanged. Worker503 is
accepted only with Redis/bucket ok and heartbeat unavailable; not job readiness.
README documents endpoint semantics and commands. New stdlib synthetic transport
tests execute the actual CLI through runpy; fixtures are not runtime/gate evidence.

## Evidence

- `python -m unittest discover -s infra/railway/dev -p test_verify.py -v`:
  [offline-red.txt](offline-red.txt), exit1, 24 semantic rejection failures before
  fix. Baseline and existing revision/dependency/HTTP safeguards passed.
- `python -W error::ResourceWarning -m unittest discover -s infra/railway/dev -p test_verify.py -v`:
  [offline-green.txt](offline-green.txt), exit0, seven tests with endpoint-specific
  negative subcases: wrong/missing service and health status; opposite availability;
  wrong/missing revision; incorrect HTTP code; wrong/missing/extra dependencies;
  worker heartbeat falsely ok; non-object JSON. Valid statusless versions accepted.
- `python infra/railway/dev/verify.py`: [live-http.json](live-http.json), exit0,
  10/10 at2026-10-27T20:53:28Z. API live/ready/version200; worker live/version200,
  ready503 with expected unavailable heartbeat; web home/library/sign-in200,
  private route404. Source revision unchanged. No model/job/authenticated E2E.
- Railway plugin read-only get_status: [plugin-status.txt](plugin-status.txt)
  records reauthentication required. No retry or credential/auth change; current
  provider-side deployment status unavailable, independent public HTTP succeeded.
- `git diff --check`: exit0. Fresh post-rebase/main checks recorded below.

## Lifecycle, skills/plugins, boundaries

Claim d6e22f8 on canonical main after preserved unrelated untracked references;
native managed isolated worktree, branch `run/S04g1`. Initial main6bb2bf8.
Only exact task files/run evidence staged. Canonical claim and finalization
serialized with controller/other lane; no persistent locking-policy change.

Applied installed Superpowers skills under
`C:/Users/HP/.codex/plugins/cache/openai-curated-remote/superpowers/7.0.1/skills/`:
systematic-debugging (checklist reproduction traced to absent semantic comparisons,
compared owning endpoint contracts); test-driven-development (real24-failure
red then minimal comparisons and green); verification-before-completion (fresh
offline/live/diff checks before commits); using-git-worktrees (native tool,
isolated branch and explicit returned directory). using-superpowers was read;
its delegated-task skip applies. Railway plugin actually invoked read-only;
connection unavailable as recorded. No install, browser, Clerk, GitHub, deploy,
credentials, account, model/provider/routing/policy or publication action.

Requested CODEX-2 GPT-6.1 Sol medium; actual delegated Codex runtime, exact model,
effort, tokens and coding cost unavailable. OpenCodex-managed; not polled.
Claim start2026-10-27T20:52:03Z; initial read-only bootstrap preceded claim.
Meta/inference/GPU calls0; existing Railway runtime costs unknown, not zero.
Gates R/M/P/RS/A/C/D/S remain NOT RUN. No deployment or product readiness claim.
No owner question. Next S04h still awaits S01b/Q4 and separate approved auth scope.

Communication: mandatory brief pre-tool update/skill announcement only;
coordination messages necessary to serialize claim/FF windows, explicitly authorized.
No optional progress or duplicated chat report; final one-line signal. Evidence
on disk; owner questions would go to STATE fallback, none needed.

## Finalization

Controller granted final serialized window; rebased on main b563519 and freshly
passed seven tests ([post-rebase.txt](post-rebase.txt)). Verified FF de29f3475e5cdab197e41cb24a8656582eedc3fa;
canonical main repeated seven tests ([main-offline.txt](main-offline.txt)) and
10/10 read-only live GETs at20:54:52Z ([main-live-http.json](main-live-http.json)),
all exit0. `git diff --check` exit0. Native managed-worktree archive refused:
`The task's primary checkout cannot be removed.` Clean worktree retained without
bypass; branch retained. No underlying deployment changed. Verification/control UTC2026-10-27T20:55:23Z
(control finalization; within15m claim timebox). Actual skill/plugin use, limits,
evidence and communication compliance checked; no questions or new decisions.
