# S20c-orch54

Objective: implement an offline, disabled-by-default provider selector requiring
explicit quota/budget receipt paths, existing AWS spot gates and S20b admission.

- Assigned CODEX-2, gpt-6.1-sol / medium; OpenCodex-managed; not polled.
- Parent project: Meta AI Hackathon `91e441f8-e40c-4ec4-bea2-de7fa1582d97`.
- Canonical root: `C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon`.
- Base main: `eda559f000aae3c8c23a6a06a51b06de18fa0704`.
- Isolated branch/worktree: `run/S20c-orch54`, `.worktrees/S20c-orch54`.
- Issue 2026-10-29T22:13:38+00:00; implementation cutoff 22:38:38Z;
  deadline 22:43:38Z (2026-10-30 04:43:38 Dhaka).

Owns (exclusive): `Build/guardrails/`, `infra/failover/`, `tests/guardrails/`,
`evidence/S20/`, `Run-System/Runs/S20c-orch54/`. No canonical controls/merges.

Scope/callers: add selector under guardrails, reuse unchanged
`Build/gpu/aws_adapter.py::activate` and `admission.require_reconstruction`;
add offline synthetic tests and update failover contract. No production caller
exists for this new selector. Existing pipeline/upload integration is outside Owns.
No exports/config/dependencies need changing. Existing admission/library behavior
must remain unchanged. No cloud API calls, environment writes or resource launch.

Acceptance:
1. Default OFF/Modal; explicit AWS selection requires readable valid quota and
   $50 gross EC2 budget receipts, us-east-2 spot only, fresh verified headroom,
   bounded session and passing S20b admission.
2. Tests refuse missing/corrupt/stale receipts, wrong region/on-demand,
   insufficient quota/credits/cap, invalid bounds and failed admission.
3. Save fresh test evidence; check TIMEBOX; commit only Owns with `git add -f`.

Ponytail full applied: reuse pure AWS adapter and S20b exception/accounting, no new
launcher/ledger or SDK. Conservative S20b Modal guard is retained even for AWS;
the selector does not turn a cap/floor failure into provider-switch permission.
Read canonical instructions and owner AWS decisions; existing approvals reused,
not new consent requests. Approval/config receipts are not live billing proof.
