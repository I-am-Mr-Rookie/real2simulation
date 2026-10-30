# S16g-orch116 — DONE (offline safety scope)

Bad patches now fail through the shared callable boundary without raw input
echoes, oversized admission or nested-candidate recursion crashes. **100 sidebar
tests PASS (91 existing + 9 new)**. Both configured search providers retain safe
one-attempt failures and explicit empty-success receipts. No live calls/spend.

## Changes / demonstrated defects

- `Build/sidebar-tools/contracts.py`: cap serialized UTF-8 calls at 64 KiB before
  experiment validation/copy/dispatch; retain strict JSON/experiment validators.
  Schema errors now expose trusted schema fields, not raw instance keys/values.
  Wrap strict parsing and candidate/spec failures in readable
  `SidebarContractError`, suppressing untrusted exception chains.
- Initial new tests reproduced raw fake-secret echo in unknown keys and invalid
  units; oversized patches reached experiment validation. A separate depth probe
  found uncaught `RecursionError` at candidate depths 600/900. Shared validation
  now converts these failures to safe typed rejections. No accepted spec hash,
  patch semantics, permissions, provider configuration or session logic changed.
- `tests/sidebar-tools/test_failure_safety.py`: nine focused tests cover malformed,
  incomplete, traversal (POSIX/Windows/absolute), out-of-scope, stale, oversized,
  non-UTF-8/cyclic/deep and malformed rebuild inputs. Checks span validate_call,
  apply_patch and RebuildSession, preserving current spec, trusted bundle bytes,
  input values and no rebuild dispatch. Exact 64-KiB and multibyte byte limits
  tested. Safe displayed errors and formatted exceptions exclude fake secrets.
- Both Baseten and explicit Fireworks exercise unavailable config, timeout,
  URL/HTTP/generic transport errors, malformed/empty/oversized response bodies and
  no-match/empty catalogue. Assertions check bounded timeout, one attempt, exact
  endpoint, closed HTTP error body, sanitized logs/results, no numeric outputs,
  no silent switch and `meta_bonus_claimed: false`. Existing search code already
  met these checks; **no speculative search rewrite**.
- `Build/sidebar-tools/CONTRACT.md`: admission limit, safe exception handling,
  unchanged callable contract and empty-success versus unavailable behavior.

## Fresh verification / evidence

- Baseline: requested unittest discovery, **91 PASS**, 85.415 s (tool receipt).
- Red regression evidence: `evidence/S16/S16g-orch116/before.txt` and
  `before-nesting.txt`. These are intentionally failing pre-fix logs, not final
  acceptance. They contain fake input only; the red parser/nesting run also
  exposed an assertion-context follow-on error in the new test harness, repaired
  before final verification.
- `python -B -m unittest discover -s tests/sidebar-tools -t tests/sidebar-tools
  -p test_failure_safety.py`: **9 PASS**, 4.663 s; `focused.txt`.
- `python -B -m unittest discover -s tests/sidebar-tools -t tests/sidebar-tools`:
  **100 PASS**, 158.530 s, exit 0; `unittest.txt`. This final suite includes all
  new tests and the final shared-code changes; earlier intermediate green run
  (98 tests) is not substituted for it.
- `behavior.json`: actual captured outputs, explicitly
  `OFFLINE_SYNTHETIC_FAKE_TRANSPORT`: four readable patch errors, six one-attempt
  fake provider results, **0 live requests / $0 inference**. Independent saved
  receipt audit passes; source metadata/gates were not promoted to real evidence.
- `verification.txt`: both changed Python files AST-parse; saved receipt audit;
  temporary test directories cleaned; diff checks and timing validation receipt.
  `TIMEBOX.json` records actual stop/report timestamps. Final named-file staged
  scope, timing and commit checks are performed during report finalization.

## Ponytail full / smallest complete change

Read and applied installed Ponytail 5.3.3 full. Reused jsonschema, strict experiment
parse/validate, existing SidebarContractError, session locking and injected
transport. Fixed the root shared admission/error code once for all existing
consumers. Added no dependency, second dispatcher, UI adapter, provider failover,
new configuration or persistence layer. Callers/fixtures/exports remain compatible
except intentionally tighter oversized/UTF-8 admission and sanitized ValueError
subclass/messages; documented the change. No real credential values read or used.

## Lifecycle / limits / next

- CODEX-2, assigned `gpt-6.1-sol/medium`; actual backend identity, coding tokens and
  subscription cost not independently observable. **OpenCodex-managed; not polled.**
- Parent project `91e441f8-e40c-4ec4-bea2-de7fa1582d97`, controller supplied;
  launcher association not independently inspectable. No child chats launched.
- Plain Git worktree `.worktrees/S16g-orch116`, branch `run/S16g-orch116`, base
  main `d3a1343c98bb17692f15f8047acfd209c68b2ca5`; initial worktree clean.
  Canonical unrelated changes preserved. Only Owns paths changed; no canonical
  controls, merge, rebase, publication, deployment, schedule or account action.
- Issued **2026-10-30T09:11:25+00:00**; cutoff **09:36:25Z**; deadline
  **09:41:25Z / 15:41:25 Dhaka**. All acceptance verification complete and task
  work stopped **09:25:07Z**; verified DONE early is permitted, no exception.
  Report/timing/staging finalization follows within the original window.
- Malformed calls intentionally raise a catchable typed error rather than forging
  correlated receipts. Trusted host must display `str(error)`; these tests do not
  establish browser UI/end-to-end acceptance or a server raw-body admission cap.
  Direct spec_sha256 retains existing experiment errors, as documented.
- Communication: mandatory higher-priority Ponytail/start notice and demonstrated
  defect update only; otherwise silent. One authorized exact completion pointer
  to controller. Mandatory final skip/risk line is a higher-priority exception to
  the one-line worker-chat preference. No owner questions or blockers.
- Controller owns integration and parent S16/S16h acceptance. Read final evidence
  and commit before merging; do not infer live or bonus readiness from fake tests.

Skipped live providers, real secrets, billing checks, installs, unrelated suites,
browser UI and deployment. Hosted availability and parent gates remain unverified;
the host must catch malformed-call errors and enforce its own raw-request limit.
