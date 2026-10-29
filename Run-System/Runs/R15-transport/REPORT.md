# R15-transport — DONE

Recovered and freshly verified the existing minimal UTF-8/raw-byte-cap patch: **frozen 11/11 and targeted 21/21 PASS**. No extra source/test changes were necessary. Scoped branch commit only; parent integration/review remains separate.

## Actual contract and interruption

- Assigned CODEX-1 / existing managed gpt-6.1-sol / high. Runtime model identity not independently attested; route/configuration unchanged. Observable tokens/costs: **unknown**. Coding quota: **OpenCodex-managed; not polled**. No capacity error occurred in this recovery; no retry churn or model/provider substitution.
- Actual issue `2026-10-29T07:23:42.000Z`; first intake command timestamp `2026-10-29T07:23:59.7848948Z`. Minute25 cutoff `2026-10-29T07:48:42.000Z`; full30m deadline `2026-10-29T07:53:42.000Z` / `2026-10-29T13:53:42.000+06:00`. Owner's direct new stop `2026-10-29T10:00:00Z` / 16:00 Dhaka does not cross this run. Actual substantive work stop and report receipt timestamps are in adjacent TIMEBOX.json; final receipt validation/commit packaging follow substantive verification. Fully verified scoped DONE permits early completion; no early-incomplete exception claimed.
- Intake branch `run/R14-transport-fix`, HEAD `79eed4719005abe5b18a2ea51854b3af6eb60fdc`: modified service and session tests plus untracked transport evidence. Created `run/R15-transport` without reset; preserved every existing edit and original log. Main SHA observed at verification: `6e1784b24890e6b37e31499769b0a2d5ea3df51b`; main not modified/merged.
- Original R14 report claimed DONE and checks through `2026-10-28T21:56:54.7498288Z`; its TIMEBOX.json is **absent**, and source/tests/evidence were not committed. Owner's new handout reports runtime usage-limit interruption. R15 did not independently reconstruct the runtime failure or original final stop/report times, did not backdate them, and did not accept that report blindly. Ignored original PLAN/REPORT files remain untouched on disk; original evidence logs are retained. Original audit frozen red receipt still shows 9 pass / 2 fail.
- Current canonical AGENTS/STATE/QUEUE, timebox policy and relevant original audit/recovery reports inspected; owner handout takes precedence over stale 04:00 UTC stop and separate-chat defaults for this inline recovery. Inherited project Meta AI Hackathon `91e441f8-e40c-4ec4-bea2-de7fa1582d97`; canonical root `C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon`. Child UI binding not independently verified. Old handle not_found supplied by handout; no duplicate worker/fanout launched.

## Concrete Ponytail full application / smallest complete change

- Read full supplied Ponytail SKILL.md. Inspected the shared `bridge()` reader, both start/fit callers, fixed Python JSON producer, existing controlled-child tests and frozen independent oracle before acceptance.
- Reused the correct interrupted patch unchanged: native `node:string_decoder` carries incomplete UTF-8 code points across stdout chunks and flushes on successful close. Raw Buffer lengths enforce existing 1,000,000-byte cap before decoding/accumulating an overflowing chunk. Ignore further output after stop.
- Reused the three interrupted focused tests unchanged: all interior splits in 2/3/4-byte characters; exact 1,000,000-byte multibyte reply acceptance; byte 1,000,001 sticky rejection/no session insertion/capacity retained until close.
- Shared root fixed once for both bridge callers: 5 additions / 3 deletions in service, 34 test additions against base. No abstraction, dependency, producer/schema/config changes, or broader refactor. No additional code written just to fill the window.
- `stopTree`, sticky abort/timeout, slot-until-close, session/reveal/privacy, HTTP route and frozen oracle remain unchanged; baseline isolation diff proves the latter route/producer/oracle pins. Parent owns instrument quantizer integration and UI verification.

## Fresh checks and evidence

All commands run in this assigned worktree, Node v24.18.0, local CPU only. Fresh raw TAP and verification/source pins are under `evidence/S10/transport-recovery/R15/`.

| Check | Actual outcome |
|---|---|
| `node --test --test-reporter=tap tests/lab/r14-service-invariants.test.mjs` | exit0; 11/11 PASS; zero fail/skip/cancel/todo; frozen11.tap |
| Exact targeted selector in evidence README, `tests/lab/session-service.test.mjs` | exit0; 21/21 PASS (18 existing + 3 transport); zero fail/skip/cancel/todo; session21.tap |
| Frozen oversized counterexample | 1,020,218 bytes / 340,218 code units rejects; zero inserted sessions |
| `node --check` service and session tests | exit0 each |
| `git diff --exit-code 79eed4719005abe5b18a2ea51854b3af6eb60fdc -- tests/lab/r14-service-invariants.test.mjs Build/web/src/app/api/lab/route.js Build/lab/session-bridge.py` | exit0; unchanged frozen oracle, HTTP route, Python producer |
| `git diff --check` | exit0 |
| Staged source/test/Markdown whitespace and owned-path review | PASS; all staged paths inside Owns |
| `git diff --cached --check` across raw evidence too | exit2 only for one blank context line in each saved product.diff (R14 original and R15 exact copy). These are valid raw diff context, preserved verbatim, not source whitespace errors. Source/test/Markdown check exits0. |

Pins: base service `f5b724ddffe04b0e7c566b25e81a2074c8f5b881`; recovered service `94b350f4a5d85029850c1cfe0b5d4372df591da6`; frozen11 oracle `d36fc348c3dc43c7e0baa11d767df280fbb3f27c`; session tests `150cae05e10e66214298705781b1c7e914af2bd3`. Recovered source/test hashes exactly match the historical R14 report, now independently rerun rather than trusted.

Selected tests use controlled child events; their module also initializes one actual Python CPU start-export fixture at import. Mock children have no pid: this does **not** verify OS process-tree termination. Existing Node MODULE_TYPELESS_PACKAGE_JSON warning unchanged. Fresh logs preserve it.

## Scope, handoff, skips and risks

- Owned changes only: recovered service transport lines, directly necessary session tests, transport evidence (including new R15 subdirectory/README note), and this R15 run directory. Original ignored R14 reports remain outside the commit. No shared controls, main, frozen tests or other workers' paths changed.
- Scoped commit subject: `fix(lab): recover verified UTF-8 transport and raw-byte cap`. Parent should inspect committed pins/diff and fresh logs, then serialize native gate review, broader integration, IAB375 and any heavy build/main fast-forward. This worker does not claim those acceptances.
- Communication: minimal mandatory developer pre-work/Ponytail announcements and one nonterminal green finding for pipelining; no optional summaries, other-chat messages or fanout. Final response is one report pointer.
- Skipped full builds, actual Windows process-tree rerun (unchanged lifecycle), arbitrary producer/privacy audit, instrument quantizer work, UI375/native cross-vendor review, model jobs, paid GPU, real scenes, physical GateM/S12, installs, deploy/publish/accounts/terms/credentials/env values/provider/routing/policy changes. No quota polling.
- **Latent P3 only**: current Python producer still ASCII-escapes non-ASCII text by default. No observed normal-producer exploit/failure or release blocker is claimed. Malformed UTF-8 retains Node replacement behavior, not strict encoding rejection. Synthetic transport tests prove no real-scene, fitter-accuracy/calibration, or physical success.
