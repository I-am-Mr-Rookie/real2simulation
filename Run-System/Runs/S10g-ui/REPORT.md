# S10g-ui report

## Result
DONE — corrected the UI to the exact agreed service fit envelope.

## Exact contract fix
- `parseFitReveal` now reads only `body.sessionId` and `body.fit`.
- It requires `body.fit.status === "ok"`, `fit.gravity.{value,unit,uncertainty,source}`, exact unit `m/s^2`, finite value/uncertainty, nonnegative uncertainty, `source.label === "simulated"`, and `fit.uncertainty.{model,assumptions}` with an array of strings.
- Removed the invented `actualS11response` wrapper and all permissive fit/value/magnitude/unit/source fallbacks from client parsing.
- The UI fit path now checks `body.fit.status` and reports `body.fit.error` when present.

## Checks
- `node --test tests/lab/ui-contract.test.mjs` — 4/4 pass, including exact valid shape, stale/malformed/error rejection, wrapper rejection, and plot behavior. Output: `evidence/S10/ui/ui-contract.txt`.
- `git diff --check` — pass.
- No server/build/deploy/auth/config changes.

## Parent handoff
- Parent service must provide the exact `{sessionId, fit}` body shape; browser verification remains parent-owned.
