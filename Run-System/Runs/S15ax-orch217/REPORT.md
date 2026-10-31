# S15ax-orch217 REPORT: Result chart to the main stage

- Status: DONE. Lane CLAUDE, model anthropic/claude-opus-5-5 high (OpenCodex-managed; not polled). Tokens/cost: unknown (not observable). No GPU, no deploy.
- UTC: issued 2026-10-31T14:27:20Z, work 14:28 to ~14:40, deadline 14:57:20Z. Branch run/S15ax-orch217 from main e8ccfc48.

## What changed
- Build/web/src/workspace/view.mjs: at phase report.owner with a measurement, renderResultChart() output is placed in the viewport section (data-hero="result", aria-label "Clip result chart"); the empty viewer host is hidden by CSS and its status line becomes sr-only (still announced). renderMeasurement(h, m, chart) skips the chart in that case, so the side card is text only: clip/label line, g value, Source, caveat (carries the verdict), scale, user scale. Abstain / no series: no hero, viewport unchanged.
- Build/web/src/workspace/result-chart.mjs: same resultChart() geometry with axis gutters (viewBox 640x360, L120 T32 R24 B48). Ticks at three series points (first, last fit-prefix, last), labels with units ("0.1 s", "443 px"); values are the API series numbers, rounded for display only (t to 3 dp, y to integer px). Axes, dotted grid, split line with "held out" label. Ticks are aria-hidden; desc + data table keep the full numbers.
- Build/web/src/workspace/workspace.css (appended S15ax block): hero card (surface, border, shadow token), tick text in --ws-mono, band now --ws-chart-2 fill .28 + 1px edge (was faint --ws-chart-3), legend with CSS swatches (half-filled dot, solid, dashed, band), tick font bumped in user units in side cards and at <=520 px so labels stay ~11 px at 375. Theme tokens only; static SVG, no motion (reduced motion: nothing to disable).
- tests/workspace/result-chart.test.mjs: +2 tests (ticks come from series points with units and lie in the plot; hero in viewport, no svg in the panel, single ws-rc-t id, side card keeps g + caveat, OWN01 FAIL in the stage, abstain = no hero).
- evidence/S15ax/: static_render.mjs (S15aw script, label changed), FIXTURE HTML for OWN05/OWN01 x 6 themes, PNGs: OWN05 paper/light/dark/midnight/graphite/contrast at 1280, OWN05 dark + paper at 375 (true 375 px iframe via frame-*.html; Chrome headless min window 500), OWN01 dark at 1280 (FAIL in danger colour), npm-build.log.

## Checks (fresh)
- node --test tests/workspace/*.test.mjs tests/web-workspace-api/*.test.mjs tests/web-private/*.test.mjs: 146/146 pass (was 144 + 2 new).
- npm run build (Build/web, node_modules junction to canonical): exit 0, "Compiled successfully" (evidence/S15ax/npm-build.log), run after the last source edit.
- Looked at: OWN05 dark/paper/light/midnight/graphite/contrast 1280, OWN05 dark/paper 375, OWN01 dark 1280. Chart is the hero; legend readable; split marker labelled; band visible near the prediction end; 375 stacks chart > side card > job with no horizontal overflow seen.
- Labels verbatim: RECORDED, SIMULATED, MEASURED, Scale unverified, held-out wording, PASS/FAIL unchanged; no em dash in chart/view text (existing test).

## Ponytail (full)
- Reuse: resultChart()/renderResultChart() kept and moved, not rewritten; existing r2s-sr class for the hidden status; theme tokens; S15aw static_render.mjs and fixtures copied.
- Smallest complete: one boolean param on renderMeasurement, one hero const in renderWorkspace, CSS-only sizing; no chart library, no dependency, no new component.
- Skipped: round-number "nice" ticks (would invent numbers), a separate narrow-screen geometry, a visible heading over the chart (svg title + panel heading already name it), myfront font changes (house fonts kept; only restrained two-shade + accent chart per myfront).

## Myfront
- Applied as restraint: two shades + one accent chart, mono ticks, house card/shadow tokens, legend swatches finished; no restyle of working parts.

## Risks / limits
- FIXTURE static SSR only; not checked in the live DEV app (controller deploys). Viewer host is hidden (not unmounted) at report.owner; if a future owner clip ever has a scene, hero logic needs a scene check.
- 375 px tick text is ~11 px; band for OWN01 is thin because sigma is 2 px (true data).
- Communication: silent; one completion message to controller as authorized.
