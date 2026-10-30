# R-C cross-vendor review — Gate C cap accounting + library exemption

Reviewer: R-C-orch60, anthropic/claude-opus-5-5 high (cross-vendor vs Sol-authored S20a/b/c). Read-only.
Base: main 53e63d7. Scope: Build/guardrails/{CONTRACT,ADMISSION}.md, accounting.py, admission.py, failover.py,
infra/failover/CONTRACT.md, Build/gpu/aws_adapter.py, tests/guardrails/, evidence/S20/, S20a/b/c REPORTs,
plus callers Build/pipeline/gpu_stages.py::reserve, Build/agent/record_muse.py::reserve, Build/web/src/app.

## Verdict: **CHANGES_REQUIRED** (for Gate C). The offline guard module itself is CLEAR.

The accounting/admission/failover code is correct and fail-closed for everything it is given, but it has
**zero callers** (rg of Build/ and infra/ outside Build/guardrails: no hits). The only live paid entry points
still use per-file local caps that a fresh path resets. Gate C (a live global cap) is therefore not met.

## Evidence

- `python -m unittest discover -s tests/guardrails -v` -> 47 tests OK ([guardrails-tests.txt](guardrails-tests.txt)).
- `python evidence/reviews/R-C/probes.py` -> 53 probes, 0 expected-safe failures, 7 observed findings
  ([probes-output.json](probes-output.json); temp files only, no network, no spend).
- Probes were started by predecessor R-C-orch57 (bf5d9bd, unverified) and re-run/extended here (A15, X1, C1).

## Findings

| ID | Sev | Finding | Evidence |
|---|---|---|---|
| H1 | **High (blocks Gate C)** | Guard not wired: `require_reconstruction`/`select_provider` have no callers in Build/pipeline, Build/web or Build/agent. Contract says so (ADMISSION.md "must not be described as a live global cap"). | rg: no callers; ADMISSION.md integration section |
| H2 | **High** | Live GPU boundary `gpu_stages.reserve` caps $1/2 jobs **per ledger file**; three fresh run dirs each admitted $1 (G1). Corrupt ledger raises JSONDecodeError, not SPEND_PAUSED (G3; fails closed but unmapped). | probes G1/G2/G3 |
| M1 | Medium | Preflight holds no reservation: two $4 Modal admissions on one snapshot both pass (C1). Correct only if caller serializes check + durable reserve under one lock (contract-stated, unimplemented). | probe C1 |
| M2 | Medium | Shared snapshot has no AWS bucket and silently ignores unknown provider keys (X1); AWS admission repeats on the same receipts (A15). AWS liabilities exist only inside the receipt's claimed net headroom; AWS Budgets lag hours, 5-min freshness does not cover unbilled sessions. Recommend: reject unknown top-level keys or add an AWS bucket before enabling R2S_ENABLE_AWS. | probes X1, A15; failover.py:44-78 |
| M3 | Medium | `record_muse.reserve` sums `est_usd` only against its own $1/20-call file cap; not the S20a liability (max reserved/est/billed). Projection per CONTRACT.md:42 (`source#L<line>`) is defined but unimplemented. | record_muse.py:35-42 |
| L1 | Low | Settled row trusts `billed_usd` with any nonempty `reconciliation_ref` (L6); source inventory is label-only (F19). Shape-only by design; truth is the caller's obligation. | probes L6, F19 |
| L2 | Low | Admission rounds credit headroom UP (ROUND_CEILING) — admits 1e-8 candidate on 1e-9 credit (R1). Sub-cent; failover already refuses rounded headroom. Use ROUND_FLOOR for headroom. | probe R1; admission.py:80 |

## Checks that passed (requested criteria)

- Meta cap: confirmed history + pending (max reserved/est/billed) + candidate, strict `< 120` (M1 at exactly 120 pauses; M3 at-cap pauses even Modal work). $30 reserve never routine headroom (M4: credit 50 but 100+25 pauses).
- No double count inside one snapshot: duplicate request_id pauses (L3); wrong-provider row pauses (F17). Cross-ledger disjointness (history vs rows) is caller-asserted, not verifiable offline.
- Lifecycle: overrun counts billed > reserve (L1); crash keeps reservation (L2); retry cannot reuse ID (L3); unsettled without reservation pauses (L5).
- Fail-closed state: NaN/Inf/huge/bool/negative/null amounts, duplicate JSON keys, missing file, directory, BOM, stale/future/naive time, paused, unverified flags, zero/negative candidates all -> SPEND_PAUSED (F1-F18).
- Modal $30 cap / $5 floor edges exact (D1/D2); AWS cannot bypass Modal floor (A4).
- AWS: default OFF; only exact "1" enables (A1/A2); flag without receipts pauses, no Modal fallback (A3); on-demand, wrong region, stale/string-approved receipts, >$50/8dp headroom, zero/over bound, bool or >1h session all refused (A5-A14); result `launched=False`. No EC2 launch path: boto3 only used for S3 HeadBucket health checks.
- Library exemption: cannot be abused. It is structural (public library never calls the guard; no flag/route switch to spoof). Only web API route is local-dev-only `/api/lab` (NODE_ENV dev/test + localhost origin) which calls the fitter, not paid providers. No upload route exists. Library page is import-free static.

## Required before Gate C

1. Wire admission inside one cross-process check+durable-reserve boundary at `gpu_stages.reserve` (and any upload/Meta entry), mapping ReconstructionPaused -> StageError/UploadError SPEND_PAUSED (H1, H2, M1).
2. Build the projection from existing ledgers (S14b, run gpu-ledgers, S05/S06/S07 job ledgers) into the snapshot with real inventory (M3, L1).
3. Before AWS enablement: AWS liabilities in shared state, unknown keys rejected (M2). Optional L2 ROUND_FLOOR.

Not checked: live HTTP/upload behaviour (no route exists), real ledger projection, concurrency under a real lock, Build.gpu.test_aws_adapter (module invocation errored in this run; S20c evidence shows it passing).

