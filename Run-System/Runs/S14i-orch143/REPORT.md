# S14i-orch143 REPORT — DONE

Lane CODEX-1 (army: Claude); model anthropic/claude-opus-5-5/high (assigned); coding quota OpenCodex-managed; not polled. Tokens/cost: unknown (unobservable); paid calls $0.
UTC issued 2026-10-30T11:40:47Z; started ~11:41:47Z; work stopped 2026-10-30T11:48:21+00:00. Base main 1235cca. Branch run/S14i-orch143.

## Changed (Owns only)
- Build/api/workspace/__init__.py — package marker.
- Build/api/workspace/auth.py — `require_owner`: internal token (constant-time, fail-closed when unset) + owner header regex; `error()` helper.
- Build/api/workspace/analysis.py — `create_router(scenes)`: questions, spec, fit, report routes per S15m §2.
- tests/api-workspace/test_analysis.py — 7 TestClient tests.
- evidence/S14i/CONTRACT.md (as-built contract for S15n/S04n/S13i/S04m), evidence/S14i/test-output.txt.

## Acceptance
1. TestClient on APIRouter: missing/bad token 401, unset server token 401, owner header missing/invalid 401, fit/report also gated — PASS.
2. questions = `interview.questions`; spec = `interview.answers_to_spec` (S08c validate_setup); fit = `fitter.api.handle`; report = `reports.number_entry` + `typeset.render_html`. No new numeric logic; invalid answers -> 422 errors with no spec (never default numbers) — PASS (equality asserted against direct module calls).
3. Report response `status: html-print-fallback`, `labels: ["simulated"]` (derived from fitter source labels) — PASS.

## Fresh checks
- `python -B -m unittest discover -s tests/api-workspace -t tests/api-workspace` -> 7 OK.
- `python -B -m unittest discover -s tests/agent` -> 53 OK.
- Import probe: `modal`/`boto3` not loaded by analysis module (also asserted in test).

## Ponytail (applied)
- Reuse: every computation delegated to existing interview/validate_setup, fitter.api.handle, reports.number_entry/render_html/digest; html-print-fallback status mirrors reports/compile.py; fixtures reuse S08 `test_setup_validation.setup/BUNDLE` and the tests/reports instrument recipe.
- Smallest: one router, one dependency; FastAPI default HTTPException body instead of custom handlers (routers can't register them); auth reads env per request (no config object). Deleted the degree-1 report branch after the existing renderer proved it requires gravity -> honest 422.
- Shortcut (commented): default scene resolver returns None -> questions/spec 404 until S13i injects the owner-scoped store.
- Skipped: mounting in app.py/deploy (S04m), uploads/jobs/progress (S13i), jsonschema pin (S04m), PDF compile, rate limiting.

## Risks / limits
- questions/spec unusable in deployed app until S13i provides a resolver; questions route takes template from the resolved scene (not a query param) — S15n must call after a scene exists.
- Error body is `{"detail": {...}}`; FastAPI body-parse errors have list `detail` without `code` — S15n/S04n should map non-dict detail to INVALID_INPUT.
- Report rejects fits without gravity (degree 1): existing reports tables/charts require gravity.
- tests/reports suite not rerun (untouched; machine heavily loaded). No deploy, no paid call, no secret value read.

Communication: silent; one completion line to controller only.
