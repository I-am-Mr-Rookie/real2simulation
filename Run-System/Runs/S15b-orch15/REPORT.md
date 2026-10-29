# S15b-orch15 — DONE

- Model: anthropic/claude-sonnet-5-5 high (assigned). OpenCodex-managed; not polled. Tokens/cost: unknown.
- UTC: issued 2026-10-29T11:30:40Z, deadline 12:00:40Z; work stopped 2026-10-29T11:37:33+00:00 (verified fully DONE, early finish allowed). Branch run/S15b-orch15.
- Files (all inside Owns): Build/web/src/workspace/{layout,viewport,view,react}.mjs, workspace.css, README.md (S15b section); tests/workspace/layout.test.mjs; evidence/S15/{react-ssr-check.mjs,.out.txt,layout-preview.html,workspace-tests-s15b.out.txt}.

## Result
Acceptance "viewer uses its public interface; no edits to viewer ownership": met. No file under Build/web/src/viewer, shell or app touched.
- layout.mjs: pure state -> 4 slots (stage-nav, viewport, panel, job-status), stage rail, schema-exact viewer request, job status text; every S15a phase labelled.
- viewport.mjs: one adapter.mount per (scene, mode, audience); replace aborts+disposes; late mount disposed; stale callbacks dropped; unexpected throw -> RENDER_FAILED.
- view.mjs/react.mjs: markup via injected h; createWorkspace(React) binding (React injected, so no new dependency); host div has no children.
- workspace.css: two-column grid, single column <860px.

## Checks (fresh)
- node --test tests/workspace/layout.test.mjs workflow.test.mjs: 17 pass (9 new). Includes real createViewerAdapter + validated fixture bundle + fake renderer: reducer scene reaches ready, load failure maps to LOAD_FAILED; request passes viewer checkViewerRequest; import-boundary test (workspace imports only ./ and ../lab/fit-contract.mjs).
- evidence/S15/react-ssr-check.mjs with real React 19.3.1 renderToString (React resolved read-only from canonical Build/web/node_modules): slots, aria-current, empty host div, synthetic banner asserted — ok.

## Ponytail (full)
Reuse: S15a reducer/fixtures untouched; viewer adapter, artifact-loader contract, fixture-bundle test helper, shell slot names, app CSS vars. Smallest-complete: no new deps (React injected via factory, markup via h so tests need no JSX transpile), no state lib, no panels beyond a heading. Skipped: S15c failure/retry surfaces, S15d interview chips, mystery mode, lab-mode request, resize logic (CSS only), app page wiring (S04-owned).
Fixtures: only S15a synthetic fixtures + viewer synthetic-room bundle; no gate/real-scene/physical/number claims.

## Risks / unverified
- No real browser/WebGL check: file:// blocked by browser policy and a local http server command was rejected by the sandbox policy, so layout-preview.html (static SSR + CSS) was NOT viewed; the CSS grid and 860px breakpoint are visually unverified. No next build/dev run (no installs; worktree has no node_modules).
- react.mjs effects (mount/unmount, StrictMode double-invoke) are covered only through the controller tests, not a DOM renderer.
- viewer request mode is always 'inspect'; scene.access 'private' + audience signed-in assumed from the job DTO; app must authorise server-side before rendering.
- Communication: silent; one completion line to controller. No browser tabs left needing cleanup beyond one failed in-app tab (no server started).
