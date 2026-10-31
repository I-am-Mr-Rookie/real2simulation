# S15ai-orch198 REPORT — PARTIAL

- Lane CLAUDE, step S15; assigned/actual anthropic/claude-opus-5-5/high via OpenCodex (coding quota: OpenCodex-managed; not polled). Tokens/cost: unknown (not observable). No Meta/GPU call, no secrets read, no Chrome, no publication.
- UTC issued 09:25:33Z, work started 09:26:41Z, implementation stopped at cutoff, report finalised at deadline 09:55:33Z (TIMEBOX.json).
- Worktree .worktrees/S15ai-orch198, branch run/S15ai-orch198, rebased onto main 430df7ce and then onto 7b4dc3c6 (S15am accepted; no conflicts). Not merged to main (controller).

## What changed (Owns only; shell/, workspace/, app/(private)/ untouched)
- Build/web/src/app/SiteFrame.jsx (new): branded chrome replacing ShellFrame in the root layout — logo mark /brand/mark-192.png (28px) + HTML wordmark "Real2Simulation" (BRAND.md prefers HTML text over raster wordmark), icon nav (book/flask from shell/icons.mjs; text labels hidden <=900px, title + accessible text kept), theme toggle, sign-in/AccountNav unchanged, footer copy verbatim.
- Build/web/src/app/ThemeToggle.jsx (new): System/Light/Dark segmented control reusing shell/theme.mjs (THEME_OPTIONS, applyTheme, choiceOf, THEME_KEY) — aria-pressed, aria-label, title.
- Build/web/src/app/layout.jsx: favicon /brand/favicon.ico + mark-32/192, apple-touch mark-192, openGraph/twitter A5 (1200x630), metadataBase from RAILWAY_PUBLIC_DOMAIN (fixes localhost OG URL found on first deploy).
- Build/web/src/app/(public)/page.jsx: H1 hero per DESIGN_DIRECTION (kicker, 2-line headline, 1-line sub, 2 icon CTAs, RECORDED/SIMULATED/what-if legend chips), A1 on a -2deg slab with the existing caption "Illustration only, not scene evidence." kept verbatim, 3-up A2/A3/A4 feature cards (Record/Fit/Replay, 1 line each), honesty strip "We abstain when scale is unverified."
- Build/web/src/app/(public)/MarketingArt.jsx (new): one <picture> per theme family (WebP 1x/2x + PNG fallback, explicit width/height, eager only for A1); dark family shown via html[data-theme] (dark + announced midnight/graphite ids; shortcut comment).
- Build/web/src/app/styles.css: S15ai block, CSS variables only (test asserts no hex); toggle 44px targets; grid minmax(0) to stop 1600px intrinsic art overflow.
- Build/web/src/app/(public)/library/page.jsx: removed hard-coded #d8cfbd and ink offset shadows -> tokens (border-strong, --r2s-shadow-sm/--r2s-shadow), hover lift, pill summary chips, full-width page. Copy unchanged.
- Build/web/src/lab/lab.css: legacy ink shadows/borders -> --r2s-shadow-ink / --r2s-shadow-sm / border-strong.
- tests/web-private/public-chrome.test.mjs (new, 4 tests): metadata/icons/OG wiring + asset existence, header mark/wordmark/icon nav/toggle/footer verbatim, home labels + picture sizes, no hard-coded colours/ink shadows.
- evidence/S15ai/: local screenshots home/library/lab x light/dark x 1280/375 (12) + deployed library light-1280 / dark-375.

