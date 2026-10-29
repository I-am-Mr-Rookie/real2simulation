# S15g-orch24 PLAN
Objective: S15g virtual instrument controls; trial measurements display provenance and uncertainty (fixture-first, visibly synthetic).
Lane/model: CLAUDE, anthropic/claude-sonnet-5-5 high (OpenCodex-managed, not polled). Parent project Meta AI Hackathon 91e441f8-e40c-4ec4-bea2-de7fa1582d97. Branch run/S15g-orch24 at .worktrees/S15g-orch24, base main 3935c04.
Issued 2026-10-29T15:03:51+00:00; deadline 2026-10-29T15:33:51+00:00; minute-25 cutoff 15:28:51.
Owns: Build/web/src/workspace/; tests/workspace/; evidence/S15/; Run-System/Runs/S15g-orch24/.
Acceptance: (1) trial measurements render value, uncertainty, unit, simulated label and source; (2) every number is Build/instruments output; (3) tests plus a 375px in-app-browser check.
Plan: reuse Build/instruments + contracts/fit/quantity via a generated JSON fixture; one pure reducer/view pair beside run controls; wire through existing react.mjs/view.mjs props.
