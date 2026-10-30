# S15k-fixture-orch83 REPORT — PARTIAL
Lane/model: CLAUDE, anthropic/claude-sonnet-5-5 high (OpenCodex-managed; not polled). Start 2026-10-30T05:47:24Z (worktree + reads from ~05:51Z); work stopped 2026-10-30T06:13:43Z.
Branch run/S15k-fixture-orch83 (worktree .worktrees/S15k-fixture-orch83), from main dc74261 (+ staged control files left untouched in canonical).

## Result
**PARTIAL.** Fixture walk through all 7 stages passes at model + React-SSR level. NOT walked: the real browser on a local dev server, and the live S14 interview. All data is FIXTURE (synthetic job; recorded Python/Build outputs); nothing here is live S14, deployed, gate, real-scene or physical evidence.

## Step outcomes (evidence/S15/walk-steps.json, walk-check.out.txt; ms = this machine, single run)
| # | Step | Mode | End phase | ms | Error |
|---|---|---|---|---|---|
| 1 | upload | FIXTURE synthetic job | interview.active | 677 | none |
| 2 | interview (3 questions: chip, free text, chip+text) | FIXTURE recorded agent response; S14 live PENDING | interview.active (answers complete) | 126 | none |
| 3 | template/spec | FIXTURE recorded real Python validate_setup verdict | run.ready | 146 | none |
| 4 | run (seeded replay) | FIXTURE deterministic runner + real Build/simulator replay record | run.done | 382 | none |
| 5 | instruments | FIXTURE recorded readings (select only) | run.done | 570 | none |
| 6 | fit | synthetic S11 reveal (reducer) + recorded REAL fitter output (panel) | fit.done | 461 | none |
| 7 | report | FIXTURE recorded Build.reports output | report.open | 632 | none |
Timings include first-import/JIT cost; not performance evidence.

## Findings
1. **Dev-server walk blocked (outside Owns):** `Build/web/src/app/(private)/layout.jsx` calls notFound() and `workspace/[sceneId]/page.jsx` returns null after the auth guard, so the workspace is not mounted in the app at all (S04-owned, intentionally fail-closed until the private repository is integration-reviewed). A browser walk of the real route is therefore impossible today; no auth/deploy changes made.
2. **In-app browser blocked for local files:** opening the static preview via file:// was rejected by browser URL policy (http/https only). I did not work around it (no ad-hoc server). Responsive/desktop browser behaviour of this walk is UNVERIFIED; per-stage 375px evidence from S15b-j still stands.
3. **Two fit contracts, no adapter (real gap):** `parseFitReveal` (S11, required by the reducer's FIT_RESULT) returns null for real Build/fitter output (what the fit panel renders). Host/S12-S14 integration must supply a lawful mapping/session-reveal path; I did not invent one (numbers must come only from fitter/simulator). Pinned by a test so a contract change is noticed.
4. Reducer needs an injected `validateSpec`; fixtures.deps only accepts `{synthetic:true}`, so the real accepted spec is rejected unless the host wraps the S08 verdict (walk does this by identity with the accepted spec). The real wiring is S14/host work.
5. No workspace defect found in Owns, so no source fix was made.

## Files
- evidence/S15/walk-check.mjs (SSR walk; usage: node evidence/S15/walk-check.mjs <Build/web/node_modules>), walk-steps.json, walk-check.out.txt, walk-preview.html (static, all stages)
- tests/workspace/walk.test.mjs (model-level full walk + gap pin)
- evidence/S15/workspace-tests-s15k.out.txt: node --test tests/workspace/*.test.mjs = 78 tests, 78 pass, 0 fail (previous 77 + 1)

## Ponytail (full) application
Reused: existing reducers/views/fixtures/recorded verdicts, React from canonical node_modules (no installs), the established react-ssr-check pattern; one new script + one test; no new abstractions. Skipped: no workflow code change (no defect), no ad-hoc http server/dev-server hacks, no screenshots. Risks: SSR walk does not exercise event handlers or the real viewer; instruments step is select-only; spec validator is a test double.

## Remaining / next
- S14 live interview integration, fit-reveal adapter (finding 3), mounting the workspace route (S04) and an in-app-browser walk over http on a dev server -> then S15k can be DONE.
- Communication compliance: silent except one completion message to the controller chat.
- Tokens/cost: unobservable.
