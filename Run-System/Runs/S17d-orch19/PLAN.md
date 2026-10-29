# S17d-orch19 plan
Objective: compile reports for all four templates (PDF, or explicit HTML print fallback). Lane CLAUDE, anthropic/claude-sonnet-5-5/high. Issued 2026-10-29T11:52:55+00:00, deadline 12:22:55Z.
Owns: Build/reports/; tests/reports/; evidence/S17/; Run-System/Runs/S17d-orch19/.
Approach (Ponytail): reuse S17c write_documents + installed MiKTeX pdflatex; one new stdlib module Build/reports/compile.py (compile_pdf, compile_all); no new deps.
Checks: 4 PDFs compile + pdftotext shows fitter g/template name/"simulated"; missing/broken compiler -> html-print-fallback, stale PDF removed; full tests/reports green.

