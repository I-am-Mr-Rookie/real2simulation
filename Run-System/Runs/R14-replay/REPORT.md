# R14-replay — DONE (bounded audit; product has confirmed gaps)

## Contract / clock

- CODEX-1; managed `gpt-6.1-sol`, high per dispatch; underlying model identity not independently introspected or changed.
- Actual first observed start: `2026-10-28T21:37:38Z`; audit work stopped: `2026-10-28T21:47:52Z`; report: `2026-10-28T21:48:47Z`.
- Original issue: `2026-10-28T21:37:28.000Z`; full30m deadline: `2026-10-28T22:07:28.000Z` / `2026-10-29T04:07:28+06:00`; minute25 cutoff: `22:02:28Z`. Completed acceptance early, no terminal incomplete result/extension/padding.
- Isolated checkout: `C:/Users/HP/.codex/worktrees/swarm14-replay/2026-10-26 - Meta Global AI Developer Hackathon`; clean initial baseline `74c886f9b2cc1322dde152f5be5813f813904bc6`; branch `run/R14-replay`.
- Parent project/root inherited: Meta AI Hackathon `91e441f8-e40c-4ec4-bea2-de7fa1582d97`, `C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon`. No independently verified child UI association claim.
- Read current canonical AGENTS/STATE/QUEUE, strict timebox policy, owner instruction transcription, relevant S10hi-gate/S10e-extension/S10fg-extension reports and scoped sources. No historical-memory lookup was needed.

## Findings / frozen oracle

Three source-supported P2 groups, **not fixes and not product-pass evidence**:

1. **Array canonicalization, replay.mjs:10-13.** Index getters execute; non-index keys `01` and `4294967295` disappear and hash like plain arrays. A subclass's overridden `map()` can manufacture trace `[123]` from actual dense values `[0,1,2,3,4,5,6]`. Required invariant: reject unsupported properties before execution; reject the subclass safely or preserve real values without invoking overridden methods. No SHA collision.
2. **Pre-run schema validation, replay.mjs:30-35.** Independently correctly hashed records with negative/fractional/unsafe seeds, null/array parameters, empty/object traces call the runner once before eventual rejection. Expected: metadata rejection before execution. Envelope trace getters are accepted/executed too; the getter case requires direct JS, while malformed schemas can arrive via JSON.
3. **Async snapshot integrity, replay.mjs:32-35.** A queued microtask replaces a valid mutable JSON-like seed1/`{x:1}`/`[1]` record with valid seed2/`{x:2}`/`[2]` fields and hashes. Replay succeeds with seed2 although its first digest checked the old trace. Expected: replay one initial detached snapshot or reject mutation. Repeated envelope reads span digest awaits.

Exact inputs/expected/actual/root causes/reachability: [FINDINGS.md](../../../evidence/S10/replay-invariants/FINDINGS.md) (repository path `evidence/S10/replay-invariants/FINDINGS.md`).
Frozen checks: `tests/simulator/r14-replay-invariants.test.mjs`. They stay RED on the baseline; no TODO/skip, threshold change or bug-fitting expected values.

## Fresh checks / evidence

- `python -m Run-System.Runs.R14-replay.generate_inputs` — PASS. Reuses `Build.lab.regression.regression_case`, S08 factories, actual `export_validated_setup.export` and existing `Build/lab/replay-check.mjs`; four validated synthetic artifacts plus actual hash/seed/sample receipts saved.
- Actual free-fall/projectile/ramp/pendulum replay hashes match the independent Node standard-library SHA-256 oracle and saved transport receipts. Counts **201/201/201/1001**; normal JSON round-trip replay and repeated records byte-identical.
- `node --test --test-reporter=tap tests/simulator/replay.test.mjs tests/simulator/r14-replay-invariants.test.mjs` — **exit1, 31 tests:18 PASS/13 FAIL**, all failures frozen counterexamples above. Latest full run `full-baseline.tap`; no failures concealed.
- `node --test --test-reporter=tap --test-name-pattern='^clean:' tests/simulator/r14-replay-invariants.test.mjs` — **exit0,16/16 PASS**; separately labeled positive subset, not a whole-suite success claim. `clean-baseline.tap`.
- Clean checks include independent literal canonical byte vectors, key ordering/array order, seed0/MAX_SAFE_INTEGER identity binding, detached deep freeze, all six ordinary field/hash tamper cases rejected before runner, changed output rejection, and existing hostile unsupported-value rejection.
- `node --check tests/simulator/r14-replay-invariants.test.mjs` — PASS.
- `git diff --quiet 74c886f -- Build contracts` — exit0, product/schema source unchanged. Staged raw Node TAP contains reporter-generated whitespace-only lines, preserved verbatim; the whole staged whitespace check reports those evidence lines. Authored-source/docs whitespace check is separate below.
- Node `v24.18.0`; Python `3.14.5`. No dependency installation, manifest edit or node_modules junction needed.
- Evidence folder: `evidence/S10/replay-invariants/`; `actual-record-hashes.json` includes actual four-template replay/trace hashes and source-file SHA-256 fingerprints. Full TAP retains expected/actual failures.
- `python Run-System/worker_timebox.py check Run-System/Runs/R14-replay/TIMEBOX.json` — TIMING PASS (separate from acceptance).

## Ponytail full/default — concrete application

Reused existing real factories/validation/engines/transport; the only expected oracle is a small sorted-JSON serializer plus Node `crypto.createHash`, independent of product canonicalization. Used built-in Node tests and Python standard library; no new dependency, feature, product abstraction, runtime patch or manifest change. One audit test file and one owned evidence-generation helper are the smallest complete reproducible audit surface.

## Scope / limitations / next action

- Owns only this run directory, `evidence/S10/replay-invariants/`, and `tests/simulator/r14-replay-invariants.test.mjs`. No product/control writes or merge. Parent must decide/fix/integrate; audit DONE does not accept S10, Gate P, physical Gate M or S12.
- Hashes are consistency checks, not authentication: reauthoring data plus hashes creates a new consistent record. Seed binds identity only; noiseless physics is not seed-randomized. JSON canonicalization intentionally normalizes negative zero.
- Lab replay transport records sample arrays, not full output metadata (units/stop/source labels); `regression.py` separately compares repeated full stdout. No whole-output persistent tamper protection is inferred from sample hashes.
- Direct-JS getter/prototype findings are not proven reachable through normal JSON-only lab input. Async mutation requires a mutable caller record; malformed schemas eventually reject, but only after runner side effects.
- Skipped deliberately: RK4 accuracy, contact numerics, covariance, actual Windows abort, production build, browser375px, real scenes, GPU/paid jobs, deployment/publication, credentials/config/quota. No unrelated ceremonial rechecks.
- Recommended parent action: retain the frozen tests; fix canonical array traversal, validate/snapshot one record before any await or runner call, then rerun full31 without weakening the oracles. No product change was attempted here.
- Coding quota: **OpenCodex-managed; not polled**. Tokens/costs unknown/unobservable.
- Communication compliance: required initial skill/runtime notice and concise nonterminal finding callbacks emitted in this chat. Explicit parent callback attempted using identified controller thread `01a1840d-7310-7991-8cb8-8ec4cfb149a7`; app returned `cannot send to your native ancestor`. No native collaboration messaging tool is exposed in this worker catalog; no retries/new chat/fanout. Delivery through that app callback is NOT claimed. Final report pointer is the completion handoff.
