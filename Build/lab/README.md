# Offline synthetic ballistic lab

Run from the repository root:

```powershell
python -m Build.lab.pipeline path/to/spec.json path/to/scene.json path/to/instruments.json
python -m unittest discover -s tests/lab -v
```

Requires the existing Python experiment validator dependencies and Node.js.
The scene bundle must include its referenced assets beside `scene.json`.
This CLI validates the full S08 setup, invokes the actual Node fixed-step RK4,
models light-gate and ruler observations, and invokes the actual S11 fitter.
Only synthetic free-fall/projectile scenes and downward displacement are supported.
Upward-launch free fall is rejected; samples are never selected to improve a fit.

All instrument fields are explicit:

```json
{"time_resolution_s":0.000001,"time_uncertainty_s":0.000001,"time_bias_s":0,"distance_resolution_m":0.000001,"distance_uncertainty_m":0.000001,"distance_bias_m":0}
```

Fitter uncertainty assumes fixed clock/scale and iid residuals; instrument
uncertainties are carried but not propagated. A fit error is returned honestly.
Output is internal diagnostic data, **not a Mystery-g public payload**, measured
physics, real reconstruction, calibration, a deployed product or a gate pass.
