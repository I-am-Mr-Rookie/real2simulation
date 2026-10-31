# S15aq-orch205 REPORT

Status: PARTIAL (verified smaller scope; see Not done).
Lane/model: CLAUDE, anthropic/claude-opus-5-5 high. Coding quota: OpenCodex-managed; not polled. Tokens/cost: unknown (not observable). No Meta/GPU/paid call, no Chrome, no deploy.
UTC: issued 2026-10-31T10:55:26Z; worktree created 10:56Z; controller HOLD 10:57Z to GO about 11:00Z; implementation stopped 11:15Z.

## Done
- Owner copy: two-line H1 (Film Physics / Simulate it in 3D, each span nowrap, fluid clamp size), exact sub caption, card titles Film it / Measure it / Remix it with short truthful captions, trust line under the chips, "Guess the Gravity" hook card to /lab, zero em dashes (old sub had one).
- Showcase below the fold (GO addition B): How it works (6 steps), The agent asks instead of guessing (existing B5/B6 art), Honest by design (RECORDED / SIMULATED / what-if / scale unverified), closing CTA (library, lab, Guess the Gravity, Explore the code on GitHub). No numbers, no new assets.
- GitHub amendment: REPO_URL constant, official mark inline SVG with currentColor, new tab, rel="noopener noreferrer", min-height 44px. Repo may still be private until Koushik's separate S25d go-ahead, so logged-out visitors may get a 404 until then.
- Motion layer (evidence/S15aq/BRIEF.md): CSS scroll-driven animations only, inside prefers-reduced-motion: no-preference and @supports (animation-timeline: view()). Devices: hero planes differential parallax on exit; signature swap of Measure it and Remix it on an arc then deck onto Film it while the row leaves (desktop only); honesty strip clip wipe; steps dealt out of a stacked deck (desktop) or rise (mobile); agent art counter-parallax; label rows from alternating sides; CTA grow. Keyframes use translate/scale/rotate/opacity/clip-path only and start or end at identity.

## Ponytail (applied)
- Reuse: existing hero/features/chip/card/actions classes; MarketingArt gained one set="app" prop instead of a new image component; existing icon() set.
- Smallest complete: no JS, no client component, no engine; pure CSS in one new file under home/. shortcut comment: no IntersectionObserver fallback, so Safari/Firefox without animation-timeline get the static page.
- Skipped: hero tertiary GitHub link (controller allowed keeping only the CTA button; avoids changing the hero resting look), JS fallback, scroll-craft engine.

## Checks (fresh)
- node --test workspace, shell-workspace, web-private, web-workspace-api: 161 pass, 0 fail (includes new tests/web-private/home-scroll.test.mjs; rerun after the GitHub/hook amendment).
- npm run build: exit 0 (final CSS).
- After rebase onto main 1b9ab540 (29 Build/web files changed upstream by parallel runs): node --test same four globs 165 pass, 0 fail; npm run build exit 0. Frames/layout evidence predate the rebase.
- Playwright headless (codex runtime playwright-core chromium, not Chrome), local next start: frame strips 11 positions at 1280, 390 and 1280 reduced motion: evidence/S15aq/frames/, contact sheets evidence/S15aq/sheet-*.png, logs frames-log.txt.
- Layout (evidence/S15aq/layout-check.json): scrollWidth equals viewport at 320/390/1000/1280 (an earlier 20px overflow at 320/390 from side-slide rows was fixed with overflow-x: clip on that section); H1 lines scrollWidth equals clientWidth (no overflow), one line each.
- What I saw: top of page at 1280 identical in layout to reduced motion; mid-scroll frames show the hero lifting, cards in motion as the row leaves, strip half wiped, steps dealing; final frame shows all four CTA buttons at rest.

## Not done / risks
- Pixel identity at scroll 0: motion vs reduced-motion at 1280 differs only by antialiasing (bbox hero area, max channel diff 152, 5533 px above 32 of 1,024,000), likely compositor layers of the animated hero; visually identical. No before/after diff against a main build was run (no time); resting look changed intentionally via approved copy.
- Mid-swap moment not isolated in a dedicated frame (10% steps); visual tuning of the swap arc unreviewed.
- Dark modes and 6 themes not screenshotted; GitHub mark uses currentColor.
- Junction Build/web/node_modules removed with .Delete(); local .next build output left (ignored).

## Files
Build/web/src/app/(public)/page.jsx; Build/web/src/app/(public)/MarketingArt.jsx; Build/web/src/app/(public)/home/home.css; tests/web-private/home-scroll.test.mjs; evidence/S15aq/ (BRIEF.md, frames.cjs, layout-check.cjs, sheet.py, frames, sheets, logs); Run-System/Runs/S15aq-orch205/.
Next action: controller visual review of the swap timing and dark modes, optional baseline diff vs main, merge and redeploy.
Communication: silent; one completion line to controller.

