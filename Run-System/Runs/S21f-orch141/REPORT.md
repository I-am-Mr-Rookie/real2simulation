# S21f-orch141 REPORT — DONE

Lane CODEX-2 (army: Claude); actual model anthropic/claude-opus-5-5 medium (OpenCodex-managed; not polled). Project Meta AI Hackathon 91e441f8-e40c-4ec4-bea2-de7fa1582d97. Base main 7dde2c9; branch run/S21f-orch141. UTC start 2026-10-30T11:32:27Z (issue), work stopped 2026-10-30T11:40:08+00:00. Tokens/cost: unknown (unobservable); no API/GPU spend.

## Result
All pitch-facing benchmark numbers in Owns match the generated evidence: **0 mismatches, 100 checks** ([evidence/S21/crosscheck.json](../../../evidence/S21/crosscheck.json)). No fixes to numbers were needed.

Checked by `Build/benchmark/crosscheck.py` (read-only):
1. Every BENCHMARK.md table row (S21b 16, S21c 6, S21d 24) — id exists, class equal, value equal (rel 5e-3 for the 4-sig-fig display) or UNAVAILABLE iff evidence value null, n equal.
2. Every prose decimal in BENCHMARK.md must equal some number in S21 JSONs/GATE_A.json (authored-number guard; links stripped).
3. Count claims: "8 measured, 8 UNAVAILABLE" / "2 measured, 4 UNAVAILABLE" vs summaries; "7 of 466 sealed frames" vs split; "Four post-freeze evidence files" vs len(costs.EXTRA).
4. Gate labels: Gate M NOT_MET_INPUT_READINESS, Gate RS NOT_MET, Gate A MET_AMENDED_Q16 + verbatim label "scale unverified, not setup-validated" from GATE_A.json; plain "Gate X: MET" forbidden.
5. about.json: equals about.build() regeneration; each row id/class/value equals evidence; summaries equal; Gate A verdict/label equal GATE_A.json; simulated rows carry "NOT spend"; no measured row in metres/m/s^2 (scale unverified).
6. About.jsx: no numeric literals outside identifiers/comments; compiles with the installed Next SWC (`jsx_check.cjs`, uses main checkout's Build/web/node_modules; test skips if absent). About.jsx is **unmounted** (no app route imports it).

## Files
- Build/benchmark/crosscheck.py (new), Build/benchmark/test_crosscheck.py (new, 4 tests incl. 5 md tamper cases + about/jsx tamper), Build/benchmark/jsx_check.cjs (new)
- evidence/S21/crosscheck.json (frozen output)
- BENCHMARK.md: replaced the "Not done here: cross-checking" line with the cross-check pointer and remaining limits.

## Commands (fresh)
- `python -B Build/benchmark/crosscheck.py` -> status PASS, checked 100, mismatches []
- `python -B -m unittest discover -s Build/benchmark -p "test_*.py"` -> Ran 28 tests OK (24 prior + 4 new); `test_about_jsx_compiles` ran (not skipped) -> OK
- `python Run-System/worker_timebox.py check` on TIMEBOX.json (see commit)

## Out-of-Owns scan (for owners; no mismatch found)
- Build/web/src (non-about): no benchmark numbers; home page bench SVG is labelled illustrative. Only CSS/fixture numbers (workspace fixture labelled non-physical).
- Build/library, Build/library/README.md, mystery_g.py, pendulum.py: Gate M/RS NOT_MET, SCALE_UNVERIFIED, WITHHELD labels consistent.
- Build/reports: no numeric benchmark claims found by grep.
- README.md: no benchmark numbers. final plan.html: score/cost numbers are planning estimates explicitly labelled "estimates, not results" (not benchmark claims).
- infra/modal/README.md:93 rounded RM02 timings/cost (1.4 s, 39.6 s, billed 30.0, $0.0103/$0.0113) and STATE.md:77 (2.52 s, 1176 tokens) are consistent with S21d rows; not machine-checked.
- evidence/S14/GATE_A.json: label/verdict consumed verbatim; not edited.

## Ponytail
Reuse: about.SOURCES/about.build/about.OUT, manifest.ROOT, costs.EXTRA, existing S21 JSON rows; Next's bundled SWC for JSX compile (no new dependency). Smallest complete: one read-only script + one test file; no generator changes, no About.jsx/about.json edits (already correct). Skipped: integer-in-prose checks (integers are ids/thresholds like 80%, Q15) except the explicit count claims; a pitch deck/video script does not exist yet, so not checked.

## Risks / limits
- Prose guard only covers decimals; a new authored integer claim would need a regex in crosscheck.py.
- Rel tolerance 5e-3 matches 4-sig-fig display; a tiny authored drift within 0.5% would pass the table check (exact drift still caught by existing test_errors/predictions/costs verbatim-table tests).
- JSX compile test depends on main checkout node_modules; skips elsewhere. About.jsx remains unmounted.

## Communication
Silent run; one completion message to controller as authorized.
