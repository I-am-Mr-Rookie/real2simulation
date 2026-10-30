# UI-e-orch88 PLAN

- Objective: apply evidence/ui/audit-orch82/DEFECTS.md (6 P2, 7 P3) with targeted fixes only; visually verify UI-c-orch73 viewer chrome; diagnose blank tests/viewer/browser-smoke.html.
- Lane/model: CLAUDE, anthropic/claude-opus-5-5 high (OpenCodex-managed; not polled). Parent project Meta AI Hackathon 91e441f8-e40c-4ec4-bea2-de7fa1582d97.
- Issued 2026-10-30T06:20:39Z; deadline 06:50:39Z (Dhaka 12:50:39); minute-25 cutoff 06:45:39Z.
- Owns: Build/web/src/app/styles.css; Build/web/src/app/(public)/; Build/web/src/shell/; Build/web/src/workspace/; Build/web/src/viewer/ (chrome styles only); tests/workspace/; tests/viewer/browser-smoke.html; evidence/ui/orch88/; Run-System/Runs/UI-e-orch88/.
- Checks: node --test tests/workspace/*.test.mjs green (+1 display-rounding test); in-app browser desktop + 375 (scrollWidth==clientWidth); computed contrast/focus values.
