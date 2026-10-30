# S12f review packet (for cross-vendor reviewer)

**Claim:** real-clip prediction is WITHHELD from the real scene and limited to the virtual lab under the current accepted Gate RS result. Decision is computed by code, not prose.

## What decides
- [Build/real2sim/fallback.py](../../Build/real2sim/fallback.py) `from_evidence()` re-runs `score.gate()` on the stored per-category clip scores in `evidence/S12/gate-rs/gate-rs.json` and refuses (ValueError) if the recomputed result differs from the stored `result`.
- `decide(median)`: `median <= THRESHOLD (0.05, reused from score.py)` -> SHOWN; `(0.05, 0.10]` -> SHOWN_WITH_ERROR (measured error displayed); `> 0.10` -> VIRTUAL_LAB_ONLY (error label "measured"); `None`/NaN/inf/negative/bool/non-number -> VIRTUAL_LAB_ONLY, error label "unmeasured". Null median = any missing category or coverage < 80% (score.gate contract).
- `label(doc, decision)`: every output gets clip_id, provenance, units, gate_m, limits (verbatim), `scale_label` (SCALE_UNVERIFIED unless gate_m == MET), `trace_label` "simulated" (fitter-extrapolated prediction), `observation_label`, `error_label`, `display`, `banner`. Synthetic provenance -> banner SYNTHETIC, display VIRTUAL_LAB, error n/a.

## Current result (from [S12f-fallback.json](S12f-fallback.json); every number copied from scorer output)
- Gate RS NOT_MET, median null, shortfall projectile/bounce/pendulum; Gate M NOT_MET.
- ST03 diagnostic only: 7/466 scored frames, coverage 0.015021459227467811, normalized RMS 0.1981633916341227, scored false (ineligible).
- Decision: VIRTUAL_LAB_ONLY, real_scene_prediction WITHHELD, error_label unmeasured.
- overlay-ST03-v2.json -> "REAL CLIP - PREDICTION WITHHELD", VIRTUAL_LAB_ONLY, simulated, unmeasured, SCALE_UNVERIFIED.
- overlay-pendulum-SYNTHETIC-v2.json -> SYNTHETIC, VIRTUAL_LAB, SCALE_UNVERIFIED.

## Reproduce
```powershell
python -B -m Build.real2sim.fallback
python -B -m unittest tests.prediction.test_fallback -v
```

## Suggested attack points
1. Inclusive boundaries (0.05 -> SHOWN, 0.10 -> SHOWN_WITH_ERROR): matches "5-10% shown honestly"; challenge if the owner meant exclusive.
2. Labels live in the sidecar S12f-fallback.json keyed by output path + sha256; overlay documents/contracts (contracts/overlay, not owned) and the web/lab UI are NOT yet wired to read them. A consumer could still render the ST03 overlay without the withhold banner.
3. Inherited R-RS RECHECK4 H1 (P3): registry writers are trusted; a replaced trusted registry could make score.gate admit forged tracks. fallback.py adds no new trust boundary.
4. The decision uses only the median; a per-category > 10% with median <= 10% would still show. That follows the stated rule; flag if per-category gating is wanted.
5. "simulated" for the predicted trace means model rollout from the prefix fit, not a physics-engine run.
