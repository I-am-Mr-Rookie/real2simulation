# N40 offline verification

Run from this worktree. All model/Modal transports in these checks are offline fakes. Test ledgers are synthetic, not invoices.

## Required checks: 183 passed

```powershell
uv run --python 3.11 --with pytest --with-requirements Build/api/health/requirements-test.txt python -m pytest tests/agent/test_core.py tests/agent/test_fallback.py tests/agent/test_handlers.py tests/agent/test_lab_handlers.py tests/gpu tests/guardrails/test_daily_cap.py tests/reconstruction/test_live_room.py -q
```

## Expanded checks: 252 passed, 464 subtests passed

```powershell
uv run --python 3.11 --with pytest --with python-dotenv==1.0.1 --with-requirements Build/api/health/requirements-test.txt python -m pytest tests/agent tests/reconstruction tests/n21 tests/gpu tests/guardrails/test_daily_cap.py -q
```

The worktree uses the contract's junction to canonical `Build/web/node_modules`. Without it, kit tests use the old RK4 fallback and fail on missing Rapier-only kit traces. The expanded suite also needs the existing `record_muse` import dependency `python-dotenv`; no dependency manifests changed.

## Baseline negative control

`baseline-regressions.txt`: 14 representative regression cases fail as expected against base `97d8b84308ba8fed8111d0460cdd1781a2c44d78`. Only function bodies were replaced in an isolated Python process via `git show` plus `types.FunctionType`, not on disk:

- Agent: `_loop`, `_from_chat`, `http_post`, `_send`.
- GPU: `status`.
- Live room: `modal_reconstruct`, `run_job`.

Selected cases cover unknown usage on Meta/Merge/Baseten, both refusal formats, provider 400/413/422, rejected routing/security tools, concurrent start/heartbeat renewal, builtin timeout cancellation/retry, and per-attempt queue reservations. Logs are expected failures, not a failing final suite.
