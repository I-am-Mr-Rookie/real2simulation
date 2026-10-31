# S15az-orch227 PLAN

- Task: QUEUE S15az, Gate D D1 + D6 (evidence/qa/claude/S22f-GATE-D-JUDGEMENT.md rows D1, D6).
- Lane/model: CLAUDE, anthropic/claude-opus-5-5 high (OpenCodex-managed; not polled). Single worker.
- Issued 2026-10-31T16:23:01Z; deadline 16:53:01Z; minute-25 cutoff 16:48:01Z.
- Objective: after the known-size answer, run the existing pure fitter (Build/fitter/core.py) server-side in Build/api/workspace on the stored RECORDED prefix points of the owner clip, scale from the user's answer over a RECORDED reference px length (from S07 evidence), held-out points only score the fit; show fitter g +- u, residuals, rmse/dof, held-out residuals only after the answer; Fit stage done.
- Owns: Build/api/workspace/; Build/web/src/workspace/ (not status.mjs, layout.mjs); tests/api-workspace/; tests/workspace/; tests/web-workspace-api/; evidence/S15az/; this run folder.
- Not: POST /api/workspace/fit (fitter.api.handle trust boundary), RM04/scene paths, S15ba files, deploy.
- Checks: python unittest (api-workspace incl. new test_live_fit.py), node --test suite, npm run build.

