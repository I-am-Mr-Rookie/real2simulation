# UI-d-orch81 REPORT — PARTIAL

- Lane/model: CLAUDE, anthropic/claude-opus-5-5/high; coding quota OpenCodex-managed; not polled. Tokens/cost: unknown (unobservable). Parent project 91e441f8-e40c-4ec4-bea2-de7fa1582d97.
- UTC: issued 05:47:23Z, work start ~05:49Z, implementation stopped ~06:06Z, reported ~06:07Z (TIMEBOX.json). Branch run/UI-d-orch81 from main dc74261.

## Changed
- `Build/reports/typeset.py`: only `_CSS` (+ comment). Markup, a11y structure, CSP, escaping, TeX untouched.
  - Formal-report home (myfront "warm, formal, academic"): serif headings stack (Libre Baskerville, Crimson Pro, Baskerville, Iowan, Palatino, Georgia), shared sans body (Instrument Sans -> Segoe UI/system-ui), mono numbers (Space Mono -> Source Code Pro/Consolas) with tabular-nums in table cells.
  - Warm paper ground #f5efe3, surface #fffcf5, ink #1d1f1c, muted #55514a (~7.8:1 on surface), one clay accent #9a3b16 (~6:1 on paper) for template eyebrow, list markers, note rule.
  - Tables/figures: 2px ink border + hard offset shadow (screen only), hairline row rules, no zebra (myfront print evidence), uppercase muted column heads, serif captions. Double-rule under h1 and above footer.
  - Consumes shared tokens via `var(--r2s-*, fallback)`; defines no global --r2s-* (UI-a owns those). Report is standalone, so fallbacks render.
  - States: :focus-visible 3px outline on table regions/skip/link; styled skip link; row hover; forced-colors fallback; prefers-reduced-motion block (no motion used anyway).
  - 375px: footer digest `overflow-wrap:anywhere` (long sha256 would otherwise force horizontal scroll), tables scroll inside focusable .tw, reduced padding/shadow under 30rem.
  - Print: white/black, no shadows/borders/backgrounds, 11pt, @page margin, break-avoid for rows/figures/headings, repeated thead; .skip/.noprint hidden (kept).
- `evidence/ui/orch81/`: gen_html.py (renders the 4 visibly synthetic fixture reports), before/*.html, after/*.html, numeric_diff.json.

## Truth/safety preserved
No text/label removed: fitter_digest + labels footer, fixture labels, template assumptions, chart alt/figcaptions, Save-as-PDF note. No new numbers or markup text. CSP unchanged (no font-src => fonts are local names only, never fetched); no JS.

## Checks (fresh, this worktree)
- `python -m unittest discover -s tests/reports -t .` -> Ran 41 tests, OK (incl. test_a11y semantics/print/diff-clean).
- `python -m tests.reports.run_diff evidence/ui/orch81` and `... evidence/S17` -> all 4 templates (0 mismatches, 15 numbers), exit 0; evidence/S17/numeric_diff.json byte-unchanged (git clean).

## NOT verified (why PARTIAL)
- No desktop/375px screenshots, no visual/contrast check in a browser: ChatGPT in-app browser unavailable to this worker — `cua.createBrowserTab('iab', ...)` returned "Browser is not available: iab"; three other attempts (incl. getState) timed out. Did not substitute Chrome/Edge/Playwright per contract. Nonterminal blocker sent to controller 06:03Z. Contrast ratios above are computed, not measured in-browser.
- Next: controller (with working iab) opens evidence/ui/orch81/after/*.html (e.g. `python -m http.server` in that dir) at desktop + 375px, saves screenshots, checks focus ring and print preview.

## Skills (concrete use)
- myfront: chose "formal/academic" home allowed for reports; Libre Baskerville/Crimson Pro headings + Instrument Sans + Space Mono pairing; hard offset shadow (hard-offset system); hairline print tables without zebra; avoided dot grids/neon/acid-lime/generic sans. calibrated-preferences.json grep (06:13Z, after cutoff, no code change) confirmed rules type.serif.formal-reading-range (Libre Baskerville first, Crimson Pro alt), print.academic-structure (hairline tables), ae.dir.technical-paper direction.
- Mobbin: search_screens (platform web) for report/results-table layouts returned refs incl. Elicit (research results table), GitBook (doc reading column), Hex (data doc). Used only as general pattern confirmation (narrow reading column, captioned tables, muted column heads); screen images were not opened/inspected in detail — time. No assets copied.
- Superpowers: verification-before-completion principle applied (fresh test/diff evidence before claims; visual unverified stated). Skill files not opened — time; TDD skipped: CSS-only change, no new logic, existing a11y tests cover structure.
- Ponytail: reuse = existing render_html markup/a11y/CSP and test suite untouched; smallest complete change = one constant (_CSS) restyled, no new deps/fonts/files in Build; skipped markup refactor, TeX restyle (out of visual scope, would risk S17e diff), new tests (no new logic). Risks: local-font availability varies (fallbacks defined); `text-wrap:balance`/forced-colors ignored by older browsers harmlessly; hover tint on rows could be confused with selection (subtle).

## Communication
Silent except one authorized nonterminal blocker and the one completion line.
