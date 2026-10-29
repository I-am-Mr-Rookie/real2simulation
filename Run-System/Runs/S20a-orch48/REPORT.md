# S20a-orch48 — DONE (contract only, not Gate C)

CODEX-2 / step S20; assigned gpt-6.1-sol, medium. OpenCodex-managed; not polled.
Exact runtime model/effort identity, tokens and coding dollars are unobservable.
Parent project Meta AI Hackathon `91e441f8-e40c-4ec4-bea2-de7fa1582d97`.
Controller `01a1882d-3481-7ce3-8f88-45c942e341cd`.

Issued 2026-10-29T21:52:08+00:00; first observed execution clock 21:53:11Z;
implementation/acceptance work stopped **22:01:28Z**; report 2026-10-29T22:02:25+00:00.
Cutoff 22:17:08Z; deadline 22:22:08Z (Oct30 04:22:08 Dhaka).
Early DONE: every assigned S20a acceptance criterion is met; no unfinished owned
implementation. TIMEBOX.json captures actual stop/report clocks; no extension.

Worktree: `C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.worktrees/S20a-orch48`
Branch `run/S20a-orch48`, base main `7fbf29f`. Main advanced independently to
`5e95fe216f129cb35295637ba36de0b4406aec45` at the final scope check.
Controller integrates; worker did not change canonical controls, merge, push or deploy.

## Result / acceptance

- `Build/guardrails/CONTRACT.md`: one read-only accounting contract over existing
  agent, GPU run-envelope, pipeline reservation and scene-cost ledgers. Stable request
  identity, disjoint historical coverage, parent/child envelope folding, conservative
  unbilled/provisional liability and final reconciliation prevent omission/double count.
- `Build/guardrails/accounting.py`: 66-line standard-library Decimal reference.
  Confirmed history + unresolved/final current liabilities + candidate count against
  **strictly below $120** routine stop; $30 demo reserve is not routine headroom.
  Unknown history, bad money, duplicate IDs and mixed providers refuse; estimates/
  partial bills cannot release reserves. No I/O, persistent store or live admission.
- Contract defines atomic pre-dispatch reserve lifecycle, retry/crash/stop/overrun
  rules, independent Modal $30 no-overage and AWS $50 EC2 spot-only envelopes.
- Upload quota contract: **1 accepted reconstruction upload/authenticated user/UTC day**,
  explicitly a reversible implementation default, not a supplied owner capacity fact.
  Reuses existing file/session limits; resume/idempotency does not consume twice;
  new failures do not grant automatic refunds; missing/corrupt quota state pauses.
  Public precomputed library/viewer remains exempt and cannot trigger paid work.
- `infra/failover/CONTRACT.md`: reuse existing AWS adapter, stay disabled by default,
  no cloud switch/resource changed. Existing approval receipts are reusable, not a
  redundant consent request.
- `tests/guardrails/test_accounting.py`: 17 tests, including direct read-only
  compatibility projections of existing tracked Meta/scene-cost receipts.
- `evidence/S20/S20a/`: test transcripts, synthetic below/at-cap examples,
  acceptance matrix and scoped staging check. No copied media or secrets.

The exact QUEUE acceptance is satisfied: Meta commitment includes confirmed
historical usage, pending requests and conservative estimates. Synthetic saved
oracle: 110 history + 2 pending + 3 estimate + 4 final + 1 candidate = 120;
routine arithmetic condition FALSE. These are test values, NOT real balances.

## Fresh verification — Python 3.14.5

| Command | Result | Evidence under evidence/S20/S20a/ |
|---|---|---|
| `python -m unittest discover -s tests/guardrails -v` | 17 PASS | accounting-tests.txt |
| `python -m unittest discover -s Build/gpu -p test_cost_log.py -v` | 5 PASS, unchanged | existing-cost-log-tests.txt |
| `python -m unittest discover -s Build/gpu -p test_aws_adapter.py -v` | 7 PASS, unchanged | existing-aws-gates-tests.txt |
| `python -m unittest discover -s tests/pipeline -v` | 52 PASS, unchanged; synthetic/fake paid transports | existing-pipeline-tests.txt |
| `git diff --cached --check` + exact Owns-prefix/bytecode assertion | PASS | scope-check.txt |

**81 tests passed**, no dependency installs, no failed acceptance checks.
Expected invalid-event diagnostic inside the passing pipeline negative test is not
a failing check. The timebox validator is run during report finalization and its
output saved as timebox-check.txt.

## Ponytail full — concrete application

Read installed `.../ponytail/5.3.3/skills/ponytail/SKILL.md` and applied full mode.
Reused existing ledger field names, conservative GPU upper bounds, upload policy,
error code SPEND_PAUSED, AWS adapter and tests. The only new executable behaviour
is pure financial arithmetic; no new journal, wrapper service, dependency, provider
client, launcher, queue, endpoint or duplicated upload store.
Impact/caller search found no pre-existing guardrails module/callers; all existing
callers intentionally unchanged. Scope staging initially included local bytecode
via forced directory add; it was removed from index before finalization, not committed.

## Skips, risks and controller handoff

**Not implemented/claimed:** live global cap, durable quota counter, global locking,
source-set reconciliation, guest-route enforcement or an AWS switch. Those are
S20b/S20c/R-C/S20d work, not incomplete S20a acceptance. No fresh live balance,
historical aggregate total, provider pricing, resources or end-to-end billing tested.

Important source bottlenecks for S20b: Meta recorder appends after response and
sums local estimates; GPU reserve read/check/append is not cross-process atomic;
recent cost-log billed rows may still accrue. The pure helper cannot fix those
by import and must not be presented as safe live admission. History coverage/
settlement evidence and credit verification remain caller obligations.
Adapter projection/folding is specified, not a new canonical ledger or automatic
reconciliation of all heterogeneous historical files.

Next: controller reviews/commits integration under existing protocol, then S20b
wires serialized admission at every supported paid boundary (or disables unsupported
live routes), quota and library exemption. Record the reversible quota default in
canonical decisions if accepting it. No new owner approval/question needed for
this offline contract; no provider/model/credential/policy change.

New Meta/Modal/AWS/other paid calls: **0**; new paid job spend/reservations: **$0**.
Historical balances/ongoing unrelated infrastructure charges: not verified, not zero.
Coding quota: OpenCodex-managed; not polled. No publication/upload/auth/terms/purchase.

Communication: silent except one higher-priority mandatory Ponytail/tool-work
notice; one authorized concise completion callback to controller. No optional
progress narration or duplicated report; any mandatory final limitation line is
a higher-priority Ponytail exception to the one-line worker format.
