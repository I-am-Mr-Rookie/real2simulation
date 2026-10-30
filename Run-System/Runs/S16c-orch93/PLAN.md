# S16c-orch93 — rebuild and numeric tool-output plumbing

- Parent project: Meta AI Hackathon `91e441f8-e40c-4ec4-bea2-de7fa1582d97`.
- Lane/requested route: CODEX-2, gpt-6.1-sol/medium; OpenCodex-managed, not polled.
- Issued: 2026-10-30T06:31:42+00:00. Implementation cutoff: 06:56:42Z.
- Deadline: 2026-10-30T07:01:42+00:00 (13:01:42 Dhaka).
- Base main: `3ea7f5342c1129fba2d134377fee2ba926269ff0`; isolated branch `run/S16c-orch93`.
- Owns: `Build/sidebar-tools/`, `tests/sidebar-tools/`, `evidence/S16/`, this run directory only. No canonical control edits or merge.

## Objective / smallest complete change
Provide a serialized, local rebuild session: S16b validates a patch before storing
the current revision; a matching rebuild request invokes the existing synthetic
lab pipeline (Node simulator -> instruments -> fitter). Return existing S14 typed
numeric outputs, with separately validated SHA-256 receipts. Retry failures without
losing the admitted revision; successful retries reuse their receipt, not compute.

## Reach and risks
Existing callers: sidebar contract tests and S16b application; no live server caller
exists yet. Extend only the rebuild result payload, preserving queued acknowledgments
and the strict S14 numeric-output shape. Add handler, tests and contract documentation.
Reuse `apply_patch`, `validate_setup`, `run_lab`, `fit_tool_output`, and S14 rendering.
No new dependencies, model/provider calls, GPU/paid jobs, deployment, or shared writes.
Session state is process-local; no durable queue or automatic retry scheduler.
Synthetic ballistic support follows existing lab capability, never physical evidence.

## Acceptance
1. Invalid/stale/unpatched requests cannot execute; preflight rechecked at admission.
2. Real local simulator/fitter run returns code-backed numbers accepted by S14, with
   independently verifiable output hashes and no caller-owned mutations.
3. Safe typed failure + retry/idempotency behavior, serialized against patch changes.
   Run sidebar-tools suite and relevant existing agent/spec/lab checks; save evidence.
