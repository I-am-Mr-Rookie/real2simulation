# R16-ui-oracle — DONE (bounded audit only; product NOT green)

## Result / handoff

Independent immutable oracle frozen at **`a79e135ae9e0702d679d3bad2351052651543666`**, parent verified main **`9eece4239d47ece4600f3fff7f2e38b78403cb02`**, branch `run/R16-ui-oracle`; no repair implementation inspected/copied. Only new test, own evidence and own run folder changed. No merge/main/control/fixture/schema/product/frozen-test edits. Old branch/history/ignored reports retained.

- Test: `tests/lab/ui-helper-oracle.test.mjs` (Git blob `fa9eba92e001c565c3ae53fcd35c54a89572a065`).
- [Expected semantics and exact pin/hash](../../../evidence/S10/ui-helper-oracle/EXPECTED-SEMANTICS.md).
- [Full base oracle TAP](../../../evidence/S10/ui-helper-oracle/base-oracle.tap): **23 tests, 14 PASS / 9 expected FAIL**, exit 1. Four known latent P3 groups: extreme finite span (4 tests), spread argument ceiling (1), contradictory explicit uncertainty metadata (3), sparse assumptions (1).
- [Unchanged existing UI suite](../../../evidence/S10/ui-helper-oracle/base-existing-ui.tap): **9/9 PASS**, exit 0.
- [Independent positive controls](../../../evidence/S10/ui-helper-oracle/base-positive-controls.tap): **3/3 PASS**, exit 0; dyadic proof, real producer, minimal DTO compatibility. This is a deliberately selected positive control, NOT a repair-green claim.
- [Actual offline producer snapshot](../../../evidence/S10/ui-helper-oracle/actual-producer-fit.json); only status/sessionId envelope is authored in the test, fit values/metadata come from the actual bridge/fitter. No hand-authored numerical success evidence.
- [Source/frozen-test preservation](../../../evidence/S10/ui-helper-oracle/protected-source-hashes.json), [verification/runtime manifest](../../../evidence/S10/ui-helper-oracle/verification.json), empty `protected-diff.txt`, initial 21-case TAP retained. Node v24.18.0, Python 3.14.5.

## Exact semantics / checks

Binary64 inputs are decoded independently to BigInt integer multiples of 2^-1074. Cross multiplication proves endpoint/midpoint/quarter spacing exactly, including +/-MAX_VALUE, overflowing +/-2^1023 spans, neighboring huge positives/negatives, subnormals and the normal boundary. Expected coordinates are literal algebraic pixels, not a copy of the floating implementation; **no tolerance**. Independent axes, custom finite extents, degenerate axes, shuffled duplicates, preserved point count, bounded 131073-row helper list and input immutability covered. Producer max samples not changed.

Real one-sigma metadata accepted unchanged; explicit contradictory meanings must reject instead of displaying the UI's one-sigma label. Established minimal DTO remains accepted without new mandatory metadata/covariance keys. Sparse arrays do not satisfy the existing string-assumption contract; no general security audit or schema rewrite.

Commands (from worktree): `node --check tests/lab/ui-helper-oracle.test.mjs`; `node --test --test-reporter=tap tests/lab/ui-helper-oracle.test.mjs`; `node --test --test-reporter=tap tests/lab/ui-contract.test.mjs`; named positive-control run recorded in evidence. Actual producer capture uses Python `-B`, existing `runpy` bridge handle, start free_fall then fit. Git source-blob comparison and `git diff 9eece42 -- Build contracts tests/lab/ui-contract.test.mjs` verify preservation. Timing validator receipt is saved beside this report.

## Authority / timing / cost

Issue **2026-10-29T07:58:39Z**; minute25 cutoff **08:23:39Z**; deadline **08:28:39Z / 14:28:39 Dhaka**. First observed tool clock **07:58:57Z**, initial inspection already underway. Actual work-stop/report timestamps are in [TIMEBOX.json](TIMEBOX.json); full 1800-second window retained, verified bounded DONE early, no early incomplete exception or idle padding. Owner extension through **10:00Z / 16:00 Dhaka** not crossed.

Assigned managed **gpt-6.1-sol/medium**; independent runtime identity/effort attestation unavailable. **OpenCodex-managed; not polled. Tokens/cost unknown.** No provider/model/credential/policy changes, capacity error or retries. Local CPU checks only; no paid/API/GPU job, native/IAB, production build, deployment or other-chat message. Parent Meta AI Hackathon **`91e441f8-e40c-4ec4-bea2-de7fa1582d97`**, canonical owner root inherited; no independent child UI binding claim.

## Ponytail full/default applied / limitations

Read requested installed skill at `C:/Users/HP/.codex/.tmp/marketplaces/ponytail/skills/ponytail/SKILL.md`. **Reuse:** Node test/assert/child_process, public helper exports and actual Python bridge/fitter; no dependencies. **Smallest complete change:** one test file plus evidence, exact table expectations and tiny dyadic input-proof helper; no repair abstraction or product edit. **Fresh checks:** full red oracle, positive controls, existing green UI suite, syntax, source hashes, Git scope and timebox. No expected assertion weakened; the second run only added the other two known P3 controls.

**Skipped:** repair implementation, broad fuzz/security audit, browser/render/HTTP checks, heavy builds and physical/calibration/real-scene validation. **Risks:** base helper counterexamples remain unresolved; huge lists and sparse arrays are outside the current bounded JSON producer, and producer acceptance is not an arbitrary-data safety claim. No product/gate pass, physical Gate M/S12 relaxation, paid GPU, publication/accounts/terms/credentials authority implied. Controller must review immutable tests/semantics and separately test a repair before acceptance; no owned implementation work remains.

Evidence and report on disk. No owner question required. Silent except mandatory higher-priority Ponytail/tool-work notice; final memory citation is another higher-priority formatting exception. No duplicated chat report or other-chat communication.
