# S22a-orch70 REPORT — PARTIAL

- Lane/model: CLAUDE; assigned anthropic/claude-opus-5-5/medium; OpenCodex-managed, not polled. Tokens/cost: unknown (unobservable). Meta/GPU spend: $0.
- UTC: issued 2026-10-30T05:09:38Z; started 05:10:26Z; implementation cutoff 05:34:38Z; work stopped 05:39:38Z (deadline). See TIMEBOX.json.
- Base main a2fa169; branch run/S22a-orch70; worktree .worktrees/S22a-orch70. Parent project 91e441f8-e40c-4ec4-bea2-de7fa1582d97.

## Result
Gate D QA protocol + checklist written. **Gate D NOT met / not assessed.** PARTIAL because dependency-gated steps
(S15k/l, S16, S17f, S19d, S20c/d, S14g/h, S04h, S18, owner candidate approval) are unverifiable now.

Files (Owns only):
- evidence/qa/claude/GATE_D_PROTOCOL.md — authority/preconditions, dependency gate table, guest walkthrough (S22b),
  fresh-account x3 with <5:00 streak rule (S22c-e), 375px/auth (S22g), retry/spend-cap/report (S22h), recheck/decision
  (S22f/i/j), JSON evidence format for S22b-i, BLOCKED-BY <row> markers (15).
- evidence/qa/claude/S22a-dev-guest-probe.md — read-only HTTP GETs of Railway dev web.
- Run-System/Runs/S22a-orch70/{PLAN.md,TIMEBOX.json,REPORT.md}.

## Findings (new)
1. Dev /library returns 200 but "No demos are published yet" and "Viewer not connected" -> Gate D (b) guest demo
   currently FAILS even on dev. S18 (library demos, all TODO) is a real Gate D prerequisite though not in S22's plan dep list.
2. Guest /workspace/<unknown> -> 404 (consistent with auth CONTRACT uniform-404); / and /sign-in 200 without redirect.
3. No owner candidate-deploy approval on record; S23a is a different, later promotion approval.

## Checks (fresh)
- Protocol JSON template parses (ConvertFrom-Json, 19 keys). BLOCKED-BY count 15.
- QUEUE statuses read at a2fa169 (S15k/l TODO, S16 TODO, S17f TODO, S19d TODO, S20c PARTIAL, S20d TODO, S14g PARTIAL, S18 TODO).
- Dev probe: 5 GETs, UTC 05:18-05:20; HTTP-only, not browser-rendered; deployed SHA not read.
- python Run-System/worker_timebox.py check TIMEBOX.json -> "TIMING PASS; controller must separately verify evidence and any exception" (reported_at 2026-10-30T05:39:50+00:00).

## Ponytail (full) applied
- Reuse: plan Gate D wording, JUDGE_RUBRIC weights, auth CONTRACT 401/403/404 rule, STATE dev URLs, QUEUE rows; no new rubric.
- Smallest complete: one protocol file + one probe note; evidence format as inline JSON schema example, not a separate schema/tooling.
- Skipped: browser-rendered walkthrough (S22b's job, Sonnet lane), sign-in test (needs approved account), any deploy/account/terms,
  HAR capture, product edits.
- Risks: S18 omission from S22 deps could leave Gate D blocked late; dev evidence must never be counted as Gate D of record.

## Communication
Silent run; one completion line to controller chat as authorized. No owner questions raised (candidate approval is already a known S22 precondition).

## Next
Controller: add S18 (library demos) as an explicit S22b/Gate D prerequisite; S22b after deps; obtain written candidate-deploy + account approvals before S22c.

