# UI-a-orch71 PLAN

- Lane/model: CLAUDE, anthropic/claude-opus-5-5 high (OpenCodex-managed; not polled). Parent project 91e441f8-e40c-4ec4-bea2-de7fa1582d97.
- Issued 2026-10-30T05:16:24Z; deadline 05:46:24Z; cutoff 05:41:24Z. Base main 6be0934; branch run/UI-a-orch71.
- Objective: shared --r2s-* design tokens + fonts, restyle public shell (landing, library, nav/footer, sign-in/up framing, not-found, error). No flow/behaviour/auth changes; truth labels kept verbatim.
- Owns: Build/web/src/app/styles.css, layout.jsx, not-found.jsx, error.jsx, (public)/page.jsx, (public)/library/, (public)/sign-in/, (public)/sign-up/, src/shell/, src/auth/ (presentation only: new appearance.js), evidence/ui/orch71/, Run-System/Runs/UI-a-orch71/.
- Checks: shell test_contract (python unittest), auth node tests, next build + shell smoke, IAB desktop+375 screenshots / no horizontal scroll, AA contrast of token pairs.
