# R10-lab-contract — DONE (worker implementation only)

**Parent acceptance still requires native Claude gate review/re-review. No review pass claimed.**

## Identity, scope and timing

- Project inherited from owner handout: `91e441f8-e40c-4ec4-bea2-de7fa1582d97`; canonical root read-only. No new project/chat/delegation; launcher binding was not independently queried.
- Worktree: `C:/Users/HP/.codex/worktrees/swarm10-lab-contract/2026-10-26 - Meta Global AI Developer Hackathon`.
- Branch: `run/R10-lab-contract`, from `f82ed85fd96c38f8fcee23322657e92e5f4f8e92`.
- CODEX-1/S10 scoped implementation; actual managed runtime model/effort not independently exposed. No route/model/provider changes. OpenCodex-managed; not polled. Tokens/costs unknown; no paid GPU/API work.
- Issued `2026-10-28T19:50:37.990Z`; first clock observed `19:50:49Z`.
- Implementation cutoff `20:15:37.990Z`; full deadline `20:20:37.990Z` = Oct29 `02:20:37.990+06:00`.
- Technical work stopped `2026-10-28T20:03:21.5387682Z`, after verified completion, before cutoff. Report/timebox administrative commit follows. No padding, early incomplete termination, owner-stop exception or scheduler work.
- Source/evidence commit: **`05024f1d6947b1d2c4039673d4b18acafc5b5aa6`**.
- Owner-relayed native-review abort follow-up: **`7aa072c`** (stronger existing test + five-process stress evidence). Both commits are needed; report/timebox committed separately.

## Concrete reproduced defects and smallest fixes

Before implementation, original seven tests passed once. Expanded red check then produced six failures, including the existing intermittent active-abort test returning success; separate hash-boundary red check produced four failures. Raw evidence preserved, not rewritten as passing.

1. **Cancellation could succeed:** Windows termination can race a successful bridge exit; code-zero close previously accepted output despite abort. Keep a sticky stopped flag for abort/timeout/I/O failure, reject even code-zero close, and recheck cancellation after async hashing before session insertion/reveal. A pre-aborted cached fit now fails; an aborted joining waiter cannot receive a successful reveal while the original live waiter still completes.
2. **Evicted/stale fits could reveal:** an in-flight fit held a detached session reference after Map eviction. Check current Map identity and TTL after bridge completion and again after trusted handoff hashing, immediately before reveal/cache mutation.
3. **Bridge capacity bookkeeping was unsafe:** synchronous spawn throws leaked slots; stdin errors released slots before close. Increment only after spawn returns, retain the slot until child close, and treat process errors as failure even if close later reports zero. Existing four-bridge, 64-session, ten-minute TTL, 30-second process and body/sample bounds unchanged.

No interface or numeric-gate changes. Errors retain the existing bounded `{status:'error', error:{code}}` envelope; underlying process/parse details stay private. Existing start/fit, unsupported-template, normal gravity and Mystery-g contracts remain.

## Ponytail FULL applied

- Read installed `C:/Users/HP/.codex/.tmp/marketplaces/ponytail/skills/ponytail/SKILL.md`; old cached path not used.
- Inspected all direct service imports/callers: route POST and tests; traced LabClient request/abort guards and fit parser, existing trusted handoff/reveal implementation and Python bridge.
- Reused the existing Map, in-flight promise, child-process lifecycle, hash/handoff and test file. One small current-session assertion; no new dependency, service abstraction, configurable policy or public test seam.
- Only production edit: `Build/lab/session-service.mjs` (24 inserted / 6 removed lines). Existing `tests/lab/session-service.test.mjs` extended; owned run/evidence files only. No Python/UI/fitter/simulator/manifest or canonical/shared-control edits, merge/rebase or publication.

## Fresh verification

Evidence index: `evidence/S10/session-hardening/README.md` (exact commands and raw files).

- Final implementation: targeted service + UI contract + Mystery-g + replay suite **34/34 PASS**, including **25 service tests**.
- After owner relayed native review's same cancellation race: existing real bridge abort test strengthened to require exact error, aborted signal, no inserted session and zero occupied slots. Five independent test processes: real active abort + deterministic exit-zero abort + post-close/hash abort, **15/15 PASS** (`abort-stress.txt`). Source fix unchanged from `05024f1`.
- Real Python bridge/fitter: **4/4 PASS**, including all four templates and two controlled private seeds.
- Cold fit concurrency starts only one actual bridge; live waiters share the same result, an aborted joiner gets an error. Active aborted Mystery-g fit retries successfully without consuming reveal. Capacity insertion evicts an in-flight oldest session without publishing its fit; expiry before/during hash refuses reveal/cache.
- Controlled spawn/stdin/error/timeout/oversize/invalid JSON events exercise slot accounting and bounded envelopes. Hash gates deterministically test invalidation before reveal; synthetic fixtures explicitly are not fitter/physics accuracy evidence.
- Broader Node suite: **48 PASS / 2 file-load failures** because this isolated worktree lacks existing `@dimforge/rapier3d-compat`; failures are contact tests importing that package. No dependency install/manifest changes. This broad run predates the last two added lifecycle tests; targeted final run covers them.
- `git diff --check`, source/test `node --check`: PASS; owned commits inspected; clean tracked worktree before final administrative files.

## Skips, risks and handoff

- Native Claude gate review/re-review remains required before controller acceptance; no further delegation authorized here. Review changed service source plus deterministic abort-zero-close and hash-boundary tests, and owner-requested stress evidence.
- Actual bridge abort tests show failed request, no inserted session and slot release. **No OS descendant enumeration or end-to-end process-tree death proof**, and no claim existing process limits guarantee descendant cleanup. Stop-tree implementation itself is unchanged.
- First caller's signal still owns a shared in-flight bridge; aborting that owner fails the shared attempt, which can retry. Aborting only a joined waiter does not kill the owner's work; it is checked when that shared attempt settles. No new cancellation architecture.
- No browser/IAB E2E or installed-Rapier contact verification, production deployment or full-repository health claim. Existing route module-type warning remains; manifests were out of scope.
- Physical Gate M/S12/real scenes, licensed-footage approval and paid GPU gates unchanged. No secrets, archived private data, uploads, accounts, terms, permissions or configurations touched. Owner's heartbeat update acknowledged as controller work; no worker scheduler created.
- Communication compliance: only mandatory skill announcement, meaningful broader-suite limitation and direct owner cancellation response; final response is one report pointer. No optional report duplication or other-chat messages.
