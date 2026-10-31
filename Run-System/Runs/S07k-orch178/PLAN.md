# S07k-orch178 PLAN — resume S07k: frozen v2 rule on OWN07–OWN11

- Lane CLAUDE, anthropic/claude-opus-5-5 medium (OpenCodex-managed; not polled). Issued 2026-10-31T00:04:39Z, deadline 00:34:39Z, cutoff 00:29:39Z.
- Base main cc644ac1. Worktree .worktrees/S07k-orch178, branch run/S07k-orch178.
- Objective: run the UNCHANGED pre-registered v2 rule (Run-System/Runs/S07k-orch174/PLAN.md; constants MOVE_PX 4, STATIC_PX 6,
  SCALE_N 5, SCALE_MIN 3, WIDTH_TOL 0.10, DECEL 0.5, N_MIN 8, held-out PASS ≤ 6 px) on OWN07–OWN11.
- Pre-registered changes (written before any OWN07–11 g is computed): (1) TRACKS/SCENES gain OWN07–OWN11 ->
  evidence/S07/S07j/track-ownXX.json, scene names from S07h PENDING; (2) assert rule constants equal the orch174 values;
  (3) assert OWN01–OWN06 rows+clips SHA-256 = 41ce6dd7268c7658f98fef97f5724226b8ea5096e77ead9b3dedf06584a14982 (orch174 results),
  in run() and --self-check; (4) table shows v1 "pending S07h" where S07h has no row; pending block cleared.
- One real run; no rule/parameter edits after results. README: 11-clip table, coverage 1u/2u, held-out count, abstains,
  05a–d repeatability (05b = OWN06 sheet partly down, flagged), robustness (nosheet, clutter, lowres 478x850), forking-paths caveat.
- Checks: --self-check; python -B -m unittest discover -s tests/measurement -t tests/measurement; worker_timebox check.
- Owns: evidence/S07/S07k/; Run-System/Runs/S07k-orch178/. No Modal/GPU/Meta, no video/frames to any model.
