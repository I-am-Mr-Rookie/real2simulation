# S15b-orch15 PLAN
Objective: workspace layout + viewport mount (QUEUE S15b). Acceptance: viewer used through its public interface; no viewer edits.
Owns: Build/web/src/workspace/; tests/workspace/; evidence/S15/; Run-System/Runs/S15b-orch15/.
Deps: S15a (accepted). Fixture-first: visibly synthetic only. Lane CLAUDE, anthropic/claude-sonnet-5-5 high.
Issued 2026-10-29T11:30:40Z; deadline 12:00:40Z; minute-25 cutoff 11:55:40Z. Branch run/S15b-orch15, worktree .worktrees/S15b-orch15.
Plan: pure layout model -> mount controller over injected adapter -> h-injected markup + React binding + CSS -> tests -> SSR evidence.
