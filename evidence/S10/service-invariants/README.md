# R14 reproducible service-invariant evidence

Source baseline `74c886f9b2cc1322dde152f5be5813f813904bc6`; Node v24.18.0 on Windows.
Actual service and route imported, not copied or edited. All child transports controlled by the existing `spawn`/`syncBuiltinESMExports` harness pattern. HTTP `Request`/`Response`/`ReadableStream` are in-memory; no server or sockets.

```powershell
node --check tests/lab/r14-service-invariants.test.mjs
node --test --test-reporter=tap tests/lab/r14-service-invariants.test.mjs
# Intentional counterexamples: 11 tests, 9 PASS, 2 FAIL, exit 1.

node --test --test-reporter=tap '--test-name-pattern=request shape|observation shape|concurrent failed fits|malformed successful fits|interleaved failure|same-ID replacement|HTTP parser|streamed HTTP JSON|ASCII-escaped' tests/lab/r14-service-invariants.test.mjs
# Passing controls only: 9 PASS, 0 FAIL, exit 0. Does not fix/waive the two counterexamples.
```

Run commands from the assigned worktree root. The test sets `NODE_ENV=test` in its own subprocess only; no env file or persistent configuration edit.

- `FINDINGS.md`: exact expected/actual/root cause, reachability, severity and byte-unit caveat.
- `final.tap`: authoritative final frozen oracle, two expected red counterexamples, bounded diagnostics. Over-cap reply is **1,020,218 bytes / 340,218 UTF-16 units**, accepted and inserts one session.
- `controls-positive.tap`: 9/9 controls, zero skipped/cancelled.
- `baseline.tap`: original nine-test run, 7 pass/2 fail; initial deep-equality assertion printed a large synthetic limitation. Preserved verbatim; later oracle assertion compares status first to avoid log bloat.
- `controls.tap`: a negative-lookahead name filter unexpectedly ran all 11 tests and exited 1; NOT a passing-control receipt. Positive enumeration above produced the valid control receipt.

Git blobs of frozen inputs:

| Source | Blob |
|---|---|
| Build/lab/session-service.mjs | f5b724ddffe04b0e7c566b25e81a2074c8f5b881 |
| Build/web/src/app/api/lab/route.js | 2f064f593e24b2ed65aac426fd085255ed6e1755 |
| tests/lab/r14-service-invariants.test.mjs | d36fc348c3dc43c7e0baa11d767df280fbb3f27c |

The small S11-shaped fixture tests state transitions only; no actual fitter accuracy, calibration, physics success or scene approval is asserted. Actual current Python producer ASCII escaping is source-verified and mirrored by a passing control, not an actual Python/service execution in this run. No lifecycle/abort, production bundle, privacy or UI re-verification.
