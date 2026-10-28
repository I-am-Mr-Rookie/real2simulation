# S10 trajectory child evidence

This child implements only the pure browser ESM trajectory kernel. It consumes caller-explicit numeric inputs and imports the authoritative fixed-step RK4 core at `Build/simulator/rk4.mjs`; that core is read-only peer work and is not duplicated here.

## Fresh check

With the peer RK4 file temporarily present at its eventual integration path:

```text
node --test tests/simulator/trajectories.test.mjs
4 passed, 0 failed
```

The tests compare free-fall RK4 output with the S08 closed-form reference, check horizontal projectile motion, explicit `simulated`/`synthetic` labels, finite/range validation, deterministic output, caller immutability, and honest sampled stop-plane crossing metadata.

## Limits

No S08 schema/validated-artifact adapter was available in this isolated child checkout, so this is numerical-kernel evidence only. Parent integration must wire the validated S08 artifact and peer RK4 commit before calling S10d integrated. No contacts, bounce, real-scene, physical approval, Gate P, Gate M, S12, or production claim follows.
