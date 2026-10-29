# R15-consumer-fixtures — DONE (consumer fixtures only)

**Fresh browser consumer suite: 10/10 PASS. All four unchanged-artifact CLI traces independently pass accepted S08 analytic references at unchanged `0.005`. Only ramp/pendulum derived snapshots changed. No broader gate pass.**

## Assignment / timing / isolation

- CODEX-2, assigned existing managed Sol/medium; actual runtime identity/effort not independently attested. **OpenCodex-managed; not polled. Tokens/cost unknown.** No model/provider/credential/policy changes, capacity error, paid job or quota query.
- Original issue `2026-10-29T07:39:21.000Z`; minute25 cutoff `08:04:21Z`; deadline `08:09:21Z` / `14:09:21` Dhaka: full **1800 seconds**, unchanged after Ponytail reminder. Owner stop `10:00Z` / `16:00` Dhaka not crossed. Actual substantive work stop/report receipt **`2026-10-29T07:49:53.955059+00:00`**, followed only by report/Git packaging. Validator result: [TIMEBOX.json](TIMEBOX.json), [timebox-check.txt](timebox-check.txt). All owned acceptance completed early; no early incomplete exception, clock reset or idle padding.
- Reused required clean closed transport checkout, verified HEAD `9598213140b74db8be2fca2adc21aa408a73cbb5`; preserved old `run/R15-transport`. Created `run/R15-consumer-fixtures` from combined source **`b37f7b8f03f9a31c6c0b245913509c0b4dfbf0c9`**. No reset, deletion, rebase, main merge or shared-control edits.
- Canonical project/root and inline exception inherited from handout: Meta AI Hackathon `91e441f8-e40c-4ec4-bea2-de7fa1582d97`, `C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon`. Child UI association not independently verified.
- Parent reports native review complete on immutable `b37f7b8`, no P0-P2. This sidecar did not conduct/repeat native review or touch Build. Preserved Build tree **`c58acfffced6fedfa0bc9caf2281d7cf23682232`**.

## Concrete Ponytail full/default application

Read the installed requested full skill at `C:/Users/HP/.codex/.tmp/marketplaces/ponytail/skills/ponytail/SKILL.md`, verified by successful file read; no plugin installation/change. Read generator, caller/test contracts, accepted S08 analytic functions, R15-numerics report and `Build/simulator/NUMERICS.md` before changing evidence.

The smallest complete change is **two derived JSON traces**, not product source, tests, or frozen input regeneration. Existing `generate_fixtures.py` also writes artifacts: deliberately **did not execute/modify it**. Reused its actual `node Build/lab/simulate.mjs` subprocess path with original artifact bytes. Added one evidence-only reproducible verifier using Python stdlib, existing S08 analytic functions, and existing `Build/lab/regression.py` characteristic scales. No new dependency, product wrapper/model option or manually patched output value. It verifies every sample against independent analytic code, repeated CLI determinism, original metadata/times, immutable hashes, and all four cases **before accepting/writing any snapshot**; rerunning it is idempotent.

## Model / exact provenance

- Original snapshot provenance commit: **`3a0d943b79a1cf41b558b94a6224bc9845a5674d`**, retained through Git; pre-refresh snapshots also remain at `b37f7b8`. Old runtime version unknown.
- Accepted S08 small-angle dynamics are `theta''=-(g/L)*theta`; R15 makes the existing `small-angle-linearized` selector actually use that model, retaining sine force only for `nonlinear-only`. Linearized energy is the correct invariant in this domain. No oracle/threshold/amplitude/fixture change here.
- Ramp now uses the S08 `g*(sin(angle)-mu*cos(angle))` order; R15 RK4 finite weighted arithmetic can change ordinary trace bits. This is explicitly recorded correctness-neutral bit drift, **not** a claim of equality with old snapshots/replay records. Existing replay records remain untouched.
- [generation-verification.json](../../../evidence/S10/consumer-recovery/generation-verification.json) contains **full exact** original/current source Git-blob SHA256, checkout SHA256, old/new snapshot hashes in both conventions, original artifact hashes, per-field differences, runtime versions, actual commands, and all **46** immutable before/after hashes. `core.autocrlf=true` means raw CRLF checkout hashes differ from LF Git-blob hashes; neither convention is silently substituted.
- The verifier's first preflight failed because it initially compared raw CRLF checkout bytes with LF Git blobs. No snapshots were written in that failed attempt. Corrected only the evidence verifier to compare Git checkout-filtered bytes and separately record canonical blob hashes; subsequent full generation/checks passed. This was EOL handling, not altered product/oracle data.

