# S15g-orch24 REPORT: virtual instrument controls
Status: DONE. Lane/model: CLAUDE, anthropic/claude-sonnet-5-5 high; OpenCodex-managed, not polled. Tokens/cost: unobservable.
UTC: issued 2026-10-29T15:03:51+00:00, work ended 2026-10-29T15:12:21+00:00, deadline 15:33:51 (Dhaka offset is +06:00 in the real calendar; the contract text equates them, receipt uses UTC). Branch run/S15g-orch24 (base main 3935c04), worktree .worktrees/S15g-orch24. Parent project 91e441f8-e40c-4ec4-bea2-de7fa1582d97. Not merged; canonical controls untouched.

## Result
Trial measurements show, for every row: value ± uncertainty unit, a `simulated` tag and `source: <instrument evidence>`. Instrument selector (stopwatch, light gate, ruler, camera), Take reading, status and trial list sit in the workspace panel; available after a finished run (`run.done`), read-only afterwards, cleared by a new run/cancel/spec edit/reset.

## Files (all inside Owns)
- New: Build/web/src/workspace/instruments.mjs, instrument-view.mjs; tests/workspace/instruments.test.mjs; tests/workspace/fixtures/instrument-readings.json; evidence/S15/instrument_fixtures.py, instrument-preview.html, instruments-375.png, instruments-375-trials.png, react-ssr-check-s15g.out.txt, workspace-tests-s15g.out.txt.
- Edited: workspace/view.mjs, react.mjs (one optional `instruments` prop), workspace.css (S15g block), README.md (S15g section), evidence/S15/react-ssr-check.mjs (S15g block).

## Evidence (fresh)
- `node --test tests/workspace/*.test.mjs`: 60/60 pass (6 new; includes the existing import-boundary test). Output: evidence/S15/workspace-tests-s15g.out.txt.
- `python evidence/S15/instrument_fixtures.py --check`: exit 0 (fixture equals current Build/instruments output); also run inside the new test.
- Real React 19.3.1 SSR check (`node evidence/S15/react-ssr-check.mjs <canonical node_modules>`): S15g line ok; earlier S15b-f checks still pass. Output: evidence/S15/react-ssr-check-s15g.out.txt.
- 375px visual check in the ChatGPT in-app browser only (not Chrome): viewport 375 wide, scrollWidth 360, zero overflowing elements in the instrument section; screenshots instruments-375*.png show three trials with values, uncertainty, units, simulated tag, source. Viewport reset and the temporary python http.server (127.0.0.1:8765, needed because the browser blocks file:) were stopped; server confirmed down.

## Reuse / smallest-complete choices (Ponytail full)
- Numbers: generated fixture from existing Build/instruments + contracts/fit/quantity; zero new numbers authored. Injected service keeps workspace free of Python/instrument imports (S15f pattern).
- Mirrors S15f structure (pure reducer + view + h-injected renderer, same-reference no-ops, CLEARS list); reused ws-chip/ws-submit/ws-actions/ws-hint CSS; hidden-key regex copied from S15a (not exported there, editing workflow.mjs is a larger change).
- Signed instrument `error` is deliberately dropped (hidden-truth leak); tested with a fixture whose error is non-zero.
- Skipped: trial cap, fit wiring of readings, persistence, i18n/number locale, instrument-settings UI (settings are caller-supplied calibration, not ours to pick), accepting the `measured` label (contract admits only `simulated`).
- Reverted the five older *-preview.html files that the SSR script regenerated (they embed CSS only; no content change).

## Limits / risks
- Fixture-first: SYNTHETIC settings/inputs (non-physical a=2 stand-in); no gate, real-scene, physical, calibrated or Gate P/A claim. Panel is not yet wired into the S04 page and has no real instrument transport.
- Display strips float noise with toPrecision(10) (e.g. 0.01666666667); uncertainty is the instrument-reported standard uncertainty, not a fit error.
- Fixture JSON round-trips Python floats; --check guards drift. The new test skips the python check if python is absent.
- Communication: silent workflow kept; one final line to controller chat.

## Next
Controller review/merge; S15h+ can feed these readings to S11 fit display; wire panel in S04 page (S06h/S15 leaves).
