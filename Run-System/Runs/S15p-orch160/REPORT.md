# S15p-orch160 REPORT — DONE (structural gap outside Owns, see below)

Lane CLAUDE; model anthropic/claude-opus-5-5 medium; coding quota OpenCodex-managed; not polled. Tokens/cost: unknown (unobservable). UTC start 2026-10-30T20:23:48Z, end 2026-10-30T20:33:13+00:00.
Branch run/S15p-orch160 from main 6cd7bc9; code commit bd3c05d.

## Changes
- controller.mjs: `browserSimulate(runSim)` = `runSim({mode:'normal', validatedSetup})` with the API validated_setup verbatim; samples -> `{time_s, position_m: position_m[1]}` (same mapping as lab BrowserSimulation.jsx). Simulator throw -> RUN_FAIL with its message; reducer labels run 'simulated'.
- /fit shape mismatch (S15n note) confirmed and fixed in controller: API (fitter.api.fit_observations) rejects unknown fields, wants `{times, positions}` quantity lists, returns top-level `gravity`/`uncertainty` without sessionId. Controller sends quantity lists (uncertainty 0 = exact simulated engine value, label simulated) and re-envelopes the response for the unchanged parseFitReveal gate (`revealBody`; numbers copied, never computed; no gravity or legacy shape -> fit.failed). Raw API fit kept (`fitRaw`) and sent to /report, which needs the raw fitter result (before: parsed reveal -> 422).
- Spec label: top-level `label` or `validated_setup.label` of the spec response (S14j not merged; field name assumed) kept as `specLabel`; shown in a SIMULATED note during run/fit/report and in the report.
- navigation.mjs: reportView accepts `{status:'html-print-fallback', labels, html}`; renderReport shows labels, spec label and the server html only in `<iframe sandbox="" srcDoc>` (no scripts, opaque origin). r2s.report/1 path unchanged.
- PrivateWorkspace.mjs: injects `simulate: browserSimulate(runBrowserSimulation)`; instruments note + I_MEASURE failure text "Instruments are not available in this build; no reading is shown."
- Tests: controller.test.mjs uses the real API fit shape (request keys, raw fit to report, specLabel), legacy envelope and gravity-null rejected; real runBrowserSimulation fails closed on a bare spec; sandboxed-iframe report test. private-workspace test asserts instruments text.

## Checks (fresh)
- `node --test "tests/workspace/*.test.mjs" "tests/shell-workspace/*.test.mjs"`: 91/91 pass.
- `node --test "tests/web-private/*.test.mjs" "tests/web-workspace-api/*.test.mjs"`: 15/15 pass.
- `npm run build` (Build/web; node_modules junction to canonical, removed afterwards): exit 0.
- Railway DEV web deployment e6bf5fe2-6013-42a6-9337-33888fcc9a1e SUCCESS; logged-out 401/404/404/200 unchanged. Evidence: evidence/S15p/DEPLOY.md.

## Structural gap (next action, outside Owns)
API `POST scenes/{id}/spec` returns `validated_setup = validate_setup(spec)` = the bare spec. runBrowserSimulation requires the S10 validated artifact (`artifact_version 's10-validated-setup-v1'`, validation, producer, spec, scene with `synthetic: true`). Those envelope fields are trust labels and were NOT forged client-side. So on dev, Run shows an honest run.failed ("INVALID_BROWSER_SIMULATION: untrusted validated artifact") for every scene; recorded RM04 scenes are also non-synthetic, which the simulator rejects. Fix belongs in Build/api/workspace/analysis.py (return the artifact) plus a controller/owner decision on the simulator's synthetic-only rule. S15o will hit this.

## Ponytail
Reused runBrowserSimulation, the lab sample->observation mapping, parseFitReveal gate, reducer labels and the I_FAIL path. Smallest change: 3 small exported helpers in controller, one branch each in reportView/renderReport, 3 lines in host. Skipped: instrument service, API changes, new fixtures, browser walk (S15o). Risks: specLabel field name assumed until S14j merges; uncertainty 0 on simulated points means fit sigma comes from the residual floor only.

Communication: silent; one completion message to controller. Temp stage dir left in %TEMP% (s15p-stage-4ad3fd36).
