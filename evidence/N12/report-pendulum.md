# Lab report: find the period of a pendulum

_Label: SIMULATED. Every number below comes from the server physics run (RK4) and Build/fitter. Nothing here is MEASURED from a real video._

Generated 2026-11-01 11:54 UTC.

## Aim

Use the virtual lab to find the period of a pendulum.

## Setup

- Gravity setting: 9.81 m/s^2 (scene input); floor: plane
- Engine: server RK4 (Build/simulator/rk4.mjs), dt 1/120 s, no contacts except the floor stop

| id | kind | mass (kg) | size (m) | position (m) | params |
|---|---|---|---|---|---|
| pendulum-1 | pendulum | 1 | 0.1 x 0.1 x 0.1 | 0, 1.3, 0 | length 0.8, angle_deg 30 |

## Data

| object | samples | duration (s) | ended |
|---|---|---|---|
| pendulum-1 | 1201 | 10 | duration |

## Fit with uncertainty

Uncertainties are one sigma, from Build/fitter with the declared noise below.

- pendulum-1: T = 1.82552 ± 0.00046 s by Build/fitter linear fit of mid-line crossing times vs crossing index over 11 crossings; declared crossing sigma 0.00241 s (assumed)
  - THEORY small angle period: 1.79428 s
  - THEORY large angle period: 1.82551 s

## Conclusion

pendulum-1: period T = 1.82552 ± 0.00046 s (SIMULATED); THEORY reference 1.82551 s.

Limits: an ideal simulation recovers its own inputs; this checks the method, not the real world. Scale and noise are declared, not calibrated.
