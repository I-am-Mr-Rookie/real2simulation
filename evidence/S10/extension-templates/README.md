# S10e extension-template evidence

## API contract

`extendedTemplateApi` exports:

```js
rampTrajectory({ origin: number[3], length, inclineAngle, frictionCoefficient, initialSpeed, gravity, dt, steps, source: 'simulated', inputProvenance: 'synthetic' })
pendulumTrajectory({ origin: number[3], length, initialAngle, initialAngularVelocity, gravity, dt, steps, source: 'simulated', inputProvenance: 'synthetic' })
extendedTrajectoryFromValidatedArtifact(rawExportValidatedSetupEnvelope)
```

Both return frozen `{kind, source, inputProvenance, integrator:'rk4-fixed-step', dt_s, requestedSteps, units, analyticComparison, samples}`. Ramp samples map `time_s`, `distance_m`, `speed_m_s`, `position_m`, `velocity_m_s`; pendulum samples map `time_s`, `angle_rad`, `angular_velocity_rad_s`, `position_m`, `velocity_m_s`. Ramp uses S08-compatible positive acceleration `g*sin(angle) - friction*g*cos(angle)` and rejects `a <= 0` coasting/stalling/static-friction regimes. It stops at the first sampled endpoint crossing: emitted geometry is before the endpoint and `stop.bracket.after` contains only scalar crossing state. Pendulum uses nonlinear `theta'' = -(g/L)*sin(theta)`. The small-angle comparison is labelled only for amplitude <= 0.1 rad; larger amplitudes are nonlinear-only.

`extendedTrajectoryFromValidatedArtifact` consumes the actual `Build/simulator/export_validated_setup.py` envelope and requires the existing `artifact_version`, `validation`, producer, synthetic scene, world -Y gravity, explicit schema quantities, and integer duration/time-step horizon. It does not replace Python `validate_setup`.

All values are synthetic/simulated. This is not Gate P/M evidence.

## Fresh checks

- `node --test tests/simulator/extended-templates.test.mjs tests/simulator/trajectories.test.mjs`: 13 passed, 0 failed.
- `PYTHONPATH=tests/spec;tests/simulator python -m unittest test_ramp test_pendulum -v`: 23 passed, 0 failed.
- Real Python export envelope consumed for both ramp and pendulum in the JS test.
- `git diff --check`: pass.
