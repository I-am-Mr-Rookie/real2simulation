# S10 trajectory child evidence

This child implements only the pure browser ESM trajectory kernel. It consumes caller-explicit numeric inputs and imports the authoritative fixed-step RK4 core at `Build/simulator/rk4.mjs`; that core is read-only peer work and is not duplicated here.

## Fresh check

Against the accepted main RK4 import:

```text
node --test tests/simulator/trajectories.test.mjs
6 passed, 0 failed
```

The tests compare free-fall RK4 output with the S08 closed-form reference, check horizontal projectile motion, explicit `simulated`/`synthetic` labels, finite/dense validation, deterministic output, deep immutability, honest sampled stop-plane crossing metadata, and the integer-horizon contract.

## Limits

Fractional duration/time-step horizons are intentionally outside this child’s supported domain unless they are only floating-point representation noise near an integer; no remainder is silently truncated. No contacts, bounce, real-scene, physical approval, Gate P, Gate M, S12, or production claim follows.
