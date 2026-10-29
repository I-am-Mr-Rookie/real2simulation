# Deterministic local replay

`createReplayRecord({seed, parameters, trace, version?})` and
`replayRecord(record, runner)` retain the `s10-replay-v1` format and sorted-JSON
SHA-256 identity. Ordinary JSON records keep their existing hashes; negative zero
normalizes to zero. Seed is identity metadata, not trajectory randomization.

Inputs must contain JSON-compatible finite values, plain parameter objects and
dense nonempty traces. Accessors, cycles, symbols, unsupported array properties
and invalid seed/version/parameter/trace metadata reject with `INVALID_REPLAY`.
Array traversal reads own data descriptors, never caller-controlled `map` or
index getters. Replay validates one detached, deeply frozen initial snapshot
before executing the synchronous runner; runner parameters are a separate clone.
Caller mutation during digest awaits or runner execution cannot mix records.

Getter/subclass/nonenumerable-property cases concern direct JavaScript callers,
not ordinary parsed JSON. Malformed metadata and mutable records can also occur
with JSON-derived data. This data API is not a hostile-JavaScript/Proxy sandbox.
Hashes check consistency, **not authentication** or ownership. No account,
private-store, physical-accuracy or product-gate claim follows from a replay hash.
