# UI-c-orch73 PLAN
Objective: finish-pass restyle of virtual lab + 3D viewer chrome to shared "bold technical" direction, consuming --r2s-* tokens with fallbacks; no flow/behavior rewrites; truth labels intact.
Owns: Build/web/src/lab/; Build/web/src/app/(public)/lab/; Build/web/src/viewer/; tests/lab, tests/viewer (read/run only); evidence/ui/orch73/; Run-System/Runs/UI-c-orch73/.
Checks: (1) node --test tests/viewer/*.test.mjs + lab UI tests green; (2) IAB desktop + 375px screenshots, scrollWidth==clientWidth; (3) truth labels still rendered.
Window: issued 2026-10-30T05:18:26Z, cutoff 05:43:26Z, deadline 05:48:26Z. Model anthropic/claude-opus-5-5/high (OpenCodex-managed; not polled).
