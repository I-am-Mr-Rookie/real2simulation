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
    "provenance": "synthetic fixture: stopwatch seed 7"
  }
}
```

Required fields are `value`, `unit`, non-negative `uncertainty`, and
`source.label == "simulated"` plus non-empty `source.provenance`. All numeric
fields reject booleans, NaN, and infinity. `error` is optional and represents a
signed instrument perturbation; it is not folded into `uncertainty`. No default
unit, uncertainty, bias, calibration, or physical/real provenance is supplied.
