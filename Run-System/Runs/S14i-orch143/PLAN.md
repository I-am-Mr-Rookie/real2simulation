# S14i-orch143 PLAN

Objective: QUEUE S14i — API workspace analysis routers (internal-token auth, interview questions, spec validate, fit, HTML report) per evidence/S15/S15m/PLAN.md §2.
Lane CODEX-1 (army: Claude), anthropic/claude-opus-5-5/high. Issued 2026-10-30T11:40:47Z, deadline 12:10:47Z, cutoff 12:05:47Z. Base main 1235cca.

Owns: Build/api/workspace/__init__.py; Build/api/workspace/auth.py; Build/api/workspace/analysis.py; tests/api-workspace/test_analysis.py; evidence/S14i/; Run-System/Runs/S14i-orch143/.

Approach (Ponytail): one APIRouter, prefix /internal/workspace, router-level auth dependency; endpoints delegate to existing interview.questions / answers_to_spec(validate_setup) / fitter.api.handle / reports number_entry+render_html. No new numeric logic, no storage, no deps, no paid calls, no deploy. Mounting = S04m; scene store = S13i (injected resolver).
Checks: python -B -m unittest discover -s tests/api-workspace -t tests/api-workspace; tests/agent suite still green.
