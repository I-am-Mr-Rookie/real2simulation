# R14 transport recovery

Both latent P3 defects are fixed in the shared `bridge()` reader. The current fixed Python producer uses `json.dumps` with default `ensure_ascii=True`; these are transport correctness regressions, not a demonstrated current-producer failure, exploit, privacy finding or release-gate blocker.

## Contract and change

- `StringDecoder('utf8')` preserves incomplete code points between raw stdout chunks; `decoder.end()` flushes at successful close.
- `outBytes += b.length` counts raw bytes from the unencoded child stdout stream. Accept exactly 1,000,000; reject above it before decoding/accumulating the offending chunk.
- Once stopped, discard subsequent stdout rather than growing the buffer. Existing sticky failure and capacity-until-close semantics remain. `MAX_BODY`, stopTree, abort/timeout, session/cancellation/privacy logic and HTTP parser are unchanged.
- No new dependency, wrapper, flag, producer/schema change or broad refactor. Native StringDecoder is available in the server-side Node runtime.

## Fresh checks (worktree root)

```powershell
node --test --test-reporter=tap tests/lab/r14-service-invariants.test.mjs
# frozen11.tap: 11/11 PASS, zero failed/skipped/cancelled/todo, exit0.

node --test --test-reporter=tap '--test-name-pattern=normal transport|Mystery error|abort cannot|stdin failure|synchronous spawn|during trusted handoff|abort during start hashing|UTF-8 bridge output|bridge raw-byte|timeout cannot|bridge output returns|asynchronous spawn|real capacity insertion|expiry while' tests/lab/session-service.test.mjs
# session-mocks.tap: 21/21 PASS (18 existing + 3 new), zero failed/skipped/cancelled/todo, exit0.
# Node filters out nonmatching tests rather than reporting them as skipped.

node --check Build/lab/session-service.mjs
node --check tests/lab/session-service.test.mjs
git diff --exit-code 79eed47 -- tests/lab/r14-service-invariants.test.mjs Build/web/src/app/api/lab/route.js Build/lab/session-bridge.py
git diff --check
```

The existing session test module initializes one actual Python CPU start-export fixture even under the mock-only name selection. No selected test runs OS process-tree verification; mock children have no pid. No lifecycle/stopTree code was changed, so the expensive actual Windows process-tree test and full production build were not rerun. No dependency installation or configuration change was needed.

## Boundary coverage

- Frozen original oracle unchanged: split two-byte UTF-8 roundtrip and 1,020,218-byte / 340,218-code-unit response now rejects with no session insertion; HTTP parser and state controls remain green.
- New focused cases: every interior split in two-, three-, four-byte characters; exactly 1,000,000 bytes containing multibyte output accepts; byte 1,000,001 fails sticky even if valid output follows, retaining the active slot until close.
- Existing selected mocks: validation/caps, generic error envelopes, abort/stdin failure/spawn errors/timeout, expiry/eviction/hashing races, capacity retention and no late reveal/cache.

## Pins / required parent review

Base commit: `79eed4719005abe5b18a2ea51854b3af6eb60fdc` (prior frozen audit preserved).

| Input | Git blob |
|---|---|
| Base service | `f5b724ddffe04b0e7c566b25e81a2074c8f5b881` |
| Fixed service | `94b350f4a5d85029850c1cfe0b5d4372df591da6` |
| Frozen 11-test oracle (unchanged) | `d36fc348c3dc43c7e0baa11d767df280fbb3f27c` |
| Focused session-service tests | `150cae05e10e66214298705781b1c7e914af2bd3` |

`product.diff` contains the exact service/test diff against the base. Parent should compare these source pins and review the tiny transport diff before serialized integration and its required cross-vendor review. This worker did not invoke Claude, merge, update shared controls or claim gate acceptance. Original red audit evidence under `service-invariants/` is intentionally preserved unchanged.

All fixtures are synthetic local transport/state evidence, not real scenes, fitter accuracy or physical GateM/S12 success. Malformed UTF-8 keeps Node's standard replacement semantics; no stricter validation contract is introduced.

## R15 recovery — Oct29, fresh acceptance evidence

The preceding R14 text/logs are historical and preserved. R14's apparent DONE report did not complete its commit/receipt handoff: source/tests/evidence were still uncommitted and its TIMEBOX.json was absent at R15 intake. The owner reports a usage-limit interruption; no original stop time is reconstructed or backdated.

R15 inspected and reused the unchanged minimal patch and three focused tests; no additional source/test edits were needed. Fresh execution of the exact two commands above passed **11/11 frozen + 21/21 selected**, zero failures/skips/cancellations/todo. New logs and source pins are in `R15/frozen11.tap`, `R15/session21.tap`, `R15/verification.json`, and `R15/product.diff`. The original red audit remains 9 pass / 2 fail and is not rewritten.

R15's actual 1800-second issue/deadline window, work stop, interruption limitations and scoped commit handoff are recorded in `Run-System/Runs/R15-transport/REPORT.md` and `TIMEBOX.json`. This is scoped transport verification, not parent integration, native cross-vendor review, UI375, deployment or physical acceptance.
