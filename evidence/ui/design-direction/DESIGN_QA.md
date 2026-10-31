# DESIGN_QA — controller acceptance checklist for UI rows (S15ah, S15ai, S15am and later)

How: for each UI row, capture screenshots at **1440x900 and 375x812** in **every mode** (paper, light, dark, midnight, graphite, contrast) for the screens the row touched (W1 empty, W2 interview, W3 result, W4 mobile, H1 home, L1 library, LB1 lab — see DESIGN_DIRECTION §11). Save as `<screen>-<mode>-<width>.png` in the row's evidence dir. A row passes only if every applicable item is YES; record failing item numbers in REPORT. Items 1-6 block any row; others block if the row touched that area.

## Blocking (honesty + access)
1. Every applicable label is visible and verbatim in every mode/width: RECORDED, SIMULATED, what-if, scale unverified, owner clip, Held-out caveat, FIXTURE (DOM text + visible in screenshot; not tooltip-only, not truncated, original case).
2. `python evidence/ui/design-direction/contrast.py` exits 0 and shipped CSS token values equal COLOR_MODES.md (devtools spot-check 5 tokens per mode).
3. 375px: no horizontal scroll (`document.documentElement.scrollWidth <= 375`), tap targets >= 44px, bottom bar/sheet never covers the primary action.
4. Theme: System and each mode persist across reload; no flash of wrong theme (first painted frame already themed).
5. Keyboard: visible focus ring (--r2s-glow) on rail, tabs, question options, buttons, inputs in a light AND a dark mode; tab order rail -> header -> centre -> panel.
6. `prefers-reduced-motion: reduce` removes pulse, count-up and drawer slide (short fades only).

## Hierarchy + copy
7. One hero per view (dropzone / question card / g value); at most 2 shadow-2 elements visible per view (count them).
8. Header title = project/clip name at h3; "fixture" is a chip, not a 2-line title.
9. No helper paragraph longer than 1 sentence on the default view; policy text lives in the (i) popover, still verbatim.
10. Question text appears once (panel); centre shows only the 1-line pointer chip.
11. Job ids mono, middle-truncated, copy affordance; no wrapped hashes.
12. Result: g value in metric-xl mono tabular with ± uncertainty and unit adjacent; caveat callout present.

## Components + craft
13. Stage stepper = pills with state icons; no "(not run)" parentheses in visible labels; state in aria-label.
14. Tool rows <= 1 line + optional state line; no always-visible kbd hints.
15. One icon set, consistent stroke, sizes per spec (14/16/18/20); icon-only buttons have tooltip + aria-label.
16. Empty states = illustration + h3 + 1 line + 1 primary; no dashed box with a bare mono chip.
17. Dark modes: offset slab visible (lit tone), not black-on-black; bg < surface < elevated visibly stepped.
18. Radii concentric (inner = outer - padding) on nested cards; no random radii.
19. Inputs, textarea, selects, menus fully styled in every mode (no native white dropdown in dark — myfront "finish every state").
20. Disabled primary readable (text >= 4.5:1) and clearly disabled (outline style), not grey-on-grey.
21. Spacing on the 4px scale; panel content 16px from edges, centre 24px; nothing touches a border.
22. S15ak/S15al images use the correct light-line/dark-line variant per mode, crisp at 2x, no alpha halo.

## Public pages
23. Home: headline <= 2 lines at 1440 and <= 4 at 375; exactly 2 CTAs; evidence legend chips visible.
24. Library: filter chips with counts; licence + attribution visible on every card (verbatim); empty filter state designed.
25. Lab: SIMULATED chip pinned on every chart/viewport in every mode.

Verdict line for REPORT: `DESIGN_QA <row>: <n>/<applicable> pass; fails: [...]; screenshots: <dir>`.

