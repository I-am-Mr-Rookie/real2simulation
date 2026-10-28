# Owned-module edge cases — F-CODEX-1-1

What this change does: This review adds evidence only. It checks finished CODEX-1 scene/spec validators and four analytic references. The results below are offline synthetic observations, not reconstruction, measured physics, simulator accuracy or a gate result.

Assumed load: one local caller today; repeated scene/oracle calls are a future integration risk, not a measured production load. Baseline: 91 spec tests and 11 scene tests pass; these counts do not disprove the cases below.

## Should fix

1. **Free fall leaks an arithmetic exception for an invalid sample time** — reproduced P1.
   - **What this is:** `Build/templates/free_fall.py:74–77` validates explicit sample times. The other references check the allowed range before converting to a floating-point number.
   - **Problem:** `times=[10**1000]` raises `OverflowError: int too large to convert to float`, while the other three references reject the same input with a field-specific `ValueError`. This matters to a caller that handles invalid inputs with `ValueError`; no such external caller was inspected in this scoped run.
   - **Fix:** Check `0 <= t <= limit` before `math.isfinite(t)`, as projectile/ramp/pendulum already do. Add the huge positive and negative integer cases to free-fall invalid-time checks.
   - **If we skip it:** A programmatic caller can receive an unexpected exception instead of a readable invalid-time reason. HTTP exposure/error handling remains unexamined.

2. **Accepted tiny motion disappears in world coordinates** — reproduced P2; extreme numeric domain, not normal-sized demo failure.
   - **What this is:** `contracts/experiment/validate_experiment.py:218,254–255` checks body-size precision; `Build/templates/free_fall.py:79,90` computes the world-space stop plane by subtraction.
   - **Problem:** With synthetic origin `[0,2,0]`, zero initial vertical velocity and `drop_height=1e-20`, setup accepts a positive height. The oracle returns a positive analytic impact time, but initial and impact positions both equal `[0,2,0]`: the requested displacement is smaller than representable spacing near Y=2. The radius precision check does not check trajectory displacement.
   - **Fix:** Reject a positive stop-plane displacement that rounds back to the original world coordinate, with a readable parameter error; or explicitly support local-relative output before allowing this range. Add this synthetic endpoint case without weakening existing radius/energy checks.
   - **If we skip it:** A future position-based comparison may see no motion for an accepted experiment. No current simulator/gate failure is claimed.

## Integration checklist — documented limits, not newly discovered bugs

- [ ] **Setup validity is not oracle availability (P3 reproduced).** Ramp friction coefficient 10 and pendulum release angle 0.2 rad pass `validate_setup` with timestep 0.0001 s, then their oracles reject the unsupported domains. `ramp.py:8–15,44–45,55–58` and `pendulum.py:8–19,47–48,58–61` deliberately add narrower conditions. Before presenting runnable cards, require factory/oracle capability checks, not numeric/setup success alone. Recheck positive downhill acceleration and small-angle amplitude at dispatch; never label this intentional split a validator bypass.
- [ ] **Bind evidence to an immutable experiment revision (P4 reproduced).** `free_fall.py:67` uses method + experiment ID. Two valid specs with the same ID and heights 1 versus 0.5 produce different analytic times but identical evidence strings. Before persistence/export, require immutable IDs per revision or a canonical input digest and scene/asset version. No storage/caller was read, so this is an unresolved integration requirement, not proof of a persisted provenance collision.
- [ ] **Do not enable physical supports from these templates (reading only).** `validate_experiment.py:273` rejects every non-null support surface; ramp's ideal centre path has no contact attachment. Add positive/negative contact-frame cases only in the separately authorized builder/contact run. Existing fail-closed behavior is intentional.
- [ ] **Keep scene-byte work off repeated hot paths without weakening trust (reading only).** Every factory and oracle calls `validate_setup`; it calls scene validation at line174, which hashes every asset (`validate_scene.py:125–128`) and scans point-cloud bodies (`:52–80,137–145`). Factory then oracle means at least two bundle validations. Benchmark repeated calls with a rights-cleared real-size bundle before optimizing. If needed, reuse only a trusted immutable/hash-bound validation result, not unchecked client metadata. No timings or denial-of-service claim were measured.
- [ ] **Preserve codec and rights boundaries (reading only).** Scene validation checks file bytes/hash, not full GLB/splat decoding (`validate_scene.py:146–151`); scene README explicitly defers these adapters. Provenance strings do not independently authenticate clip approval. Future consumers must validate payloads and resolve owner-approved source records, never infer those guarantees from schema success. No malformed real media, external URL, private data or rights assertion was tested.

## Evidence and reproducibility

- `python -B evidence/fillers/CODEX-1/1/probes.py`: eight observation records; exit0 means reproduced observations, **not** product correctness.
- `probes.json`: exact exception classes/messages, synthetic positions, domain split, evidence identity and SHA256 fingerprints of reviewed source.
- `spec-regression.txt`: existing spec suite, 91 tests, OK.
- `scene-regression.txt`: existing scene suite, 11 tests, OK.
- Probe P3 initially failed its setup displacement guard; changed only the evidence probe timestep to0.0001 s and reran. The guard was not changed or bypassed in product code.

Verdict: fix 1 and 2 before promising uniform invalid-input errors or support for the entire accepted numeric range. The evidence-only deliverable is complete; product changes need a separate authorized run.

Not checked: downstream other-lane callers/storage/viewer/API, integrations, real clips, GLB/splat decoders, runtime performance, simulator or any event gate.
