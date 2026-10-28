# S10g-ui report

## Result
DONE — implemented the requested UI inspection fixes on `run/S10g-ui`.

## Fixes
- Added `Build/web/src/lab/fit-contract.mjs`, a strict actual-S11 parser. Reveal requires `status: ok`, matching session ID, finite gravity value, nonnegative finite gravity uncertainty, nonempty unit, `source.label === "simulated"`, source evidence, and `{model, assumptions}` uncertainty metadata. No fallback to arbitrary value/magnitude/default source or unit.
- Updated `LabClient.jsx` to reveal only parsed actual-S11 fit data, preserve uncertainty/source evidence, and guard stale/aborted errors before setting error state.
- Reset Mystery-g when switching to ramp/pendulum; corrected ramp description to `Sliding motion`; fixed result headings for all four templates.
- Added pure `plotPoints` helper using finite observed time/position domains, including negative and degenerate values; SVG now uses declared response units and no authored physics scaling/clipping.
- Added behavioral tests for valid/invalid/stale fit responses and plot scaling.

## Checks
- `node --test tests/lab/ui-contract.test.mjs` — 4/4 pass. Output: `evidence/S10/ui/ui-contract.txt`.
- `git diff --check` — pass.
- No shared shell/layout/style/auth/API files changed; no dependency, build, browser, server, job, spend, deploy, auth, upload, or policy changes.

## Ponytail reuse and skips
- Reused the existing client fetch flow and public shell; added only the approved helper inside `Build/web/src/lab/`.
- Skipped heavy Next build/live browser verification because `Build/web/node_modules` is absent and parent owns service/browser integration.

## Risk / parent handoff
- Parent must verify the service emits the known `actualS11response.fit.gravity` shape and run the four-template browser check after service integration.
