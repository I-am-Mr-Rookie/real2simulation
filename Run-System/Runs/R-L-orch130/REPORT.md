# R-L-orch130 — DONE (verdict CHANGES_REQUIRED: 1×P2, 2×P3)

Lane CLAUDE, step S18; model anthropic/claude-opus-5-5 medium; coding quota OpenCodex-managed; not polled.
Issued 2026-10-30T10:53:45Z; work started 2026-10-30T11:04:15Z (worktree created); stopped 2026-10-30T11:09:50+00:00.
Worktree .worktrees/R-L-orch130, branch run/R-L-orch130 from main 67e299a.

Review: evidence/reviews/R-L/REVIEW.md. Key: guest HTTP surface leaks no answer field/record (only /cases/0 shares
the challenge record and it is withheld), but the answer value g=9.81 is recoverable from the served projectile
trace (same g/seed/duration/dt) and from committed repo evidence that becomes public at submission (P2). P3s: per-request
full revalidation cost; 64 MiB guest object cap.

Files: evidence/reviews/R-L/{REVIEW.md,library-tests.txt,probe_guest_exposure.py}; this run's PLAN/TIMEBOX/REPORT.
Commands: `python -B -m unittest discover -s tests/library -t tests/library` -> 81 tests OK (97 s);
`python -B evidence/reviews/R-L/probe_guest_exposure.py` (from worktree root) -> 2 playable, 1 metadata-only, 15 UNAVAILABLE; no replay hash/acceptance bytes served;
read-only fixture inspection of acceptance.json and objects/sha256.

Ponytail full applied: reused existing `load_guest()` as the oracle instead of reimplementing the projection; one small probe
script kept as evidence; no source edits (review-only, other lane). Skipped: browser/UI render, /lab internals, Build/web.
Risk: if the demo calls Mystery-g "blind"/"answer withheld", judges reading the public repo can contradict it.
Next: owner/controller pick P2 fix (relabel vs /lab server-owned randomized g) and dispatch to S18 owner lane.
Costs: no API/GPU/network spend. Tokens: unknown (not observable). Communication: silent; one completion line to controller.

