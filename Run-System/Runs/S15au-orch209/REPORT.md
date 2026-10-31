# S15au-orch209 REPORT: DONE

Lane CLAUDE, model anthropic/claude-opus-5-5 high (assigned). UTC start 2026-10-31T11:36:00Z (issued 11:35:03Z), end 2026-10-31T11:47:31+00:00. Coding quota: OpenCodex-managed; not polled. Tokens/cost: unknown (not observable). No Meta/GPU/paid call, no deploy, no secrets, no Chrome (headless codex-runtime playwright-core chromium).
Branch run/S15au-orch209 from main fb8a5a42. Worktree .worktrees/S15au-orch209.

## Changes (Owns only)
- page.jsx: agent, honesty and CTA sections are now `show show-split` (copy left, art/cards right at >900px, stacked below). Agent images get captions "The agent asks" / "Your answer, labelled". Honesty section gets the line "Every result carries one of these labels." (reused hero aria-label copy) and labels render as a 2x2 card grid. CTA left-aligned like the others with a short line and a 2x2 button grid. REPO_URL and GITHUB_MARK now imported.
- MarketingArt.jsx: the shared home for `export const REPO_URL` and `export const GITHUB_MARK` (moved verbatim from page.jsx).
- home/home.css: `.show-split` grid 4fr/7fr; label grid 2x2; `.honesty-strip { max-width: none }` (it was capped by global `p { max-width: 65ch }`, the cause of the 62% strip); dropped the 720px caps and centred CTA; <=560px single column. Motion: step deal range `entry 0% entry 100%` (was `cover 40%`) so a row resting mid-screen is never half-dealt. Card swap timing unchanged (checked frames, crossing reads intentional).
- SiteFrame.jsx: mark 34px (attrs + CSS); icon-only header GitHub link (aria-label "GitHub repository", target _blank, rel noopener noreferrer, shared REPO_URL/GITHUB_MARK); FRAME_CSS appended to the existing THEME_CSS style tag (styles.css is outside Owns): <=700px workspace link shows `content:"Workspace" / ""` (alt-empty generated text, accessible name stays "Private workspace"), 521-700px shows the "Real2Simulation" text beside the mark, <=420px nav gap 0 and 40px targets so 375px does not overflow.
- tests: home-scroll asserts shared constant export/import, three splits, captions, no centred CTA, 2x2 labels; public-chrome asserts header GitHub link attrs, 34px mark, workspace pseudo-label.

## Ponytail (full) applied
Reuse: existing classes (.show, .card, .slab, .chip, .actions, figcaption global style), existing art b5/b6, existing icon(), existing THEME_CSS injection pattern for header CSS, existing hero aria-label copy. Smallest complete: CSS-only label/caption/layout changes, no new component, no new images, no numbers. Skipped: IntersectionObserver fallback (S15aq shortcut kept), icon before "Workspace" (would not fit at 375).

## Fresh checks
- `node --test tests/web-private/*.test.mjs`: 21 pass, 0 fail (incl. new S15au test).
- `npm run build` (Build/web): Compiled successfully (run after the last edit).
- Local `next start` + evidence/S15au/shoot.cjs: all 6 themes x 1280/375 x motion/reduced: scrollWidth == clientWidth (no horizontal overflow), mark 34px, header GitHub link _blank/noopener noreferrer, workspace link height 44px (one line), labels RECORDED/SIMULATED/what-if/scale unverified present verbatim, no em dash in body text. Log: evidence/S15au/after/log.txt. rg found no U+2014 in owned source files.
- Before (DEV https://web-dev-cd80.up.railway.app/, reduced motion): paper/dark/contrast at 1280/375 in evidence/S15au/before/ (mark 28px, no header GitHub link).
- After: evidence/S15au/after/after-<theme>-<1280|375>[-rm].png (24 full-page) + 5 dark 1280 mid-scroll frames and 5 dark 375 mid-scroll frames (after-dark-*-mid15..75.png). Viewed dark/paper 1280, contrast 375, mid30/45/60 frames.

## Limits / risks
- Signed-in header is simulated: no Clerk session locally, so the shoot script injects AccountNav's shape (<a href="/workspace">Private workspace</a> + 32px avatar). Verify on DEV signed in after deploy.
- "Real2Simulation" text is not shown at 375: measured header needs ~140px more than available beside the icon nav; shown from 521px up and on desktop.
- Header targets are 40px (not 44px) at <=420px only, above WCAG 2.5.8 24px minimum.
- A process on 127.0.0.1:3918 (not this run's) blocked that port; used localhost:3926.
- Evidence ~10 MB of PNGs.

Next: controller deploys to DEV and checks the signed-in 375 header.
Communication: silent; one completion message to controller.

