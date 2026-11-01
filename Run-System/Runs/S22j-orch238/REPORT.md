# S22j-orch238 REPORT: DONE

Lane CLAUDE, anthropic/claude-opus-5-5 high (assigned). OpenCodex-managed; not polled. Issued 2026-11-01T07:22:03Z,
worktree 07:22:21Z, work stopped 2026-11-01T07:27:46+00:00. Tokens/cost: not observable. No GPU, paid call, deploy, account or product code.
Branch run/S22j-orch238 from main 341bc50c.

## Deliverable
evidence/qa/claude/S22j-GATE-D-DECISION.md: per-criterion verdicts with file:line evidence for Gate D (a) 3.1-3.8 + streak
and (b) 2.1-2.6, S22f D1-D11 final state, nine disclosure limits, freeze recommendation (may / must not change).

## Decision (summary)
- (a) private flow: MET on DEV rehearsal (fresh 3/3 streak, 21.2/19.5/21.5 s, fit executed server-side, report body
  verified); NOT MET of record (no judging URL). 3.6 N/A (no patch/search in signed-in UI).
- (b) guest library: MET on DEV rehearsal (S22g); NOT MET of record; not re-run on web 45fbd535.
- Overall PASS-on-DEV, of-record PENDING S23a/b/c (protocol line 100 requires the judging URL). Library-only fallback
  (QUEUE.md:606) becomes binding only if S23a approval is missing or S23c fails by freeze. README upload limits needed in
  both branches.
- Structural risk flagged: private workspace only exists when Railway env name is "dev" (dev-scenes.mjs:6-9); S23 must
  promote the DEV shape or add an explicit env flag before the freeze SHA.

## Fresh checks
- Read S22f, protocol, five S15 REPORTs, three RUN.md files in full (line-numbered).
- Viewed S22i r1-result.png, r1-report.png, i-d4-blank.png, i-o2-logged-out.png; strings matched RUN text and source.
- rg cross-checks: 13 quoted snippets found in their cited files (S22g/h/i RUN.md, protocol, QUEUE.md, layout.mjs,
  view.mjs, S15bb REPORT); label sources located (analysis.py:39-40,111; view.mjs:67,97,118; trajectory-replay.mjs:7;
  PrivateWorkspace.mjs:23); rg "SPEND_PAUSED" Build/api -> 0 hits; rg patch in PrivateWorkspace.mjs -> no control.
- python Run-System/worker_timebox.py check Run-System/Runs/S22j-orch238/TIMEBOX.json (result in commit step).

## Ponytail (full) applied
- Reuse: S22f table structure and D-IDs, protocol criteria numbering, QA RUN.md evidence as-is; no new probe or browser
  run (S22i already produced the fresh streak on the same build).
- Smallest complete: one decision file + run receipts; no edits to canonical controls, QUEUE or product code.
- Skipped: re-driving the browser; re-reading S22b-e evidence (S22f already judged it); viewing the remaining S22g/h/i
  screenshots (r2/r3-result, offline/reload, rm04); verifying deployed SHAs (S22i records them "per controller").

## Risks / limits
- All Gate D evidence is DEV rehearsal with Clerk test accounts and scripted timings; of-record verdict needs S23.
- (b) not re-run after S15ba-bd web changes. Row S15be is in the canonical working QUEUE.md but not in committed main.
- S22f D9 (S22e timestamp) not rechecked.

Communication: silent; one completion message to controller chat per contract.

