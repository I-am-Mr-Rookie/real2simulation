# R14 replay audit — frozen findings (baseline 74c886f)

## P2 — array canonicalization bypass (confirmed 21:39:56Z)

Source: `Build/simulator/replay.mjs:10-13`. Factory documentation in `Run-System/Runs/S10fg-extension/REPORT.md` says accessors and extra/out-of-range array keys are rejected. Expected: reject unsupported array properties before executing them; never discard data or manufacture a trace through user-overridden iteration. For a subclass, either reject safely or preserve the actual dense values without invoking its overridden methods; no extra feature is required.

- `trace=[0]` with an enumerable getter at index `0` returning `9`: `createReplayRecord({seed:1,parameters:{},trace})` succeeds, executes getter once, stores `[9]`.
- `trace=[1]; trace['01']=2` or `trace['4294967295']=2`: factory accepts, discards extra property, and hash equals plain `[1]`.
- `class Forged extends Array { map(){return ['123'];} }`, densely populated with `[0,1,2,3,4,5,6]`: hash equals `[123]`, and factory stores `[123]`.

Root cause: the array branch omits descriptor/prototype checks, accepts every digit-only key (not canonical in-range indices), and dispatches through caller-controlled `value.map()`. No SHA-256 collision is involved: unsupported inputs are mapped to the same canonical bytes before hashing.

Reachability: direct JS replay/stableHash callers, including arrays nested in parameters and trace. JSON transport strips getters/subclass prototypes but retains object-level concerns separately; numeric non-index array properties also cannot arrive through JSON arrays. No evidence that normal JSON-only lab inputs trigger this bug; no physical or security-authentication claim.

Frozen expected-oracle tests remain failing on baseline; no product patch is owned by R14.

## P2 — malformed record executes runner before validation

Source: `Build/simulator/replay.mjs:30-35`. Independently compute valid SHA-256 hashes for a record whose seed is `-1`, `1.5`, or `Number.MAX_SAFE_INTEGER+1`, whose parameters are `null`/`[]`, or whose trace is `[]`/`{}`. Expected: reject before invoking simulator callback. Actual: runner is invoked once; eventual metadata/output validation rejects afterward. Hashes establish byte consistency, not schema validity. No forged record is claimed authenticated.

Root cause: only version and runner type are validated before hashing; schema validation occurs in `createReplayRecord()` after `runner(...)`. A valid JSON-decoded record can trigger this ordering bug. The eventual rejection prevents a false replay-success return, but not runner side effects/resource consumption.

Also confirmed: replacing the valid envelope's `trace` field with an enumerable getter returning the original array is accepted; getter executes twice. The envelope itself is not descriptor-validated. Getter issue requires direct JS input, not JSON transport.

## P2 — async record mutation mixes verified versions

Source: `Build/simulator/replay.mjs:32-35`. Start `replayRecord()` on a mutable JSON-like record with seed `1`, parameters `{x:1}`, trace `[1]`. Before the first digest await resumes, a queued microtask replaces the fields/hashes with a consistent seed `2`, parameters `{x:2}`, trace `[2]` record. Expected: either replay the initial detached snapshot or reject concurrent mutation. Actual: success returns seed `2`, trace `[2]`; the first trace-hash check was against `[1]`, while later checks/runner use the replacement record.

Root cause: repeated reads across asynchronous digest boundaries instead of snapshotting/validating one envelope. No getters/proxies, SHA collision, timing loop or external resources are required. The frozen test uses `queueMicrotask` and the independent synchronous Node hash oracle.

## Bounded-clean results / deliberate limits

- Actual validated S08 artifacts for free fall, projectile, ramp and pendulum execute the existing engines, then match independently serialized SHA-256 trace/body hashes and JSON round-trip replay. Counts: 201/201/201/1001 samples.
- Ordinary JSON tampering with seed, parameters, trace, version or either hash rejects before runner invocation. Seed is metadata bound into identity, not a physics randomizer; valid boundary seeds `0` and `Number.MAX_SAFE_INTEGER` work.
- Hashes are not authentication: an author who rewrites both data and hashes can create a new consistent record. This is tested as a positive limitation, not reported as a bug.
- Lab `replay-check.mjs` records `.samples`, not full trajectory envelope metadata (`units`, `stop`, labels). `regression.py` separately compares repeated complete transport stdout. R14 does not assert whole-envelope persistent tamper protection from sample hashes.
- No RK4 numerical accuracy, contact, browser, production bundle, Windows abort, physical gate or real-scene audit was repeated.
