# Bounce — UNAVAILABLE

No accepted bounce simulation or complete real-clip bounce evidence exists in
the source checkout for S18c. This is an availability note, **not a demo entry**;
there is deliberately no `bounce.json`, fixture or authored numeric output.

- BN01 tracking stopped fail-closed at **31/176 frames**: chunk-boundary text
  re-detection failed; the full segment was rejected (observed subset only OK).
  Source: [S07-chunktrack-orch67 report](../../Run-System/Runs/S07-chunktrack-orch67/REPORT.md).
- The accepted [S12e Gate RS receipt](../../evidence/S12/gate-rs/gate-rs.json)
  has `/clips/bounce: null` and
  `/result/per_category_normalized_rms/bounce: null`. Bounce remains an untracked
  shortfall, with no accepted prefix-to-committed-prediction-to-suffix comparison
  or sourced restitution/floor record. The older receipt's contiguous-job limit
  is historical; the later chunk-tracking attempt above still failed closed.
- The [S10 acceptance JSON](../../evidence/S10/acceptance/acceptance.json)
  contains free-fall, projectile, ramp and pendulum only; S11 acceptance evidence
  contains no bounce template. Pre-contact projectile motion is **not** bounce.

**SCALE_UNVERIFIED; Gate M NOT_MET; Gate RS NOT_MET.** No gate promotion,
calibrated metric result, held-out bounce error or uncertainty is claimed.
No raw footage, assets, licence or original clip identity is invented.

To make a bounce demo available, first accept a complete licensed clip-bound
bounce run (including tracking, floor/restitution provenance, held-out comparison
and uncertainty), or an explicitly accepted synthetic bounce simulation. Then
index its original bytes and JSON pointers through a reviewed validator change.
Do not fill this absence with a newly authored fixture.
