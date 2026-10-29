# S17a-orch14 REPORT
Status: DONE. Lane CLAUDE, anthropic/claude-sonnet-5-5 / high (OpenCodex-managed; not polled). Started 2026-10-29T11:22:12Z, work stopped 2026-10-29T11:27:21+00:00 (every acceptance criterion verified; early finish allowed for verified DONE). Tokens/cost: unobservable.
Branch run/S17a-orch14 (worktree .worktrees/S17a-orch14), not merged; controller integrates.

## Delivered
- [contract.py](Build/reports/contract.py), [CONTRACT.md](Build/reports/CONTRACT.md): schema `r2s.report/1`. Narrative holds no numerals/number words/fractions, only `{{id}}` placeholders; `numbers[id]` entries carry `path`; `validate_report(report, fitter_result)` re-resolves each path in the fitter output and requires exact value (incl. int/float type), fitter-derived unit and fitter source label, plus `fitter_digest` pin. Closed list of reportable paths; closed field sets everywhere; template in {free_fall, pendulum, projectile, ramp}.
- [fixture.py](tests/reports/fixture.py): visibly synthetic fitter result via existing `Build.fitter.api.handle` + `Build.instruments.synthetic`; evidence in [evidence/S17/](evidence/S17/) (synthetic_fitter_result.json, synthetic_report.json, test-contract.txt).

## Checks (fresh)
- `python -m unittest tests.reports.test_contract`: 11/11 OK. Rejection proofs: altered/boolean/NaN/string/int-vs-float value, entry without path, digits/number words/½/²/Arabic-Indic digits in prose, unresolved or malformed placeholder, unit/label/uncertainty tampering, label upgrade, stale fitter digest, extra fields, unknown template, non-reportable paths, error/incomplete fitter results, non-finite fitter values. Acceptance for all 4 templates.
- Regression: `tests.fitter.test_api` + `test_core` 22/22 OK (no fitter files touched).

## Ponytail choices
Reused `handle()`, synthetic instruments, existing unittest style and the S11 unit/label conventions (units and labels are read from fitter output, not retyped). No new dependency, no schema library, no renderer (S17b+). Skipped: fit.coefficients (unit/order not asserted by fitter), multi-fitter-result reports, number-word check beyond English.

## Risks / limits
Trust boundary is the caller supplying the genuine fitter result; S17e must re-run the fitter and diff. Fixture-only: no gate, real-scene or physical evidence claimed; all labels "simulated". Communication compliance: silent; one final line to controller.

