# S17f-orch68 REPORT — PARTIAL
Lane/model: CLAUDE, claude-sonnet-5-5 medium (OpenCodex-managed; not polled). UTC start 2026-10-30T05:07:47Z.
Scope: visibly synthetic fixtures only; no Gate A/S14 real interview content; S14 real-integration portion PENDING (S14 dependency unmet) — the only reason for PARTIAL.

## Defects found (Build/reports/typeset.py HTML) and fixes
- No main landmark / skip link / viewport meta -> added `<main id=main>`, skip link, viewport.
- Table headers unscoped, no row header, wide tables not keyboard-pannable -> thead/`th scope=col`, first column `th scope=row`, focusable `role=region` scroll wrapper with aria-label.
- Chart alt was just "<key> chart" -> descriptive alt + visible figcaption (digit-free; exact values stay in tables).
- No print CSS / fallback hint -> `@media print` (hide skip/hint, repeat table header, avoid row/figure breaks, no width cap) and a screen-only "Save as PDF" note (no script: CSP blocks JS, so no print button).
- Contrast: text #111 on #fff, borders #767676 (>=4.5:1), focus outline #0b57d0; chart bars #4878a8 on white (>3:1).
- Sections now aria-labelledby their h2; heading order h1 then h2 only (no skipped levels).
CSS/markup is digit-free and `<style>` form unchanged, so the S17e numeric diff stays clean (0 mismatches x4, 15 numbers each).

## Fresh checks
- `python -m unittest discover -s tests/reports -t .` -> 41 tests OK (38 prior + 3 new tests/reports/test_a11y.py: semantics x4 templates, print/fallback, diff clean). Log evidence/S17/test-reports-all.txt.
- `python -m tests.reports.run_diff evidence/S17` -> all four 0 mismatches.
- Actual compile (MiKTeX pdflatex, evidence/S17/s17f_compile.py -> compile_manifest.json): all four status=pdf, 2 pages each; PDFs regenerated in evidence/S17/compiled/. Fallback path with missing compiler already covered by test_compile (removes stale PDF, html-print-fallback).
## Not verified / skipped
- No browser/screen-reader run (no real AT; structure checked by HTMLParser only); no automated contrast tool; contrast values by hand.
- Added hyperref (pdfusetitle, pdflang=en) to the TeX so PDFs carry title+language; recompiled, 4/4 pdf, 2 pages, 41 tests OK, diff clean. PDFs remain untagged (no PDF/UA): HTML is the accessible format; PDF is a print artefact.
- Rendered print layout not visually inspected. S14/Gate A real content untested.
## Ponytail
Reused existing render/typeset/diff, test fixtures and compile script pattern; stdlib HTMLParser, no deps; one CSS constant + one alt dict; no new abstractions. Communication: silent, one final line.

