# S09e PLAN — Implement pixel-ratio and detail budgets

- Lane/model: CLAUDE, requested Opus 5.5 medium (orchestrator-delegated Codex desktop chat). UTC start 2026-10-27T19:23:35Z.
- Depends: S09d DONE. Branch run/S09e at .worktrees/S09e from main fd5d508.
- Objective: one pure, deterministic device-budget function (DPR cap + detail tier + point cap) applied by the three renderer at mount.
- Owns: Build/web/src/viewer/; tests/viewer/; evidence/S09/ (plus serialized control updates on main).
- Acceptance: "DPR cap and reduced detail are deterministic per device budget."
  1. node --test viewer suites incl. new render-budget tests (hand-derived literals, boundaries, invalid inputs) — all pass.
  2. Renderer test: reduced-budget device sets capped pixel ratio, decimates a large model deterministically, exposes handle.budget.
  3. Browser smoke still ok/overlaysOk; red-green mutation of the cap/threshold caught.
- Skills: Superpowers test-driven-development (+ writing-good-tests.md), verification-before-completion; Ponytail (smallest change).
- Out of scope: mobile_asset_id loading (loader/model change), idle/hidden pause (S09f), 375px layout (S09g), real-device fps.
