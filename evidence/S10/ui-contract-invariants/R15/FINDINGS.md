# R15 UI contract audit — bounded result

Audited base `74c886f9b2cc1322dde152f5be5813f813904bc6`. No product edits. No current producer-reachable P0–P2 UI defect demonstrated in the assigned cases. This is not a general release, security, fitter-accuracy or gate decision.

## Reachability matters

The UI start handler trusts successful local-service envelopes; it is not a general arbitrary-JSON validator. `handleLab` accepts only action/template/mystery for start and action/sessionId for fit. It does not accept caller observations, fitted metadata or arbitrary setups. Its fixed Python bridge uses authored regression templates: 0.2s/0.001s for free-fall/projectile/ramp, 1s/0.001s for pendulum; normal gravity 9.81 and Mystery gravity in [4,16). These are synthetic setup facts, not measured physical quantities.

The bridge rejects nonfinite observations, returns JSON, caps samples at 2000; the service checks finite observation rows and size before returning them. Actual tested envelopes contained 201 observations for ballistic/ramp and 1001 for pendulum. UI chart kept all points; table stayed at most nine rows. All four normal browser traces were finite, simulated/synthetic, and matched the producer sample count. Existing tests additionally cover accepted fixture equality and the 2000/2001 boundary.

## Frozen inherited counterexamples (latent P3 each)

| Case and expected oracle | Fresh observed result | Why not a present release blocker |
|---|---|---|
| Explicit `quantity_uncertainty: "95% confidence interval"` must not become a one-sigma reveal | `parseFitReveal` accepts it | Actual fitter hardcodes `standard uncertainty (one sigma), not a 95% interval`; no user metadata input to this path. Revisit if fitter response schema/producer changes. |
| In-memory `assumptions = Array(1)` should reject | `.some` skips the hole, parser accepts | JSON serializes the hole to `null`; actual wire-form parser rejects it. Actual producer assumptions are dense strings. |
| Rows `(-1e308,-1e308)` and `(1e308,1e308)` should yield finite endpoint coordinates `24,190 616,30` | `24,190 NaN,NaN` from overflowing subtraction/span | Fixed producer values cannot approach these magnitudes. Revisit before accepting arbitrary observation ranges. |
| 200000 finite rows should not escape as an argument-stack error | `RangeError: Maximum call stack size exceeded` | Both server and browser paths cap at 2000. The all-points contract remains unchanged; no silent truncation was added. |

These four expected assertions remain unchanged and deliberately fail. No TODO/skip/xfail annotations, tolerance changes, expected-value weakening or product fixes hide them. `prior-R14/r14-ui-invariants.test.mjs` is the original unfinished oracle; `inherited-frozen-oracle.tap` is a fresh R15 reproduction, not an R14 completion receipt. Root-level pre-existing evidence is preserved unchanged and remains historical.

## Successful current-path checks

- Actual local service → JSON roundtrip → extracted exact run/fit handler bodies for four normal and two ballistic Mystery envelopes. This tests real service envelopes, not a live HTTP server or React rendering.
- Actual accepted artifact fixtures/engine through existing tests. Units, simulated provenance, one-sigma metadata, unsupported-fit labels and separate world-Y/downward-displacement wording checked.
- Missing/wrong session ID rejected before a fit is committed. Existing tests cover late fetch success/failure; R15 adds late JSON success/failure after both abort and request-version invalidation, for both handlers.
- Malformed/nonfinite observations filtered without coercion; sparse/invalid browser origin vectors rejected unchanged. Caller-injected observations/fit metadata rejected at the service entry point.
- Browser handler clears success/error appropriately and exposes sanitized failure text; payload-reference reset is a source assertion, not a React rerender assertion.

## Fresh results and reproducible commands

Run from the assigned worktree:

```powershell
node --test --test-reporter=tap --test-name-pattern=R15 tests/lab/r14-ui-invariants.test.mjs
# current-envelope-tests.tap: 10 tests pass, 0 fail (includes six envelope subtests)
node --test --test-reporter=tap tests/lab/ui-contract.test.mjs tests/lab/browser-simulator.test.mjs
# existing-focused-tests.tap: 19 pass, 0 fail
node --test --test-reporter=tap tests/lab/ui-contract.test.mjs tests/lab/browser-simulator.test.mjs tests/lab/r14-ui-invariants.test.mjs
# final-audit-tests.tap: 35 pass, 4 expected latent failures; exit 1, NOT an all-green suite
```

An initial R15 test incorrectly expected 2000 free-fall samples at a longer horizon; the engine correctly stopped at its declared drop plane after 453 samples. That redundant test was removed, not used as a product finding. Existing browser tests already use the accepted pendulum fixture for a real 2000-sample horizon. Initial output is retained in `initial-envelope-tests-with-test-error.tap`; no inherited expected oracle was changed.

## Skips and risks

No browser/375px/mobile/accessibility interaction, React mount/rerender, live HTTP or end-to-end deployment exercised. No independent Mystery auth/privacy audit; only assigned public envelope/fit-consumption contract. No numerical accuracy, fitter accuracy, physical/calibration/Gate M/S12 or broad simulator regression claim. No new dependency, GPU, external model, network publication or shared control changes. A future arbitrary-data UI or producer change must address/reassess the four latent cases before treating these helpers as general-purpose boundary validation.
