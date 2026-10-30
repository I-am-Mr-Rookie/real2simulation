# R-A-recheck3-orch96 — Gate A fix5 cross-vendor review

- Objective: independently review fix5 at `0a18072251360c971ca80b8e0c67fa27ce918fa1`; close or re-rate F1-R2 and verify Q16 reporting without modifying product sources.
- Assigned route: `gpt-6.1-sol/high`, CLAUDE cross-vendor review lane, step S14. Runtime model identity not separately observable. OpenCodex-managed; not polled.
- Parent controller: `01a1882d-3481-7ce3-8f88-45c942e341cd`; project supplied by launcher: Meta AI Hackathon `91e441f8-e40c-4ec4-bea2-de7fa1582d97`. No claim of independent app-project binding verification.
- Canonical root: `C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon`.
- Isolated checkout: `.worktrees/R-A-recheck3-orch96`, branch `run/R-A-recheck3-orch96`, created from main before writes.
- Issue: 2026-10-30T06:47:20+00:00. Implementation cutoff: 2026-10-30T07:12:20+00:00. Deadline: 2026-10-30T07:17:20+00:00 (13:17:20 Dhaka). Verified complete review may finish early; a CHANGES_REQUIRED review can be DONE while Gate A remains unaccepted.

## Exact Owns

1. `evidence/reviews/R-A/RECHECK-fix5.md`
2. `evidence/reviews/R-A/recheck-fix5/`
3. `Run-System/Runs/R-A-recheck3-orch96/`

## Acceptance and affected surfaces

1. Reuse prior reviewer strings and production `validate_response`, `safe_reply`, trial retry/tool-only fallback, saved gate turn runner; check narrative, question prompt, chip label and candidate rationale. Independently check the oracle and private-use CITE forgery.
2. Replay the saved packet as a function (never its S14-writing CLI), observe actual setup-validator calls, verify 30 saved live turns, unchanged rendering, zero oracle-flagged invention, exact Q16 label and 0/10 setup alongside 10/10 numeric-contract specs.
3. Probe bounded natural numeric-language gaps, especially the worker-disclosed label-adjacency residual; write a severity-based CLEAR/CHANGES_REQUIRED review, fresh reproducible evidence, timing validation and a scoped commit.

Ponytail full: reuse existing review harness patterns and stdlib assertions; no product fixes, new dependencies, broad blacklist, new model calls, credentials, physical/scale claims or control edits. Tests, fixtures, exports and config are inspected only; no callers change. Protect source/evidence hashes, deny network and restrict probe writes to owned review output.
