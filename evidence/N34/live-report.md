# Lab report: measure the gravitational acceleration g from a falling object

_Label: SIMULATED. Every number below comes from the server physics run (Rapier (same world as the editor Play, room collision proxy included), dt 1/120 s) and Build/fitter. Nothing here is MEASURED from a real video._

Generated 2026-11-01 20:32 UTC.

## Aim

Use the virtual lab to measure the gravitational acceleration g from a falling object.

## Setup

- Gravity setting: 9.81 m/s^2 (scene input); floor: ply
- Engine: Rapier (same world as the editor Play, room collision proxy included), dt 1/120 s

| id | kind | mass (kg) | size (m) | position (m) | params |
|---|---|---|---|---|---|
| ball-1 | ball | 1 | 0.05 x 0.05 x 0.05 | 0, 1.2, 0 | none |
| ball-2 | ball | 1 | 0.05 x 0.05 x 0.05 | 0, 1.2, 0 | none |

## Data

| object | samples | duration (s) | ended |
|---|---|---|---|
| ball-1 | 59 | 0.4833 | floor_contact |
| ball-2 | 59 | 0.4833 | surface_contact |

## Fit with uncertainty

Uncertainties are one sigma, from Build/fitter with the declared noise below.

- ball-1: g = 9.50122 ± 0.014 m/s^2 by Build/fitter degree-2 fit of height vs time; fall 1.175 m; rmse 0.00093 m; declared position sigma 0.001 m (assumed)
- ball-2: g = 10.1188 ± 0.014 m/s^2 by Build/fitter degree-2 fit of height vs time; fall 1.126 m; rmse 0.00093 m; declared position sigma 0.001 m (assumed)

## Conclusion

ball-1: g = 9.50122 ± 0.014 m/s^2 (SIMULATED) against the scene setting 9.81 m/s^2; difference -0.309 m/s^2 (22 sigma), not consistent within 2 sigma. ball-2: g = 10.1188 ± 0.014 m/s^2 (SIMULATED) against the scene setting 9.81 m/s^2; difference 0.309 m/s^2 (22 sigma), not consistent within 2 sigma.

Limits: an ideal simulation recovers its own inputs; this checks the method, not the real world. Scale and noise are declared, not calibrated.
