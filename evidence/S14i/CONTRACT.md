# S14i — /internal/workspace analysis routes (as built)

Module: `Build/api/workspace/analysis.py` `create_router(scenes=resolver)` -> FastAPI APIRouter, prefix `/internal/workspace`.
Mount (S04m): `app.include_router(create_router(<S13i scene resolver>))`. Not mounted or deployed by S14i.

Auth (`auth.require_owner`, router-level): `x-workspace-token` must equal env `WORKSPACE_INTERNAL_TOKEN` (hmac.compare_digest; unset env fails closed); `x-workspace-owner` required, `[A-Za-z0-9_-]{1,128}`. Else 401.
Error body (all routes): FastAPI `{"detail": {"code": UNAUTHORIZED|NOT_FOUND|INVALID_INPUT, "message": str, ...}}`. Malformed/missing JSON body -> FastAPI default 422 (`detail` is a list, no `code`).

| Route | Body | 200 | Errors |
|---|---|---|---|
| GET scenes/{id}/questions | — | `interview.questions(id, base_spec.template)` | 404 NOT_FOUND (unknown/other owner/bad id) |
| POST scenes/{id}/spec | {answers} | {ok:true, spec, validated_setup} (same validate_setup output) | 404; 422 detail {ok:false, code INVALID_INPUT, errors[]} |
| POST fit | fitter request | `fitter.api.handle` output (status ok) | 422 detail {code INVALID_INPUT, error:{code}} |
| POST report | {spec:{template}, fit: ok fitter result} | {status:"html-print-fallback", labels:["simulated"], fitter_digest, html} | 422 (bad template, non-ok fit, fit without gravity e.g. degree 1) |

Scene resolver: `(owner, scene_id) -> (base_spec, scene, scene_root) | None`. Default returns None (no store until S13i) so questions/spec are 404 until S13i injects one.
Report numbers: `reports.number_entry` from the fit (g, rmse, n); prose is number-free; labels derived from the fitter's own source labels.
Tests: tests/api-workspace/test_analysis.py (7 OK, test-output.txt). SYNTHETIC S08/instrument fixtures only; not real-scene/physical evidence.
