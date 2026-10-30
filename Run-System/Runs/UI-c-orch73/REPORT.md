# UI-c-orch73 REPORT — PARTIAL
Lane CLAUDE / anthropic/claude-opus-5-5 high (OpenCodex-managed; not polled). Base main 6be0934. UTC start 05:19:43Z; work stopped at deadline 05:48:26Z. Tokens/cost: unobservable.

## Changed (3 files)
- Build/web/src/lab/lab.css — full restyle. Local --lab-* aliases resolve to var(--r2s-*, fallback) (warm paper #f4efe4 / surface #fffdf8 / ink #1c1a17 / one accent #b4451f / muted #5b554c); no globals redefined; app/styles.css untouched. Hard ink offset shadow on control + results cards; primary button ink-filled with accent offset, secondary surface + ink offset; hover lift / active press / :focus-visible 3px outline / disabled flattened. Custom-styled radio + checkbox (appearance:none; no bare native controls); selected template card gets accent offset; disabled Mystery toggle dashed. Status line states (running/fitting=warn, ready/fitted=ok, error=danger tint). Mono (--r2s-font-mono, Space Mono fallback) for eyebrow, badge, table numbers (tabular-nums), chart axis text, reveal value. Chart: single accent trace on paper ground (restrained: accent + ink axis + muted labels). prefers-reduced-motion kills transitions/transforms. 650px/390px breakpoints kept.
- Build/web/src/lab/BrowserSimulation.jsx — class hooks only (lab-browser-sim section, eyebrow on the existing "Simulated · synthetic · RK4-only" truth line, secondary button). Text/behavior unchanged.
- Build/web/src/viewer/three-renderer.mjs — chrome inline styles only: truth banner (SYNTHETIC / SCALE_UNVERIFIED text untouched, plain text, full opacity) gets mono uppercase on surface with 2px warn underline; labels get surface chip + ink border + small offset; toolbar buttons keep 44x44 min + 18px and gain surface/ink border/offset shadow. All via var(--r2s-*, fallback). No render budget, limit, geometry or draw-loop change.
- page.jsx untouched (no need).

## Verified (fresh)
- node --test tests/viewer/*.test.mjs tests/lab/{ui-contract,ui-helper-oracle,ui-helper-recovery,r14-ui-invariants,browser-simulator}.test.mjs after all edits: tests 115, pass 112, fail 0, skipped 3.
- IAB (ChatGPT in-app browser, local next dev --webpack :3174, no auth/deploy): /lab desktop + 375px, Run trial + Fit & reveal executed against real local API. 375px: documentElement scrollWidth 327 == clientWidth 327 (no horizontal scroll). Truth text present: "Simulated · m" badge, "Fit complete. This is simulated evidence, not a calibrated measurement.", 1σ note, Limits, dev footer. Before (stashed edits, computed .lab-controls box-shadow "none") vs after captured.
- Evidence: evidence/ui/orch73/UI-c/{before-lab-desktop.png, before-lab-375.png, after-lab-desktop-running.png, after-lab-desktop-fitted.png, after-lab-375.png}.

## Skills applied
- myfront: bold-technical home; Instrument Sans + Space Mono pairing ("my favorite"); restrained chart (one accent + neutrals); hard black offset shadows; finished states incl. styled radio/checkbox (myfront: one unstyled native control ruined a 9/9 form); avoided lime/dot-grid/neon.
- Mobbin (tool worked): search_screens "science simulation lab controls parameter panel with results chart" -> Stripe, Databricks, Hex, Braintrust, Causal… Opened Hex (screen 2d4c8181) and Causal (c36bf8b1) as reference only: Hex status chips with dot ("In development") -> compact bordered uppercase mono truth badges; Causal uppercase section chips + right-aligned tabular numbers + tiny restrained sparklines -> mono tabular table numbers, uppercase muted th with ink rule, single-accent trace. No assets/brand marks copied. redesign-screen/best-practices SKILL.md bodies NOT read (time).
- Superpowers verification-before-completion applied in spirit (fresh test run + browser evidence before claims); skill bodies not read (time). Ponytail: smallest change = CSS + class hooks + inline style extension; no new components, deps, tests (no new logic), no flow rewrites; reused existing classes/breakpoints.

## Not done / risks (why PARTIAL)
- Viewer chrome restyle NOT visually verified in browser (viewer mounts in private /workspace behind auth; no viewer screenshots). Only unit tests cover it.
- Attempted tests/viewer/browser-smoke.html via local python http.server :3175 in IAB at ~05:40Z: page rendered blank (no banner/toolbar, scrollWidth 10786) — harness issue not diagnosed (time); screenshots not committed. Viewer chrome visual remains unverified.
- tests/lab service tests (contact-integration, process-tree, session-service, r14-service-invariants): earlier full lab run exit 1; isolated rerun shows process-tree harness child failing (Build/lab/session-service.mjs, not touched by this run). Not re-run on base main, so pre-existing vs environmental is unverified.
- WCAG AA: palette chosen for AA (muted #5b554c on #fffdf8 ≈7:1, accent #b4451f on surface ≈5:1) but not measured with a tool; focus visible by design, not keyboard-walked in browser. --r2s-* tokens were absent on this base (UI-a not merged) so fallbacks rendered; final look depends on UI-a token values. h1/h2 serif comes from global styles (UI-a).
- 375px full-page screenshot looks right-cropped in capture; DOM metrics show no overflow.
- Dev server + node_modules junction (Build/web/node_modules -> canonical, git-ignored) left in worktree; logs in .worktrees/uic-*.log.
Next: merge after UI-a tokens; verify viewer chrome on /workspace with signed-in session; investigate process-tree test on main.
Communication: silent; one completion line to controller.