## Ponytail (applied)
- Reuse: theme layer + icon set imported from shell/ (no edits, no new icon package); AccountNav reused; existing .primary-link/.secondary-link/.actions/state-tag styles; existing brand/marketing exports; stage.py + railway up deploy path from S15ab.
- Smallest complete: new SiteFrame instead of editing forbidden shell/ShellFrame (ShellFrame left in place, now unused by the layout); one MarketingArt helper for 4 placements; CSS-only token swaps in lab/library; source-level tests (JSX compiled by next build).
- Skipped (not done in 30m): library L1 filter chips with counts, 16:9 thumbnails, designed empty-filter state (B3); lab LB1 two-column layout, B4 empty-state art, SIMULATED chip pinned on every chart; about + sign-in pages only inherit the new chrome/tokens (no page-specific redesign); PWA manifest icons still /pwa/* (manifest lives in public/pwa, outside Owns); app/icon.svg route still also emits a link; contrast.py not run (token values are S15ah/S15am's).

## Fresh checks
- node --test "tests/workspace/*.test.mjs" "tests/shell-workspace/*.test.mjs" "tests/web-private/*.test.mjs" "tests/web-workspace-api/*.test.mjs" -> 157 pass, 0 fail (after rebase). public-chrome.test.mjs re-run after metadataBase change -> 4/4.
- npm run build (Build/web, node_modules junction to canonical, removed afterwards with (Get-Item).Delete()) -> exit 0, three times (last after 44px toggle change).
- Playwright (headless, not Chrome) local next start :3917: scrollWidth == clientWidth on home/library/lab, light+dark, 1280 and 375 (first pass caught 1720px overflow on home; fixed). Labels present in DOM: RECORDED, SIMULATED, what-if, "Illustration only, not scene evidence.", footer "Synthetic lab results are not calibrated measurements." Local library shows its UNAVAILABLE state (no local snapshot); deployed library shows SIMULATED / SCALE_UNVERIFIED / credit / "Display only · not a measurement." cards.
- Deployed https://web-dev-cd80.up.railway.app: brand mark + toggle on /, /library, /lab; og:image absolute https://web-dev-cd80.up.railway.app/images/marketing/a5-light-line@1x.png; icon/apple links -> /brand/*; favicon + A5 HTTP 200; scrollWidth 375 at 375 dark.

## Railway DEV web deploys (deployments.json NOT edited — controller lines)
Final web deployment (carries S15am main 7b4dc3c6 + S15ai): "deploymentId": "45cbf633-7282-42da-ac7c-bd1eba386867", "previousDeploymentId": "7ee86b56-bdb3-409c-a832-795b2ea9a462", "sourceRevision": "c51a457e4e78adf2fbae4cbb6b5ec0b6ca85abd0", "redeployNote": "S15ai-orch198: stage.py web + railway up (branded public chrome, home hero/features A1-A5, theme select for all S15am modes, token restyle library/lab; includes S15am)", "verifiedUtc": "2026-10-31T09:49:35Z", "providerStatus": "SUCCESS"
Intermediate S15ai DEV deploys superseded by the final one (all SUCCESS): 225e2b9f-ee6d-433f-a9fd-1651475f16f8 (a57d4125), 3c3189cc-9471-4cf3-8a63-b5132ea05e2b (175ac8da, OG fix), 49557426-b337-4b4f-8736-af5c0dd9edc6 (ebf786b7), ee2ceaa9-4600-4776-8a8c-d929b5d6c0cd (dd4d8c3a, first after S15am rebase; exposed 7-option icon toggle overflow 398px at 375 -> fixed in c51a457e).
Deployed verification (Playwright, headless): / paper 375 sw=375 labels 5/5; /library midnight 375 sw=375; /lab graphite 375 sw=375; / contrast 1280 and / dark 1280 sw=1280; select shows 7 modes and persists the stored choice; screenshots evidence/S15ai/deployed-*.png.

## DESIGN_QA self-score (public items + applicable blocking)
1 labels verbatim/visible: PASS on public pages checked (home legend + caption, library badges, footer). 2 contrast.py: NOT RUN. 3 375 no h-scroll: PASS (measured); toggle 44px after final change, nav icon links 36x44 (width < 44: gap). 4 theme persist/no flash: PASS via existing pre-paint script (reload with stored choice screenshotted). 5 focus ring: existing global :focus-visible, not re-verified per mode. 6 reduced motion: existing rule kept + feature hover transform only. 7 shadow-2 count on home: 3 (2 CTAs + hero slab) — over by 1. 15 icon set/aria: PASS. 16 empty states: NOT DONE for library/lab. 17 dark slab visibility: shadow-ink #000 on dark is weak (token value owned by S15am). 22 image variant per mode: PASS (light/dark family screenshots). 23 home: PASS (2-line headline at 1280, 2 CTAs, legend). 24 library filters/licence per card: PARTIAL (credit/licence line kept; no filter chips). 25 lab SIMULATED chip per chart: NOT VERIFIED/NOT DONE.
Overall: header/logo/metadata/home/theme acceptance met; library/lab redlines partially met -> PARTIAL.

## Communication
Silent run; one completion line. Controller-messaging tool (codex_app namespace) was removed mid-run, so the completion line is the final answer.

## Next action
Post-rebase (controller note): S15am moved THEME_CSS into ShellFrame; SiteFrame now renders the same THEME_CSS style tag (else the 6 modes would not apply on any page, since the root layout uses SiteFrame). Art family switches on html[data-tone="dark"]. ThemeToggle is now a native select of all THEME_OPTIONS (7 modes; segmented icons overflowed). Known cosmetic gap: at 375 the Sign in button wraps to a second header row (no horizontal scroll). Full suite after S15am rebase: 159/159 pass; npm run build exit 0 (twice post-rebase).
Controller: verify + fast-forward run/S15ai-orch198 into main; follow-up row for L1 filter chips/thumbnails/empty state, LB1 lab layout + B4 + pinned SIMULATED chip, PWA manifest icons -> /brand (needs public/pwa or src/pwa owner), app/icon.svg removal.
