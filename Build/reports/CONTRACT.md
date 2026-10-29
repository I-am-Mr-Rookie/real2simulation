# Report data contract (S17a, schema `r2s.report/1`)

Fixture-first: validated only against visibly synthetic fitter output (`tests/reports/fixture.py`). It claims no gate, real-scene or physical evidence.

- A report is JSON with exactly: `schema, template, fitter_digest, title, sections, numbers`. `template` is one of free_fall, pendulum, projectile, ramp.
- Narrative (title, section titles, paragraphs) contains **no numerals, number words or fractions**. It may only cite numbers as `{{id}}` placeholders (ids: lowercase letters/underscore).
- `numbers[id]` = `{path, value, unit, label[, uncertainty_path, uncertainty]}`. Create with `number_entry(fitter_result, path, uncertainty_path)`; `validate_report(report, fitter_result)` re-resolves every entry and requires exact value (incl. int/float type), unit and source label from the fitter output. Labels are copied, never upgraded; the validator accepts `measured` only if the fitter says so.
- `fitter_digest` (sha256 of canonical fitter JSON) pins the report to one `status: "ok"` result of `Build.fitter.api.handle`.
- Reportable paths (closed list in `contract.py::_FIELDS`): `gravity.value|uncertainty`, `covariance.variance|standard_error`, `fit.rss|rmse|dof|n|rank`, `fit.fitted[i]|residuals[i]`, `uncertainty.residual_variance_floor`, `model_selection.aic[i]|selected_degree`. Anything else is rejected until a later leaf adds it with its unit rule.
- Limits: one fitter result per report; the trust boundary is the caller holding the real fitter output (S17e re-runs the fitter and diffs); the number-word check is English-only.
