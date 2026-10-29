# R15-replay — DONE (scoped S10p recovery)

## Result and provenance

Recovered and verified the interrupted R14-replay-fix implementation. The unchanged frozen regression now passes **31/31**; the complete directly impacted replay suite passes **50/50**, with no skips/todos. Actual four-template CLI replay and trace hashes equal the original R14 receipts. This is local deterministic synthetic data correctness, **not authentication, physical accuracy, Gate P/M/S12 acceptance, native review or UI verification**.

- Assigned CODEX-1 / existing managed `gpt-6.1-sol` / high. Assignment is not independent runtime/model attestation. Coding quota: **OpenCodex-managed; not polled**. Tokens/costs unknown/unobservable; no paid job or reservation.
- Original new window: issued `2026-10-29T07:23:45.000Z`; deadline `07:53:45.000Z` / `13:53:45` Dhaka; minute25 cutoff `07:48:45.000Z`. First tool `07:23:58Z`. Actual product-work stop and report timestamps are in `TIMEBOX.json`; full1800-second arithmetic is checked by the existing validator. All acceptance was verified early; no early incomplete exception, clock reset, padding or extension used. Owner stop `10:00Z` / `16:00` Dhaka does not cross this window.
- Checkout: `C:/Users/HP/.codex/worktrees/swarm14-replay/2026-10-26 - Meta Global AI Developer Hackathon`; inherited HEAD `f62b095734791798f2fe62149ddcc6d60b8ab7c4`. Created `run/R15-replay` from `run/R14-replay-fix` without reset; canonical main observed `6e1784b24890e6b37e31499769b0a2d5ea3df51b`, not rebased/merged/changed here.
- Inherited canonical root/project: Meta AI Hackathon `91e441f8-e40c-4ec4-bea2-de7fa1582d97`; child UI binding not independently verified. Direct owner inline-recovery authorization used; no worker/fanout or automatic continuation.
- R14-fix had uncommitted source/docs/tests/TAP, PLAN and an ACTIVE TIMEBOX but no terminal report or actual stop receipt. Its actual interruption/stop remains **unknown**. Preserved its artifacts and original timestamps; did not backdate a stop or accept its old green TAP blindly.

## Smallest complete change / Ponytail full

Read/applied the installed full/default Ponytail instructions. Inspected all replay API callers before deciding no caller/API change was needed. Reused the existing canonical serializer, clone/deep-freeze helpers, SHA-256 format and validation error prefix; no dependency, new product abstraction, version migration or unrelated refactor.

- `Build/simulator/replay.mjs`: recovered descriptor-based own-index array traversal, rejecting sparse/non-index/symbol/accessor properties without calling overridden `map` or index getters. Object values also use checked data descriptors. Dense subclasses preserve actual own values rather than manufacturing canonical output.
- Creation and replay share metadata validation. Replay detaches/freezes one initial snapshot synchronously before the first digest await, validates it before the runner, and uses that same snapshot for verification, runner arguments and output comparison. The synchronous runner receives separately cloned parameters.
- `Build/simulator/replay.md`: recovered the data contract and explicit non-authentication/Proxy-sandbox limits.
- `tests/simulator/replay-recovery.test.mjs`: retained all18 interrupted recovery cases and added one dependency-free assertion for the existing unsupported-version caller contract. No additional product edit was necessary after fresh verification; recovered source SHA-256 is `483afb36ea0de093219379453cb3dccd158d6acdf8cc52fc76c413d82e832e11`.
- Only additional run helpers reproduce the pre-fix frozen failures without replacing working files, and verify the real CLI against existing frozen artifacts. No frozen test/input/oracle edit or regeneration.

## Fresh verification / retained failures

All evidence paths below are under `evidence/S10/replay-recovery/`.

