# Gate M: reproducible actual-source evaluation

```powershell
python -m Build.measurement.gate_m --output evidence/S07/S07e/actual-gate-m.json
python -m unittest discover -s tests/measurement -v
```

Run from repository root. Gate command exit **1** is expected with current inputs:
**NOT_MET_INPUT_READINESS**, physics **NOT_RUN**, not measured accuracy failure.
Implementation/test success is distinct from physical gate acceptance.
No API/model/SAM/GPU/download/decode/secret operations or new dependencies.

The command reads current clips.csv, the exact reviewed S02e scoped receipt,
S02f replacements and S02i clock/projection evidence. Artifact fingerprints all
consumed evidence plus frozen implementation. S07a historical counts are not
substituted for current rows. Raw media are not opened; recorded source-byte
hashes are inherited receipts, not fresh file verification. Current base includes
all accepted sources; compare hashes with canonical before controller acceptance.

Only the reviewed receipt hash (normalizing CRLF to LF) grants the listed **scene_tracking** IDs. It
grants **no metric input**, including ST03. Changed receipt means unknown/deny,
not permission inferred from CSV owner flags, scope strings or evidence text.
Replacement RP01 remains useful for partial-flight tracking (floor contact is
not required), but S02i does not resolve capture clock or metric projection.
No original input, approval or source evidence is modified.

## Fixed gate, not a reduced denominator

Exactly three preselected independent Earth trials, at least two within
**5% of 9.81 m/s²**, with honest uncertainty covering reference error. The target
9.81 is comparison-only, never an input to scale/clock/fitter. Unknown groups
and overlapping takes cannot count as independent. No best-three selection.
Fewer trials, unknown coverage, or absent qualification cannot pass. All eight
reviewed candidates remain visible, not eight measured benchmark trials.

Current artifact: one scene-approved Earth candidate, zero metric-approved,
zero eligible and zero measured trials; measured g/errors/coverage are **null**.
Counts/successes are zero, not fabricated physical numbers. No empty coordinate
record is constructed to pretend validation/tracking ran. The real abstention
is the current authoritative permission and missing calibrated-input boundary.

## Fitter path and uncertainty limit

`evaluate_record` reuses accepted validator, fitter, suffix evaluator and S07d
propagation only after a trusted caller explicitly authenticates metric use and
custody outside the record; defaults deny. Actual-source CLI cannot set these
flags under current receipts. This is not a new approval/custody verifier.
Any later metric integration must review actual source bytes/licence, scope,
independent calibration, capture clock, frozen prefix/suffix and assumptions;
this run does not authorize that integration.

S07d returns a conditional **standard uncertainty**, explicitly not a coverage
interval. No multiplier, Gaussian distribution or coverage probability is
invented. Even the synthetic fitter path therefore leaves covering uncertainty
null and cannot pass. Missing uncertainty assumptions abstain without emitting
partial metric output. Summary threshold regressions with explicit synthetic
coverage booleans test policy arithmetic only, not establish physical coverage.

R-M must review these boundaries, including the unresolved coverage methodology.
S07f must explicitly record the authorized fallback decision. This evaluator
does not enact table-plane fallback, pass parent S07, or unlock S12.
