# S11 shared quantity contract (simulation-only)

Import `contracts.fit.quantity.Quantity` or call `validate_quantity(payload)`.

```json
{
  "value": 9.81,
  "unit": "m/s^2",
  "uncertainty": 0.05,
  "error": 0.01,
  "source": {
    "label": "simulated",
    "evidence": "synthetic fixture: stopwatch seed 7"
  }
}
```

Required fields are `value`, `unit`, non-negative `uncertainty`, and
`source.label == "simulated"` plus non-empty `source.evidence`; unknown fields
are rejected. Allowed units are exactly `s`, `m`, `px`, `m/s`, and `m/s^2`; an
arbitrary unit such as `bananas` is rejected at this boundary. `uncertainty` is
a non-negative standard uncertainty in the same unit as `value`. All numeric fields reject
booleans, NaN, infinity, and overflowing integers. `error` is optional and is
the total known signed perturbation (`observed - true`), kept separate from
standard uncertainty. No default unit, uncertainty, bias, calibration, or
physical/real provenance is supplied.