| Command | Actual result / evidence |
|---|---|
| `node --import ./Run-System/Runs/R15-replay/baseline-loader.mjs --test --test-reporter=tap tests/simulator/replay.test.mjs tests/simulator/r14-replay-invariants.test.mjs` | Expected exit1: **18 pass /13 fail**, all original frozen counterexamples; `r15-frozen31-baseline.tap`. Loader reads committed pre-fix replay from `f62b095` via Git; never overwrites source/oracles. |
| `node --test --test-reporter=tap tests/simulator/replay.test.mjs tests/simulator/r14-replay-invariants.test.mjs` | Exit0: **31/31 pass**; `r15-frozen31.tap`. |
| Initial combined recovery + `tests/lab/contact-integration.test.mjs` command | Exit1: **18 pass /1 module-load failure**; `r15-targeted.tap`. Contact file cannot import the absent `@dimforge/rapier3d-compat`; neither contact subtest executed. Not concealed, not treated as a replay failure or a successful integration check. No installation, test weakening, dependency junction or retry churn. |
| `node --test --test-reporter=tap tests/simulator/replay-recovery.test.mjs` | Exit0: **19/19 pass**; `r15-recovery19.tap`. Includes the unsupported-version assertion without importing unrelated contacts. |
| `node --test --test-reporter=tap tests/simulator/replay.test.mjs tests/simulator/r14-replay-invariants.test.mjs tests/simulator/replay-recovery.test.mjs` | Final exit0: **50/50 pass**, zero failed/cancelled/skipped/todo; `r15-final50.tap`. |
| `python Run-System/Runs/R15-replay/verify_transport.py` | Exit0: actual `Build/lab/replay-check.mjs` for all four existing validated synthetic artifacts; full CLI receipts equal frozen R14 expectations, including both hashes, determinism/seed binding and sample counts201/201/201/1001; `r15-transport.json` includes source/artifact SHA-256. |
| `node --check Build/simulator/replay.mjs` and `node --check tests/simulator/replay-recovery.test.mjs` | Exit0. Node `v24.18.0`; Python `3.14.5`. |
| `git diff --quiet f62b095 -- tests/simulator/r14-replay-invariants.test.mjs evidence/S10/replay-invariants` | Exit0: frozen tests, inputs, hash receipts and findings unchanged. |
| Targeted unowned-source diff and authored source/docs whitespace checks | Exit0; no lab/instruments/web/contracts or shared controls changed. Raw TAP whitespace is reporter output and retained verbatim, not rewritten as authored code. |

Old `before.tap`, `frozen31-after.tap` and `recovery-tests.tap` are retained interrupted R14 evidence only; fresh conclusions use `r15-*` files. Test-driven verification: independently frozen tests predate recovery; fresh loader run confirms the same13 pre-fix failures, then current code passes without oracle changes. Applied verification-before-completion: read fresh results and inspect source/frozen-path diffs before scoped commit/completion, not old report claims.

## Scope, skips, risk and handoff

- Actual product/test work stopped `2026-10-29T07:32:54.852Z` / `13:32:54.852` Dhaka; report finalized `2026-10-29T07:33:09.000Z`. Subsequent operations only package/commit/read back this report and validate the terminal receipt; no further implementation or product test work. Scoped changes committed on `run/R15-replay`; parent retrieves the exact SHA from this branch. No merge or FF performed here.

- Changed only owned replay source/docs/tests, replay-recovery evidence and this run directory. Preserved all inherited uncommitted edits; no shared controls/main merge or old R14 receipt edits. Parent serializes native gate review, instrument quantizer integration, IAB375px, any heavy build and main FF.
- **Remaining check outside this child:** actual Rapier contact integration in an already provisioned parent environment. Its module-load failure is recorded above; no claim that contacts or the full lab passed. The pure replay version contract and real replay CLI did pass.
- Ordinary JSON identities and negative-zero normalization remain unchanged. Hashes detect consistency, not authorship/authentication; anyone can reauthor a consistent record and hashes. Seed binds identity, not noiseless trajectory randomization. Direct-JS descriptors/subclasses are not evidence of reachability from parsed JSON; hostile Proxy/global-runtime isolation is not promised.
- Deliberately skipped private Mystery/auth audit (refused shard not retried/rephrased), broad physics/fitter reruns, full build, browser/native review, real scenes, paid/model/GPU work, Gate M/S12, deployments/publication, accounts/terms/credentials/env values/provider/routing/policy edits and quota polling. No new owner question or permission required within scope.
- Communication compliance: only mandatory initial runtime/skill notices and one concise nonterminal environment finding; no optional status stream, duplicated report, fanout or cross-chat delivery claim. Final response is one report pointer. Findings are available here for parent pipelining; controller must independently accept/integrate this child.

Skipped unrelated build/UI/contact installation. Risk: contact integration remains environmentally unverified here; this child closes replay-data invariants only.
