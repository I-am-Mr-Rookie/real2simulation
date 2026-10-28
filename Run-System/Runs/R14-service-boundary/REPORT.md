# R14-service-boundary — DONE (bounded independent AUDIT only)

**Two latent P3 transport gaps frozen; no current-producer/product pass or fix claimed.** All assigned bounded audit deliverables complete. The intentional regression suite remains red on the assigned unmodified source; parent owns triage/fix/integration.

## Source / authority / time

- Requested actual lane/managed route: CODEX-1 / gpt-6.1-sol / high, as supplied; underlying model identity not independently attested. No routing change. OpenCodex-managed; not polled. Tokens/costs unobservable; no paid operation.
- Initially clean assigned isolated worktree `C:/Users/HP/.codex/worktrees/swarm14-service-boundary/2026-10-26 - Meta Global AI Developer Hackathon`; branch `run/R14-service-boundary`; baseline `74c886f9b2cc1322dde152f5be5813f813904bc6`. Canonical main had independently advanced to `55a3d2e` at intake; no source refresh/rebase performed.
- Canonical project/root and inherited parent-project ID `91e441f8-e40c-4ec4-bea2-de7fa1582d97` recorded in PLAN.md. Launcher says visible parent corroborated but metadata null; no independent child UI-project claim.
- Original issue **2026-10-28T21:37:28.000Z**, implementation cutoff **22:02:28.000Z**, deadline **22:07:28.000Z / Oct29 04:07:28+06:00**. First observed clock 21:37:46Z. Actual stop/report timestamps in TIMEBOX.json; verified complete audit may finish early, no exception or shortened window.
- Task work stopped **2026-10-28T21:46:44.3999070Z** after frozen-test/source-isolation/scope checks; report/timebox/commit administration followed. Report timestamp **2026-10-28T21:47:12Z**.
- Read current canonical AGENTS/STATE/QUEUE, timebox policy, Ponytail FULL, relevant last three reports (SWARM-20261029-1000, R13-process-lifecycle, R12-fitter-invariants), exact service/route, existing session tests and relevant trusted-handoff/producer helpers. Current launch scope supersedes older stop/desktop-chat constraints only for this run.

## Findings

Detailed counterexamples/limits: `evidence/S10/service-invariants/FINDINGS.md`.

1. **F1 / P3:** `Build/lab/session-service.mjs:57` decodes each stdout Buffer independently (`out += b`). Valid JSON containing UTF-8 `µ` split at `C2 | B5` returns success with `��`, violating byte-partition-independent decoding.
2. **F2 / latent byte-bound gap:** lines57/59 cap decoded UTF-16 units, not raw bytes. **1,020,218-byte / 340,218-unit** valid response accepted and inserts one session. Independent expected byte-limit oracle rejects it. Source does not explicitly document output limit units; if intentionally code-unit-bound, classify F2 as hardening rather than a violated published contract.

Both examples use controlled valid bridge responses. **Current fixed Python producer ASCII-escapes Unicode (`session-bridge.py:132`, default ensure_ascii=True), so current actual producer is not shown to trigger either defect.** No remote exploit, changed physics, privacy defect, P0–P2 finding or release blocker demonstrated. One small shared-root fix could address both; no product fix authored.

Immediate nonterminal commentary sent. Explicitly authorized parent callback attempted; app tool returned unavailable. No delivery claimed or retry/config bypass. Evidence preserved for parent handoff.

## Fresh checks / outcomes

| Check | Result |
|---|---|
| `node --check tests/lab/r14-service-invariants.test.mjs` | PASS |
| Full frozen oracle, `node --test --test-reporter=tap tests/lab/r14-service-invariants.test.mjs` | **9 PASS / 2 intentional FAIL**, exit1, zero skipped/cancelled/todo; final.tap |
| Explicit positive-name control selection (README exact command) | **9/9 PASS**, exit0; controls-positive.tap |
| Requests | Malformed types/allowlists/unknown actions reject before spawn; proper expected error codes |
| Response validation | Invalid sample keys/types/finite values/2001 samples reject; exactly2000 accepts; malformed gravity/unit/source/covariance/model never cache and permit valid retry |
| Shared state | Three failed waiters share one attempt; valid concurrent retry shares one success and cache; interleaved sessions isolate failure/success; same-ID replacement rejects stale completion |
| HTTP body/parser | Actual UTF-8 byte ceiling enforced despite lying length; exactly1,000,000 accepted,1,000,001 rejected; streamed split UTF-8 preserved; malformed/empty JSON400, oversize413, semantic error200; no-store retained |
| Current-producer control | ASCII-escaped Unicode survives chunk split unchanged |
| Source isolation | `git diff --exit-code 74c886f -- Build tests/lab/session-service.test.mjs` PASS; actual imports unchanged |
| Whitespace / scope | Authored test/Markdown/timebox PASS; all-file check exit2 solely for12 original trailing-space TAP diff lines, preserved verbatim; staged10 files all inside Owns |

All checks bounded local CPU/in-memory. No Python/simulator dependency junction needed, no service deployment or sockets. Frozen source/test blob IDs and raw evidence in evidence README. Node emits existing MODULE_TYPELESS_PACKAGE_JSON warning; not changed.

## Concrete Ponytail FULL / scope / limits

- Reused existing Node runner, assertions, controlled child-process pattern, test-only session accessor and real trusted-handoff/session constructors. One owned test file; no new helpers/dependencies/frameworks, source copy, product refactor or manifest edit.
- Small independent oracles: JSON/UTF-8 partition identity, raw Buffer byte count, specified sample/body caps, exact generic errors, shared-object cache identity and one bridge per concurrent attempt. Fixtures explicitly state machine-only, not fitter accuracy evidence.
- Preserved first bulky synthetic failure log; reduced later assertion output without weakening expected behavior. A negative-filter control attempt unintentionally ran all tests; retained nonpassing receipt and corrected with explicit positive enumeration, not relabeled as green.
- Skipped duplicate actual Windows abort/process-tree and production bundle checks, privacy/host authorization audit, UI375px, actual fitter/simulator, real scenes, physical GateM/S12, all heavy builds/network/GPU/deployment/publication/accounts/terms/credentials/config/provider changes. Wider payload schema/combinatorics and arbitrary producers are not proven safe.
- Exact changed Owns only: this run directory, `evidence/S10/service-invariants/`, `tests/lab/r14-service-invariants.test.mjs`. No canonical controls, product code or merges.
- Communication: mandatory developer pre-tool/skill updates plus required nonterminal finding and callback-unavailable clarification; otherwise silent. Final one-line pointer only. No fanout.
- Next action: parent triages latent severity/byte-unit contract before integrating these deliberately red regressions; fix in parent scope if warranted, rerun frozen tests unchanged. Audit DONE is not product/gate acceptance.
