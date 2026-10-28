# S11abc instruments swarm evidence

Simulation-only local evidence; generated values are not physical measurements.

## Completed leaves

- **S11a:** strict shared `Quantity` payload and validator in `contracts/fit/`.
  Required units, non-negative uncertainty, and simulated provenance; rejects
  booleans, NaN, infinity, negative uncertainty, and non-simulated provenance.
  Signed `error` is retained separately from `uncertainty`.
- **S11b:** seeded stopwatch reaction noise with explicit seed, bias, noise
  standard deviation, resolution, and reported uncertainty. Same seed and
  parameters replay identically.
- **S11c:** camera time/pixel and frame quantization, ruler distance
  quantization, and light-gate timing quantization. Bias, resolution and
  uncertainty are explicit caller inputs; negative and boundary controls are
  covered. No realistic sensor behavior is inferred.

## Fresh checks

```text
python -m unittest discover -s tests/instruments -v
Ran 6 tests ... OK
python -m compileall -q Build/instruments contracts/fit
git diff --check
```

## Integration pointer

Fitter should import `contracts.fit.quantity.Quantity` or
`contracts.fit.quantity.validate_quantity`; see `contracts/fit/CONTRACT.md`.
Shared contract commit: `dd0f1b98c227005ea7bbee9f0e7f9ce25313eff9`.

## Limits

No physical coverage, calibration, S07/S09 readiness, model/checkpoint,
network, deployment, or gate claim is established. Floating-point serialization
uses ordinary Python numbers; consumers needing decimal presentation should
format at their boundary rather than alter the numeric contract.