## Fresh measured results

All error/difference values below are computed from actual CLI outputs, not authored fixture numbers. Relative error is worst all-sample position distance divided by the existing characteristic scale, never pointwise division near zero.

| Template | Samples | Relative analytic error (limit 0.005) | Changed samples | Maximum old/new position distance, m |
|---|---:|---:|---:|---:|
| Free fall | 201 | 7.922080705786024e-15 | 0 | 0 |
| Projectile | 201 | 5.561909207513163e-15 | 0 | 0 |
| Ramp | 201 | 2.9784368547281638e-15 | 90 | 2.6020852139652106e-18 |
| Pendulum | 1001 | 1.460514219561413e-12 | 1000 | 1.3322495542273105e-05 |

Ramp maximum velocity-vector difference: `3.1031676915590914e-17 m/s`; pendulum: `7.622861298110407e-05 m/s`. Metadata, sample counts, step/time values remain equal. Ballistic snapshots remain byte-identical; no irrelevant EOL rewrite.

| Command / check | Result / evidence |
|---|---|
| `node --test --test-reporter=tap tests/lab/browser-simulator.test.mjs` before generation | Exit 1, **8 pass / 2 fail** at unchanged line29 snapshot assertion for ramp/pendulum, after actual current browser/engine/CLI equality. [browser-before.tap](../../../evidence/S10/consumer-recovery/browser-before.tap) |
| `python -B evidence/S10/consumer-recovery/regenerate.py` | Exit 0; four accepted S08 oracles, unchanged threshold, every sample, repeated actual CLI, all46 immutable hashes pass. [generation-run.txt](../../../evidence/S10/consumer-recovery/generation-run.txt) |
| Same unchanged browser suite after final generation | Exit 0, **10/10 pass**, zero skips/todos. [browser-after.tap](../../../evidence/S10/consumer-recovery/browser-after.tap) |
| Independent hash/readback and `git diff --name-only b37f7b8 -- Build contracts tests test-data evidence/S10/numerical-invariants evidence/S10/extension-replay evidence/S10/replay-invariants evidence/S10/replay-recovery` | PASS: protected diff empty, 46 immutable hashes equal, four snapshot hashes match actual CLI receipt, old transport branch preserved. [isolation-verification.json](../../../evidence/S10/consumer-recovery/isolation-verification.json) |
| Scoped staged diff/whitespace and timebox validation | Only Owns staged; authored files pass whitespace checking. Whole staged check flags four whitespace-only lines in the preserved raw failing TAP (lines24/27/52/55); no raw diagnostic rewriting. Timing validator PASS. [commit-check.txt](commit-check.txt). Parent integration/main merge remains separate. |

## Skips / risks / handoff

- **Not broad Gate P.** R15-numerics reports unchanged frozen invariants **15 pass / 2 fail**, both old nonlinear-energy controls conflicting with accepted small-angle linear dynamics. This is inherited report evidence, not a rerun or a claimed green suite here. Frozen suite, `validated-cases.json`, all thresholds and browser tests remain unchanged. Parent decides broader gate acceptance separately.
- Single authored synthetic input per template, short ballistic/ramp horizons and small-angle pendulum only; no exhaustive-domain/finite-angle/physical/contact assurance. Fixed-step binary64 phase/rounding and model-selector limitations remain.
- Skipped broad build/physics repeats, UI/IAB375 (parent serialized), native review, replay record migration, future features, fanout, Claude, installs/dependencies/network/model/GPU jobs, Gate M/S12, real scenes, deployments/publication/accounts/terms/auth/secrets/routing/quota/global policy. No owner decision needed within this scope.
- Communication: mandatory minimal skill update plus actionable generator finding/green consumer update; no optional chat recap, other-chat messages or fanout. Explicit Ponytail reminder applied without changing scope/timebox. Final response is a report pointer.
- Next: parent may accept/cherry-pick this scoped commit after reading fresh evidence. Do not infer replay hash continuity, physical readiness or broader gate completion.
