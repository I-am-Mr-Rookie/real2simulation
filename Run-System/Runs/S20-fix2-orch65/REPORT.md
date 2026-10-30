# S20-fix2-orch65 — DONE (scoped offline fix; NOT Gate C clearance)

CODEX-2 / S20; assigned gpt-6.1-sol/high. OpenCodex-managed; not polled.
Exact runtime identity, token use and coding dollars are not independently observable.
Parent project Meta AI Hackathon 91e441f8-e40c-4ec4-bea2-de7fa1582d97 per delegation.
Canonical root: C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon.
Worktree: canonical root/.worktrees/S20-fix2-orch65; branch run/S20-fix2-orch65.

## Timing / custody

Issued 2026-10-30T05:00:36Z; cutoff 05:25:36Z; deadline 05:30:36Z
(11:30:36 Dhaka). All implementation and acceptance checks stopped 05:24:22Z,
before cutoff. Report receipt: 2026-10-30T05:25:17Z. Fully verified scoped DONE may finish early.
No incomplete early-stop exception or deadline extension requested.

Started from rejected/unverified ad99589 on run/S20-fix-orch63; critically reviewed
its gaps, retained useful accounting/locking work, and supplied the missing tests,
fixtures, projection repairs and AWS reservation. Rebased first onto dbdc059,
then again onto current main (35c9a90 at rebase). Fresh suites below ran AFTER the
final rebase. Code checkpoint b1fa06d; final receipt/evidence follow-up commit.
Historical predecessor report/timebox remain untouched, including its timing failure.
No merge, canonical control edit, push, deployment, schedule or additional worker.

## Fixed / reach

- H1/H2/M1: shared segment/reconstruct reserve calls require_reconstruction inside
  one canonical cross-process O_EXCL lock, with atomic/fsynced global journal
  persistence before local append or dispatch. Linked worktrees share Git common
  root state. Existing local $1/two-job checks remain and cannot be reset by a new
  run directory. Missing/corrupt state, lock/write failure and corrupt ledgers
  become nonretryable StageError SPEND_PAUSED. Failed append keeps the global debt.
- Projection: inventory S05/S06/S07/S12/S13/S14 and Run-System run GPU ledgers;
  fold reservation/result/billing events, reject ambiguous/conflicting app IDs
  and duplicate receipt/journal IDs, retain max(reserved, estimate, bill). Parent
  job envelopes use max(parent, SUM(child worst costs)), not parent + children.
  Linked scene logs and pipeline artifacts bind app IDs, contribute upper bounds,
  and carry source hashes. Persisted source inventory makes later disappearance
  fail closed. Legacy release hints never release outstanding reservations.
- M2: unknown top-level snapshot fields rejected; AWS bucket required before
  enabling AWS. AWS selector reuses the same canonical lock/projection/journal,
  rechecks S20b and $50 gross/credit/budget headroom, and durably reserves AWS plus
  any Meta candidate before returning a plan. Repeated receipts cannot refill
  headroom. Result remains launched=False; no cloud resource is started.
- L2: liability rounding stays upward; available credit uses ROUND_FLOOR.
- Fixtures use isolated temporary runtime receipts/journals. Pipeline retry test
  now verifies that a failed paid identity is NOT automatically submitted twice;
  its reservation remains consumed. Clean raw-result cache is still tested
  without another paid admission.

Runtime documentation: Build/guardrails/ADMISSION.md and infra/failover/CONTRACT.md.
No live receipt/empty journal was bootstrapped. Trusted reconciliation must create
and maintain those server-owned files; never delete a journal to regain capacity.

## Fresh checks

- python -m unittest discover -s tests/pipeline -v: **52 PASS**.
  evidence/S20/pipeline-fix2-tests.txt
- python -m unittest discover -s tests/guardrails -v: **64 PASS**.
  evidence/S20/guardrails-fix2-tests.txt
  Includes G1 three fresh directories, G3 corrupt ledger mapping, C1 real-process
  concurrent $4 admissions, X1 unknown provider, R1 rounding, A15 repeated AWS,
  missing state before transport, crash/write retention, duplicate identities,
  linked-worktree resolution, scene-log overrun/missing known source, child
  envelopes and no repeated credit debit.
- python -m unittest discover -s Build/gpu -p test_aws_adapter.py: **7 PASS**.
  evidence/S20/aws-adapter-fix2-discovery-tests.txt
  Initial module-style invocation failed because that existing test imports
  aws_adapter as a top-level module; original failure is preserved separately in
  aws-adapter-fix2-tests.txt. Correct discovery invocation passed; no source bypass.
- Real canonical read-only projection: **27 files / 29 source references**,
  outstanding conservative Modal $11.80000000, Meta $4.47405600, AWS $0.
  evidence/S20/inventory-fix2.json contains actual source hashes. These are ledger
  liabilities, NOT current balance, final billing, available credit or admission
  proof. Synthetic history/credit placeholders were only used to inspect projection;
  no live runtime snapshot was written.
- git diff --check: PASS. Timing validator result is saved beside this report.

Unchanged R-C probes.py intentionally asserts the old findings (and directly calls
the live-root reserve); it was NOT rerun against canonical runtime. Its probe cases
are migrated into isolated regression tests rather than retaining expected bugs.

## Ponytail full / limits

Read and applied installed 5.3.3 Ponytail full. Reused liability_usd,
require_reconstruction, existing GPU reserve caller and AWS adapter, with stdlib
locking/atomic JSON; no dependencies, parallel reservation service, provider client
or speculative API/HTTP layer. Only named owned files staged (no caches).
Silent-workflow exception: mandatory initial developer progress/skill notices.
One authorized completion pointer goes to the controller; no owner question needed.

M3 DEFERRED: Build/agent/record_muse.py::reserve/record still needs global locked
Meta admission + durable reserve BEFORE its provider transport; its est-only local
cap is insufficient. That file was NOT edited (another worker owns Build/agent).
Standalone GPU CLIs and future HTTP upload routes also need reviewed integration
before a universal cap/Gate C claim. Other producers must honor serialization and
trusted coverage; source hashes do not establish financial truth or completeness.

Skipped live Modal/Meta/AWS calls, spend, secrets, installs and deployments.
New service spend $0; existing account headroom/billing/health and end-to-end
shutdown remain UNVERIFIED. AWS flag stays unchanged/default OFF. O_EXCL crash
locks require verified manual recovery; unresolved reservations intentionally
remain charged and may conservatively pause useful work. Gate C needs independent
re-review and deferred call-site closure; no live safety or physical success claimed.
