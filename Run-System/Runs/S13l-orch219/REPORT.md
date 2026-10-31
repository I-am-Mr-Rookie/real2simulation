# S13l-orch219 REPORT: DONE

- Lane CLAUDE; anthropic/claude-opus-5-5/high (coding quota OpenCodex-managed; not polled). Tokens unknown. Project 91e441f8-e40c-4ec4-bea2-de7fa1582d97.
- UTC issued 14:27:21Z, start 14:28:49Z, work stopped 2026-10-31T14:39:50Z; deadline 14:57:21Z. Base main 7055bc38; branch run/S13l-orch219; worktree .worktrees/S13l-orch219.
- Modal spend: RM04 job app ap-HyDn6NecaH49gRHPDZhiHh billed $0.00955339 (4 rows, hour 2026-10-31T14:00, read 14:38:52Z, may still rise until the hour closes) vs reserved $0.50 vs estimate $0.01035363. App state stopped at 14:38:04Z, tasks 0; modal container list empty (14:38:33Z). No other paid call.

## Step 1: settlement (canonical runtime, guardrails only, serial)
1. Bind events: evidence/S13l/settlement/bind.py appended one {provider, request_id, app_id} line per request to standalone-gpu-ledger(-2).jsonl under admission.lock, same append+fsync pattern as reserve_gpu (idempotent). project before/after in bind-output.json: app_id None -> ap-9SEB.../ap-7qnU.../ap-HTu3....
2. Billing: fresh read-only `modal billing report --start 2026-10-30 --end 2026-11-01 -r h --json --show-resources` at 14:30:58Z (settlement/modal-billing-report-2026-10-30_31-fresh.json) equals the S13j 14:06Z read per app.
3. Receipts settlement/receipt-{OWN01,batch1,batch2}.json (modal-settlement/1, containers [], completed_at 2026-10-31T00:00Z = upper bound, basis recorded in receipt; modal app list empty 14:32:02Z) + scene-log-*.json. `python -m Build.guardrails.settlement <id> <receipt>` exit 0 each: OWN01 0.02228421 (14:32:27Z), batch1 0.10192457 (14:32:29Z), batch2 0.03512343 (14:32:32Z). Journal unsettled Modal 3 -> 0; $1.40 reserved -> $0.15933221 billed.

## Step 2: RM04 reconstruction
- Attempt A (canonical cwd, 14:32:49Z): SPEND_PAUSED, receipt.json as_of 2026-10-30T23:55:28Z > 5 min. Nonterminal blocker sent; controller approved a trusted-operator refresh.
- receipt.json refresh (evidence/S13l/refresh_receipt.py, under admission.lock, same shape; Modal historical 1.05201277 from read-only Oct billing total 14:33:31Z, headroom 28.94798723, Starter $30 only, old sources kept; Meta unchanged). sha256 85DA8A38...AA60 -> F7C25DEC...2704 (14:34Z) -> 8207B338...2046 (second refresh 14:37Z). Backups receipt-before.json, receipt-before-refresh2.json.
- Attempt A retry (14:34:33Z): reserved $0.50 (journal row evidence/S13l/gpu-ledger.jsonl:reconstruct:reconstruct:b3fe96a5...), then uv failed before Modal: "No environment file found at: Hackathon.env" (gpu_stages ENV_FILE is absolute path with spaces from main; worktrees use ../../.env). $0, no app.
- Attempt B (worktree, 14:34:55Z): SPEND_PAUSED "GPU admission state unavailable or invalid": reservations.project scene-log fallback did r["source"] on the journal copy of that row (same key as S13h) -> KeyError; this froze ALL Modal admission on main. Controller approved a fix (Owns extended).
- Fix (commit 23eb7c15): Build/guardrails/reservations.py skip rows without "source" in that fallback (one line) + regression test tests/guardrails/test_reservations.py::test_journal_row_reusing_recorded_reconstruct_key_does_not_break_projection (fails without fix, passes with). **Main stays frozen until this is merged.**
- Run (worktree cwd, ledger canonical evidence/S13l/gpu-ledger-2.jsonl, dispatch 14:37:01Z): exit 0, reconstruction.json sha 8c892f8d..., point_count 20000, bundle validated by gpu_stages (contracts/scene). Manifest: Build/pipeline/recorded/RM04-S13l-mapanything.json (shas only). Bytes local only in worktree evidence/S13l/reconstruct/bundle/ (gitignored). New shas differ from S13h (as expected; old shas not reused). Labels: Display only, scale unverified, not a measurement.

## Open liabilities (controller)
- Orphan attempt-A reservation $0.50 (evidence/S13l/gpu-ledger.jsonl...): no app, no dispatch. Build.guardrails has no release/cancel path for never-dispatched rows (rg: none); left unsettled per controller.
- RM04 reservation $0.50 (gpu-ledger-2...): unsettled; billing hour not final. After 15:00Z: append bind event {provider, request_id, app_id ap-HyDn6NecaH49gRHPDZhiHh} to canonical evidence/S13l/gpu-ledger-2.jsonl (bind.py pattern), receipt from fresh billing, settle. Until then 2 journal jobs = gpu_stages MAX_JOBS 2: further gpu_stages jobs pause.
- Canonical untracked files under evidence/S13l/ (settlement receipts/sources, gpu-ledger*.jsonl) are referenced by the journal and rechecked on every projection (reservations.py:215 final_amount): never edit/move them. The branch carries identical copies; before fast-forwarding main, move canonical untracked copies aside or verify identical, so git does not refuse to overwrite.

## Ponytail (full)
- Reused: Build.guardrails.settlement CLI, reserve_gpu append pattern, durable.exclusive/write_json, gpu_stages CLI unchanged, existing test fixture setUp. One-line root-cause fix in shared projection, not a caller workaround.
- Skipped: ENV_FILE space-path fix in gpu_stages (worked around by worktree cwd; outside Owns), DEV deploy/viewer wiring, orphan release code (no existing path; new code not authorized).
- Fresh checks: tests.guardrails.test_reservations 15 OK; test_settlement+test_admission 29 OK; new test fails without fix; project() passes on canonical state; worker_timebox check.

## Risks
- receipt.json historical 1.05201277 is a CLI gross total that may overlap ledgered rows (conservative).
- completed_at in the 3 settlement receipts is an upper bound, not observed completion.
- RM04 billed figure may grow slightly until the 14:00Z hour finalizes.

## Communication
Two nonterminal blockers + one completion line to controller chat 01a1882d-3481-7ce3-8f88-45c942e341cd (owner-authorized).

