# UI-d-orch81 PLAN

- Lane/model: CLAUDE, anthropic/claude-opus-5-5/high (OpenCodex-managed; not polled). Parent project 91e441f8-e40c-4ec4-bea2-de7fa1582d97.
- Issued 2026-10-30T05:47:23Z; deadline 06:17:23Z; minute-25 cutoff 06:12:23Z. Branch run/UI-d-orch81 from main dc74261.
- Objective: visual finish of generated report HTML/print CSS in Build/reports/typeset.py (formal-report home), keeping every S17f a11y fix, CSP no-JS, numeric diff 0 mismatches, all truth labels.
- Owns: Build/reports/; tests/reports/; evidence/ui/orch81/; Run-System/Runs/UI-d-orch81/.
- Checks: python -m unittest discover -s tests/reports -t . ; python -m tests.reports.run_diff evidence/S17 (0 mismatches); in-app-browser desktop + 375px screenshots.
