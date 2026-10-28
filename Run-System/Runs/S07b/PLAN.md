# S07b plan

Start UTC: 2026-10-28T07:29:06Z. Stop by 07:59:06Z; no new implementation after 07:54:06Z.
Lane: CODEX-1; requested gpt-6.1-sol/medium; actual runtime identity not exposed.
Base: 4bbae8ba9dbbb386794f050d4287eb21aea99d86. Branch run/S07b, isolated managed worktree.

Objective: implement an explicit local SAM 3.1 multiplex predictor adapter and
strict training-prefix response boundary, without executing models or footage.

Owns ONLY: Build/measurement/tracking.py; Build/measurement/TRACKING.md;
tests/measurement/test_tracking.py; evidence/S07/S07b/; Run-System/Runs/S07b/.
Shared inputs, controls, dependencies and main read-only. Controller integrates;
leave commits unmerged. No subagents.

Checks: red/green response/transport tests; S07a regression and S07a integration
with synthetic custody suffix; lazy import/no execution defaults; strict diff.
Ponytail full: reuse frozen Frame, stdlib dataclasses/JSON and already-installed
NumPy for vectorized boolean-mask centroid; no framework, remote transport or new
dependency. No metric calibration, clock inference or held-out input to predictor.

Read current canonical DISPATCH and AGENTS, relevant controls and S07a/S07r receipts;
read Ponytail, Superpowers TDD and verification-before-completion. Primary upstream
README, release, builder, shared predictor, video inference, notebook and licence
checked before choosing local SAM3.1 interface. This is not a licence acceptance.
