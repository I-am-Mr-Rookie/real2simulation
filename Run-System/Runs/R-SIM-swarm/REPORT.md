# R-SIM-swarm review run report

- Status: **DONE** — independent review complete; not parent gate/product acceptance.
- RID/timebox: issued 2026-10-28T17:23:55Z; stopped/reported 2026-10-28T17:28:30Z; deadline 2026-10-28T17:53:55Z; minute25 17:48:55Z. TIMEBOX.json records the bounded early completion.
- Lane/model: CODEX-1 GPT-6.1 Sol medium requested; exact backend/tokens unavailable. OpenCodex-managed; not polled.
- Owns only `evidence/reviews/R-SIM-swarm/` and `Run-System/Runs/R-SIM-swarm/`; no peer source/control edits.

## Reviewed peer heads

- Simulator `eb24f12a66397a2bd79858c8028841c6353f97b2`
- Instruments `ef570b63ca12c6bd34bb54ca66aadbe7ae179eef`
- Fitter `bc6a7ac197a71ea30842e571b4c3124048881eef`

## Changes/evidence

- Added `evidence/reviews/R-SIM-swarm/REVIEW.md` with precise findings, file/line references, setup, scope and limitations.
- Added executable `repro_fitter_findings.py`.
- Findings: P1 raw `OverflowError` escapes fitter public `FitError` boundary on finite huge inputs; P2 non-zero RSS is incorrectly treated as exact (`AIC=-inf`) by an absolute epsilon threshold. Both reproduced against the current fitter head.

## Fresh checks

- Simulator `node --test tests/simulator/simulator.test.mjs`: 3/3 pass.
- Instruments `python -m unittest discover -s tests/instruments`: 9/9 pass.
- Fitter `python -m unittest discover -s tests/fitter`: 10/10 pass; independent repros expose P1/P2.
- `git diff --check`: pass.

## Ponytail choices

Applied full Ponytail: reused existing dependency-free ESM/Python seams and test conventions; made the smallest review-only evidence change; no source rewrite, dependency, framework, external API, model/media/job or speculative fix. Kept implementation ownership with peers and separated clean tests from actionable defects.

## Limits / skips

No peer edits, merge, shared-controls update, credentials, auth, paid job, model/checkpoint download, deployment, publication, live/browser/hardware check, or gate claim. Findings are local numeric-contract review only; parent controller must relay/fix and re-review.

## Communication compliance

Silent workflow followed; no cross-chat message needed. Final output is the single required pointer line.

## Continuation re-review (17:34Z)

Controller requested review remain open while corrections were active. Re-read actual peer heads and reran only boundary-focused checks. Simulator final committed head remains `eb24f12a66397a2bd79858c8028841c6353f97b2`: S08 export adapter, exact producer/schema boundary, sparse-state and zero-step guards pass 3/3. Instruments final committed head remains `ef570b63ca12c6bd34bb54ca66aadbe7ae179eef`: source/evidence, uncertainty, total-error separation and overflow/boolean guards pass 9/9.

Final committed heads were re-reviewed: simulator `e16810e4de1ff5e2e4d14f370995a07442ae12c1`, instruments `f261e91dcef7d1fa74652847e433352e94b55057`, fitter `57027a3eff25d3f0bf7c8f966c2e9cfa45f71f5b`. Fresh simulator unit 3/3, actual S08 adapter 2/2, instruments 10/10, and fitter 11/11 passed. Independent fitter repros now show huge finite input -> FitError and nonzero RSS -> finite AIC. Simulator recursive freeze/sparse guards and instrument unit/source/error/mutability changes were verified. No source edits made by this reviewer; no API/trajectory peer was complete/available in this review window.
