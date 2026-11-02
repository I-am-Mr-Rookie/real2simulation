# N77-orch322
Status: DONE, pending controller spend-code review before merge/deploy.
SF3D module: Build/gpu/sf3d.py. Batch caller: Build/reconstruction/shape_upgrade.py (not objects.py in this revision).
Changed: each serial upgrade batch reserves one separate A10G-worst-case 900 s idle tail before its first spawn; each call reserves worst-case compute before joining the queue.
Settlement: successful calls pay bounded wall time plus worst-GPU inter-call gaps; the shared tail settles at batch exit, including exceptions. Crashes leave reservations counted, never refunded.
Isolation: each concurrent batch owns its tail. Long gaps or clipped slow transfers settle the old tail and require another reservation before spawning; no unsupported warm-sharing assumption across those breaks.
Failure/abort: unknown execution or cancellation retains the full compute bound plus the reserved tail; lease-reaped rows cannot be released by a late result. Standalone call accounting unchanged.
Receipts: room per-mesh estimates now explicitly exclude the separately booked batch idle tail.
Tests: python -m pytest tests/gpu tests/reconstruction tests/guardrails/test_daily_cap.py -q: 174 passed, 6 subtests passed, one existing anyio/pytest deprecation warning, Python 3.14.5.
Evidence: evidence/N77/accounting.json (7 synthetic ledger checks), evidence/N77/CHECKS.md; all observed actual settlements <= reservations.
Checks: git diff --check passed; named staged paths and credential-pattern scan checked before commit.
Paid calls: 0. No browser, UI changes, deployment or push.
Skipped P3-5 elapsed-wall refund: cancellation acknowledgement is not verified termination-time evidence; no safe smaller upper bound was established. Full failure bounds intentionally retained.
Risk: worst-GPU tail is conservative even when all meshes use L4; crash orphan tail remains reserved for that day. Provider billing and production Python environment not exercised.
