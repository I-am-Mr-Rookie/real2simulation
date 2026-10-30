# S20d-orch112 — Gate C SIMULATED cap regression

- Assigned CODEX-2 / gpt-6.1-sol high; OpenCodex-managed; not polled.
- Parent project: Meta AI Hackathon `91e441f8-e40c-4ec4-bea2-de7fa1582d97`.
- Issued 2026-10-30T08:55:26+00:00; cutoff 09:20:26Z; deadline 09:25:26Z (15:25:26 Dhaka).
- First execution ~09:00:24Z; isolated branch `run/S20d-orch112` from main
  `8fa101a`; plain git worktree add as explicitly requested.
- Objective: reproducible multi-scene, no-network regression of existing accounting,
  durable global reservations, standalone/handoff/settlement and AWS-off failover.
- Owns ONLY: `Build/guardrails/`, `infra/failover/`, `tests/guardrails/`,
  `evidence/S20/`, `Run-System/Runs/S20d-orch112/` in THIS worktree.
- Reach: one offline evidence runner, its unittest, generated JSON and summary;
  no production edits unless a small defect is actually found. Reuse existing guards,
  journal/projection and settlement schema; no dependency or new spending policy.
- Checks: deterministic replay; exact Meta $120 stop/$30 reserve, Modal $30 cap/$5
  floor, explicit SPEND_PAUSED, canonical shared ledger, one-use claims, settlement,
  five guarded Modal local entrypoints and AWS OFF/no automatic selection; full
  guardrails unittest discovery remains green; TIMEBOX validator PASS.
- Safety: temporary synthetic state only, no canonical controls/runtime, no providers,
  GPU/AWS, credentials, installs or spend. Existing R-C P3 residuals are limitations,
  not prerequisites for this offline acceptance. No universal live-cap claim.
- Controller handles integration; no merge/main edits or follow-up dispatch.
