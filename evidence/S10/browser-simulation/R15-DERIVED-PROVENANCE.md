# R15 derived snapshot refresh (synthetic only)

The existing `generation.json` describes original artifact creation and remains
unchanged. This refresh does **not** regenerate its four validated artifacts.
Original snapshots remain recoverable at Git commit
`3a0d943b79a1cf41b558b94a6224bc9845a5674d` and pre-refresh base `b37f7b8`.

Current simulator source is pinned to `b37f7b8`. Its R15 correction implements
the accepted S08 linear small-angle pendulum model, S08 ramp acceleration
operation order, and finite RK4 weighted arithmetic. Ordinary floating-point
trace bit drift is therefore expected, not silently called bitwise equivalent
to the original implementation. Existing replay records are **not migrated**.

Reproduce only derived traces and verification:

```powershell
python -B evidence/S10/consumer-recovery/regenerate.py
node --test --test-reporter=tap tests/lab/browser-simulator.test.mjs
```

The evidence-only generator reuses the inspected `generate_fixtures.py` Node
CLI path, feeding original artifact bytes instead of recreating artifacts. All
four complete CLI traces pass the accepted, unchanged S08 Python analytic
functions at unchanged `0.005` relative position tolerance **before writing**
any snapshot. Characteristic scales are reused from `Build/lab/regression.py`.
Only ramp/pendulum derived traces differ; free-fall/projectile stay byte-identical.

[Generation verification](../consumer-recovery/generation-verification.json)
records exact old/new checkout and canonical Git-blob SHA256 hashes, original
and corrected source hashes, every immutable before/after hash, numerical
deltas, actual command/runtime versions, and all-sample analytic results.
Git's `core.autocrlf=true` explains checkout-vs-blob hash differences; it is not
a content/model change. The old runtime version is unknown.

This is browser consumer integration evidence, not a new analytic oracle,
whole Gate P pass, replay-hash continuity claim, native/UI test, physical Gate M,
real-scene or S12 acceptance. Parent native review on `b37f7b8` was reported
complete with no P0-P2 by the controller; it was not performed by this sidecar.
