# S15ae-orch191 PLAN
Objective: left rail -> activity bar (Q21 spec section 6): icon rail always visible, one current pane, toggle/click/hover-preview/pin/escape, persisted, 375 drawers; pure reducer + node tests; web redeployed to Railway DEV.
Owns: Build/web/src/shell/; Build/web/src/workspace/workspace.css; tests/shell-workspace/; evidence/S15ae/; Run-System/Runs/S15ae-orch191/.
Lane CLAUDE, anthropic/claude-opus-5-5/medium (OpenCodex-managed; not polled). Issued 2026-10-31T07:22:58Z, deadline 07:52:58Z, cutoff 07:47:58Z.
Checks: node --test 4 suites; npm run build; static SSR render 1280 open/collapsed/preview + 375; Railway DEV web SUCCESS.
