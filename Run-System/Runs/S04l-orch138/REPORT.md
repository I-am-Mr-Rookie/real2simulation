# S04l-orch138 REPORT — DONE

- Lane/model: CLAUDE, anthropic/claude-opus-5-5 medium. Coding quota: OpenCodex-managed; not polled. Tokens/cost: unknown (not observable). No paid/API/GPU spend.
- UTC: issued 2026-10-30T11:26:56+00:00; work start ~11:30:29Z; stopped 2026-10-30T11:39:22+00:00. Base main b82b1a6, branch run/S04l-orch138.

## Changes
- `Build/web/src/app/(public)/library/library-copy.mjs` (new, pure): status TAG/TONE, `MYSTERY_COPY`, `creditLine(entry)`, `groupDemos`. Lets node tests check real copy without JSX.
- `LibraryClient.jsx`: stale "setup only. The answer is withheld until your own fit in the lab" replaced per S18l: "Mystery-g practice shape at Earth g. This is not a blind test. To play blind, open the lab: the server draws a hidden g for each session." + "Play blind in the lab →" (/lab). Summary chips (playable / practice setup / unavailable counts from the manifest), "Ready to open" grid, unavailable entries collapsed into a `<details>` "Not available yet (n)" list with UNAVAILABLE tag + reason, per-card status + SCALE_UNVERIFIED tags, credit line, limitations in `<details>`, replay panel expands the card full-row (`aria-controls`, `aria-busy`, `role=alert` error with "No trace was shown"), fail-closed library-unavailable card.
- `page.jsx`: scoped CSS using existing `--r2s-*` tokens (surface, 1.5px ink border, offset shadow, Space Mono tags); 420px breakpoint.
- `tests/web-library/library.test.mjs`: +1 test (copy says "not a blind test"/"hidden g", no "answer is withheld", SIMULATED/SCALE_UNVERIFIED/UNAVAILABLE present, real-manifest grouping complete, every unavailable has reason, every ready entry credits SIMULATED, footage credit format).

## Credits
Guest manifest exposes `source` only for the 3 synthetic entries → "Credit: SIMULATED · project-authored, no external footage." Unavailable entries serve no media → no credit line (reason shown instead). Footage branch (creator · licence) is supported and unit-tested but no footage entry is served today. No S18h data copied in (api/library + Build/library not owned).

## Checks (fresh)
- `node --test tests/web-library/library.test.mjs`: 6/6 pass (5 existing + 1 new).
- `npm run build --prefix Build/web`: green (via a temporary junction to canonical Build/web/node_modules, removed after; gitignored).
- `next start -p 3417` with `R2S_GUEST_SNAPSHOT` pointed at a temp snapshot made by the same GUEST_SCRIPT (prod mode 503s without a snapshot, by design). Screenshots: [desktop](../../../evidence/S04l/library-desktop.png), [desktop, replay open + unavailable expanded](../../../evidence/S04l/library-desktop-open.png), [375px, replay open](../../../evidence/S04l/library-375-open.png) (Playwright, true 375 viewport).
- 375px: `scrollWidth == innerWidth == 375`, 0 overflowing elements; replay state `ready`.
- Keyboard: Tab order skip-link → nav → Limitations → Play replay → … → "Play blind in the lab" → "Not available yet"; global focus-visible ring applies. Native button/details/link only.
- A headless-Chrome `--window-size=375` shot was discarded: Chrome's min window width clipped it (false overflow); Playwright measurement is authoritative.

## Ponytail / skills
- Reuse: existing `.state-tag`/`.state-card`/button/focus styles and `--r2s-*` tokens; existing loader/replay unchanged; native `<details>` for disclosure (no JS state); counts derived from manifest (no new data/numbers).
- Smallest complete: one pure helper module only because tests need copy without a JSX loader; no new deps.
- myfront applied: kept the brand's warm paper + hard offset shadow + Instrument Sans/Space Mono; finished empty/error/unavailable states. Mobbin: 1 search (web library card grids) — Arcade library (primary grid + secondary "Resources" section) informed the ready/unavailable split; Fabric empty state informed the explicit empty copy. Superpowers: not needed for this size.
- Skipped: filters/search (19 entries), thumbnails (no served media), S18h credit import.

## Limits / risks
- Entry titles still come from data (e.g. "…play blind in /lab"), so mystery wording appears twice; changing titles belongs to Build/library.
- Screenshots used a temp snapshot, not the staged deploy snapshot; no deploy.
- No new numeric claims; labels SIMULATED/SCALE_UNVERIFIED/UNAVAILABLE stay visible.

Communication: silent; one completion message to controller only.
Next: controller review/fast-forward merge.
