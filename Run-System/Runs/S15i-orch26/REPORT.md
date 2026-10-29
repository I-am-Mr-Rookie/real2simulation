# S15i-orch26 REPORT
Status: DONE. Lane/model: anthropic/claude-sonnet-5-5 medium; OpenCodex-managed; not polled. Start 2026-10-29T15:29:12+00:00, end 2026-10-29T15:35:03+00:00.
Tokens/cost: unobservable.

## Result
- `Build/web/src/workspace/navigation.mjs` (new): pure sidebar model, report parser/view, render fns. Wired opt-in into `view.mjs`/`react.mjs` (`navigate`, `report` props) and `workspace.css` (empty "side" grid row).
- `tests/workspace/navigation.test.mjs` (new, 9 tests), `evidence/S15/report_fixtures.py`, `nav-ssr-check.mjs`, `nav-preview.html`, `nav-375-frame.html`, `react-ssr-check-s15i.out.txt`; README section.
- Fixtures only; every number in the report is copied from fitter output (label simulated). No gate, real-scene or physical claim.

## Checks (fresh)
- `node --test tests/workspace/*.test.mjs`: 75/75 pass (66 prior + 9 new), including existing import-boundary test and the slot test (sidebar uses `data-nav`, not `data-slot`, so SLOTS stay fixed).
- `python evidence/S15/report_fixtures.py --check`: fixture equals current `Build.reports.number_entry`/`validate_report` output.
- React 19.3.1 SSR through `createWorkspace`: ok. 375px check in the ChatGPT in-app browser: sidebar shows between stage rail and viewport, report text readable, no horizontal overflow seen. First pass exposed two bugs, fixed: sidebar had no grid area (rendered off-position), and dimensionless unit "1" printed as "8 1 (simulated)". Server I started was stopped; tab closed. Screenshot PNG not saved to disk (no file API from the browser tool); preview HTML is.

## Ponytail choices
Reused: S15a reducer events (`availableEvents`, REPORT_OPEN/CLOSE, EDIT_SPEC, RESET), `interviewView`, `STAGES`, existing fixtures and generator pattern, existing `renderWorkspace` positional params. Skipped: report tables/charts/PDF, dependency, new state slice, URL routing, digest recompute in JS. Smallest-change: sidebar is derived from state, no new reducer state.

## Findings for owning lanes
- S17 (Build/reports): no JSON transport/schema file for `r2s.report/1` or for rendered tables/charts; the JS mirror is hand-written and may drift. Suggest a `contracts/report/*.schema.json`.
- S14 (Build/agent): no change needed; its contract already feeds `parseQuestions`.
- Shortcut: prose number-word check (e.g. "nine") is not mirrored in JS; server validate_report is authority.

## Risks / not verified
Host wiring (S04) not done; destructive RESET/EDIT_SPEC has no confirm dialog (host should confirm on `destructive`). Communication compliance: silent apart from this report.
