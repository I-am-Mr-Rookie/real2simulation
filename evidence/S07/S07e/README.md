# S07e evidence

- `actual-gate-m.json`: actual-source eligibility/abstention evaluation, NOT
  synthetic g, measured accuracy, physical coverage or parent-gate success.
- `verify_sources.py` / `source-integrity.json`: fresh evidence hashes and
  canonical/worktree content comparison (normalizing Windows line endings only).
- `gate-command.txt`: actual evaluation exit1; honest insufficient input result.
- `reproduction.json`: two runs byte-identical, both exit1.
- Full RED/GREEN command outputs live in `Run-System/Runs/S07e/`.

Current raw media not opened/hashed and no SAM/runtime invoked. S02i partial
flight remains useful but not qualified. R-M/S07f follow; no fallback enacted.
