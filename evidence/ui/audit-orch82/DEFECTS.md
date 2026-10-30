# UI-audit-orch82 — prioritized defects (read-only review)

Sources: Build/web/src/app/styles.css tokens on main; UI-a after-shots evidence/ui/orch71/after-*.png; UI-b after-shots evidence/ui/orch72/after-*.png (both captured by those runs in the ChatGPT in-app browser). Fresh in-app capture by this run FAILED (see REPORT). Owner = surface that should fix.

## P1
none confirmed. No truth label removed/softened in reviewed shots: SYNTHETIC banner, SIMULATED pills, "Illustration only, not scene evidence", "Synthetic lab results are not calibrated measurements", "EMPTY · NOT CONNECTED" all present.

## P2
1. **[UI-b] Fit values over-precise / unit typography** — evidence/ui/orch72/after-desktop.png, fit summary + residual tables ("1.887124302 ± 0.1415784327 m/s^2", "0.02277194369 m"). Fix: display-format only (round value to the uncertainty's 2 sig figs, e.g. 1.89 ± 0.14 m/s²; keep full raw value in a `title`/details or copy cell); render `^2` as superscript ². No value changes, no new numbers. Ref: Amplitude chart+breakdown table (Mobbin 3afcd733) — compact formatted values with exact data one click away.
2. **[UI-b] SYNTHETIC banner off-palette** — after-desktop.png top of workspace: saturated amber (Tailwind-like yellow) clashes with warm-paper tokens. Fix: keep text/role unchanged; background `color-mix(in srgb, var(--r2s-warn) 14%, var(--r2s-surface))`, 1px border `var(--r2s-warn)`, left 4px bar; verify AA. Never hide/shorten wording.
3. **[UI-b] Right column cards detached** — after-desktop.png: status card and Job card separated by ~170px empty gap (aside stretched to viewer height, items spaced). Fix: aside `align-content:start; gap:var(--r2s-space-4)` (or `align-self:start` on cards). Ref: Databricks notebook (Mobbin 29c5dddd) keeps status metadata adjacent to its result.
4. **[UI-a] Control border contrast** — styles.css `--r2s-border:#cfc5b2` on `--r2s-bg:#f3eee3` ≈1.5:1. Fine for decorative rules, but inputs/select/chips that rely on it fail WCAG 1.4.11 (3:1). Fix: add `--r2s-border-strong` (e.g. #8f877a, already --r2s-chart-2, ≈3.3:1 on bg) for input/select/textarea/.ws-chip borders; keep #cfc5b2 for dividers.
5. **[UI-b vs UI-a] Focus colour inconsistency** — UI-a token `--r2s-focus:#1c1a16` (ink) while UI-b REPORT measured `.ws-chip/.ws-submit:focus-visible` = 3px rgb(184,67,15) (its fallback, not the token). Fix: UI-b consume `var(--r2s-focus)` + same offset as global; one focus style app-wide. Re-measure in-app.
6. **[UI-b] Empty viewer = 430px black slab** — after-desktop.png / after-375.png: dark canvas block with "Scene loaded." caption. In the harness WebGL did not paint, so unverified in-app, but the empty/unloaded state should be a paper-toned state-card (reuse UI-a `.state-card` + `.state-tag` "EMPTY · NOT CONNECTED" pattern) not a dark block; avoids the dark-neon look and matches library empty state.

## P3
7. **[UI-b] Repeated SOURCE column** — every fit row repeats "S11 offline quantity-to-fit adapter". Fix: caption once ("Source: S11 offline adapter unless noted") and show only exceptions; keep provenance text present.
8. **[UI-b] Desktop width use** — Interview and Fit cards span only ~half width under the viewer with empty right side. Fix: let `.ws-panel` below the viewer span the full grid (`grid-column:1/-1`) or max-width ~72ch centred.
9. **[UI-b] "Failed" step wavy underline** — job step list renders red wavy underline; reads like a spell-check error. Fix: solid 2px underline or ✕ glyph + `var(--r2s-danger)` text.
10. **[UI-a] Home vertical dead space** — orch71/after-desktop-home.png: ~150px empty band before footer at 900px height. Fix: `main` min-height not forced, or footer `margin-top:var(--r2s-space-6)`. Ref: Steep landing (Mobbin 901f5e97) — warm off-white ground, restrained single accent, tight hero→content rhythm (supports current direction).
11. **[UI-a] 375 nav wraps to 2 rows** — orch71/after-375-library.png: brand row + 3 links row; acceptable, no overflow. Optional: keep "Sign in" as the only filled button (already), reduce link gap so it stays one line ≥390px.
12. **[dev-only] Next dev indicator overlaps footer at 375** — orch71/after-375-library.png. Not product; ignore (absent in prod build).
13. **[UI-b] Fallback drift** — harness fallbacks (#b8430f etc.) differ from tokens (#b23a0e). Use exact token values as `var()` fallbacks so unstyled contexts match.

## Lab/viewer (UI-c in progress — note only)
Not reviewed visually (UI-c-orch73 in flight; fresh capture failed). Apply same checks after merge: banners via `--r2s-warn` tint, strong control borders, single focus token, no native `<select>` popups unstyled, 375 scrollWidth==clientWidth.
