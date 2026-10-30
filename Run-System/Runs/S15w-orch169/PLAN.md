# S15w-orch169 PLAN
Lane CLAUDE, anthropic/claude-opus-5-5/high (OpenCodex-managed; not polled). Issued 2026-10-30T23:09:52Z; deadline 23:39:52Z; cutoff 23:34:52Z. Branch run/S15w-orch169 from main 67a13878.

Objective: one presentation-only UI pass (myfront 1.2.0 round-3 + make-interfaces-feel-better) over public pages + workspace shell. Direction: default Mobbin R1/R2/R3 (layout/hierarchy only).

Owns: Build/web/src/ (NOT workspace/controller.mjs, workflow.mjs, interview logic); tests/workspace/; tests/shell-workspace/; evidence/S15w/; Run-System/Runs/S15w-orch169/.

Approach (Ponytail): CSS-only edits to the three existing stylesheets (app/styles.css, lab/lab.css, workspace/workspace.css) + library inline CSS string; no markup/label/behaviour changes, no new tokens beyond what the pass needs.

Checks: node --test workspace/shell-workspace/web-private/web-workspace-api; npm run build; rebase on main; stage.py web + railway up (DEV); TIMEBOX check.
