# Frozen independent UI-helper semantics

Base: `9eece4239d47ece4600f3fff7f2e38b78403cb02`.
Test freeze: `a79e135ae9e0702d679d3bad2351052651543666`.
Test Git blob: `fa9eba92e001c565c3ae53fcd35c54a89572a065`.
Raw LF test SHA256: `3CD295FA966747C2199666338997E87B9CEC9BD3677E30FAFB31635F2DFBB072`.
Git's configured CRLF checkout conversion may change a later raw-file SHA256; the frozen commit/blob is authoritative.

## Geometry, not an implementation recipe

The public plot convention is x=24 at minimum time, x=616 at maximum time;
y=190 at minimum position, y=30 at maximum position. A constant axis is centered
(x=320 or y=110). Time and position are independent. Defaults describe a 592-by-160
interior; custom 512-by-128 extents have endpoints (24,190), (536,62) and midpoint
(280,126). Equal observations remain separate points. No sorting or downsampling.

For an exactly equally spaced three-point domain the expected pixels are
`[[24,190],[320,110],[616,30]]`; for five points they are
`[[24,190],[172,150],[320,110],[468,70],[616,30]]`. These are literal algebraic
endpoint/midpoint/quarter expectations, not approximate outputs from the helper.
All assertions use exact equality, with no tolerance or implementation-dependent
normalization branch. The independent BigInt dyadic decoder proves the input
spacing exactly in units of 2^-1074 before these coordinate tests run. It never
computes the expected plot result. It is self-checked on +/-MIN_VALUE and 1.

Cases cover +/-2^1023, +/-MAX_VALUE, same-sign MAX_VALUE midpoints, neighboring
huge values spaced by exact ULPs, positive/negative/opposite-sign subnormals and
the subnormal/normal boundary. A shuffled, duplicated mixed-axis case proves
order/count and independent scales. Frozen arrays/rows and before/after copies
guard mutation. A fixed 131073-row constant list proves there is no implicit
JavaScript argument-count ceiling or silent truncation in this helper contract;
this is NOT a requirement to enlarge the actual producer's 2000-row limit.

## Uncertainty meaning and legitimate compatibility

The actual offline Python bridge generates a normal free-fall run and calls the
actual fitter on its observations. The test authors only a service-shaped
status/sessionId envelope around that complete fit, not its numeric results or
metadata. `actual-producer-fit.json` is a separate fresh producer capture.

The producer explicitly declares `quantity_uncertainty` as
`standard uncertainty (one sigma), not a 95% interval`; its covariance interval
is null. The UI's existing label promises one standard uncertainty. Preserve the
producer value and uncertainty without rescaling or inferring a 95% interval.
Changing ONLY that explicit meaning to a 95% confidence interval, two-sigma
expanded uncertainty, or an express denial of standard uncertainty must not
yield a trusted one-sigma reveal. Return null rather than silently relabel it.
An assumptions array must actually contain strings at every position; holes
are not strings even though Array.prototype.some skips them.

No new required DTO field: the established minimal simulated gravity DTO with
model and string assumptions, but without `quantity_uncertainty` or covariance,
must still parse identically. No new model enum, covariance requirement, general
metadata parser, confidence-level conversion or arbitrary-field rejection is
introduced. The sparse array case is in-memory only, not JSON-reachable.

## Base findings and use

Final 23-case oracle: **14 PASS / 9 expected FAIL**, exit 1. Failures group into
four known latent P3 families: extreme span arithmetic (four tests), argument
spread ceiling (one), contradictory uncertainty meaning (three), sparse
assumptions (one). Positive producer/legacy/dyadic controls: **3/3 PASS**.
Unchanged existing UI contract suite: **9/9 PASS**. Initial 21-case TAP is also
retained; two later additions cover the large-list and sparse-array findings,
without changing any expected value/assertion in the first 21 tests.

These are helper counterexamples on the base, NOT a product or gate PASS and
NOT evidence of current fixed bounded JSON producer exposure. No repair worker
implementation was inspected or copied. Controller may consume the frozen test
commit and compare a later repair, retaining the red base evidence. No repair
was tested here. Do not weaken assertions to obtain green.
