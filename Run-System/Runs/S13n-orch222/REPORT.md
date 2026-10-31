# S13n-orch222 REPORT — DONE

- Worker anthropic/claude-opus-5-5 high, CLAUDE lane; OpenCodex-managed; not polled. Tokens/cost of model: unknown (unobservable).
- UTC start 2026-10-31T14:45:52Z (issued 14:44:53Z); work stopped ~15:07Z. Branch run/S13n-orch222 from main e1a76ce.
- Modal spend this run: $0 (read-only CLI reads only: app list, container list, billing report). No GPU job.

## Result
- Canonical journal (evidence/S20/runtime/reservations.json) unsettled Modal: **2 -> 0** (evidence/S13n/steps.log, before 14:50:48Z / after 15:05:54Z).
  - Orphan attempt-A (evidence/S13l/gpu-ledger.jsonl …b3fe96a5…): **voided at $0** 14:51:06Z via new modal-void/1 receipt evidence/S13n/void-orphan.json (fresh app list + billing read 14:51:03Z: only app since reservation is RM04's ap-HyDn6…, bound to the other request).
  - RM04 (evidence/S13l/gpu-ledger-2.jsonl): bind event {provider, request_id, app_id ap-HyDn6NecaH49gRHPDZhiHh} appended under admission.lock (bind.py pattern, idempotent); fresh billing read 15:05:49Z (after 15:05Z, 14:00Z hour final); app stopped 14:38:04Z, container list []; modal-settlement/1 receipt evidence/S13n/receipt-RM04.json + scene-log-RM04.json; settled **$0.00955339** (A10G .00794460 + Memory .00092446 + CPU .00068324 + egress .00000109) vs $0.50 reserved.
- Applied with `python evidence/S13n/s13n.py <step>` from the canonical checkout, PYTHONPATH = this worktree (new code; operates on canonical runtime via repository_root). Journal never hand-edited; ledger only appended by code under lock.

## Code
- Build/guardrails/settlement.py: `modal-void/1` release path inside the existing settle_gpu/final_amount (no new CLI: `python -m Build.guardrails.settlement REQUEST_ID VOID_RECEIPT.json`). Void requires: reviewed receipt; journal row has no dispatch_operation/app_id; reserved <= read_at <= now; hashed in-repo app_list + billing_report; projected row has no app/app_ids/bill; every app created and every billed object in/after the reservation hour is bound to ANOTHER request. Final amount 0. Replaying the same void receipt is a no-op (idempotent); any other re-settle still rejected. Shared source-hash loop extracted to `_sources` (reused by both schemas).
- Build/guardrails/reservations.py: projection rechecks a voided row; an app later bound to it pauses admission.
- Build/pipeline/gpu_stages.py: ENV_FILE now `.env` / `../../.env` relative to cwd=ROOT. Root cause verified: uv splits `--env-file` on spaces (absolute canonical path -> exit 2 "No environment file found at: Hackathon/.env"; relative `.env` -> exit 0).
- Tests: tests/guardrails/test_settlement.py +4 (void at 0 + idempotent replay + slot release; rejects app-bound, billed, unexplained app in list or bill; dispatched cannot void; late app binding pauses). tests/pipeline/test_gpu_stages.py +1 (env-file space-free, relative, resolves to .env).

## Checks (fresh)
- `python -m unittest tests.guardrails.test_accounting … test_simulated_cap_regression tests.pipeline.test_gpu_stages` -> 108 OK.
- Canonical projection after settle: both rows settled (steps.log last line).

## Ponytail (full)
- Reused: settle_gpu/final_amount/CLI, admission.lock, S13l bind.py + make_receipts.py patterns, existing test fixture setUp/billing_row.
- Smallest: void is a second receipt schema in the existing settlement path, not a new module/CLI/event type; ENV fix is one line.
- Skipped: generic release for dispatched/billed jobs (not needed; fail-closed), journal migration, DEV deploy.

## Risks / limits
- **Canonical main still has old settlement code**: until this branch fast-forwards, main's projection rejects the modal-void/1 row -> GPU admission fail-closed (paused). Merge promptly.
- Canonical evidence/S13n/* are untracked and referenced (sha256) by the journal; branch carries identical copies — verify identical/move aside before fast-forward; never edit them. evidence/S13l/gpu-ledger-2.jsonl gained one bind line (canonical, untracked).
- Void trusts that `modal app list` shows recently stopped apps (it showed RM04 stopped 27 min later) and hourly billing; a job billed only in a later hour would show up as a late binding only if ledgered.

## Communication
One completion line to controller chat 01a1882d-3481-7ce3-8f88-45c942e341cd (owner-authorized).

