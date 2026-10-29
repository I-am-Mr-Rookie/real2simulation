# S09j-orch35 PLAN

- Run: S09j (controller contract S09j-orch35). Lane CLAUDE, assigned anthropic/claude-opus-5-5/medium; OpenCodex-managed, not polled.
- Issued 2026-10-29T16:00:45Z; deadline 16:30:45Z (Dhaka 22:30:45); minute-25 cutoff 16:25:45Z. Worktree started 16:02Z from main be06dda.
- Objective: consolidate S09a-i evidence into evidence/S09/CHECKPOINT.md (fixture vs real RM02/RM04/RM05, scale UNVERIFIED,
  Fallback 2), measured numbers with sources, known limits; fresh IAB check at 375px + desktop; fix only observed small visual defects.
- Owns: Build/web/src/viewer/; tests/viewer/; evidence/S09/; Run-System/Runs/S09j-orch35/.
- Temporary junctions (gitignored, removed at end): Build/web/node_modules -> canonical install; evidence/S09/local -> .worktrees/S09i-orch33/evidence/S09/local (real media, never committed).
- Checks: node --test tests/viewer; browser-smoke 375 + default; IAB real-scenes.html desktop + 375.
- No Modal/GPU, no deploys, no installs, no canonical control edits. In-app browser only.
