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

## S07f review response

`summarize(trials, *, independence_verified=False)` derives qualification and
mean relative error from finite `g_m_s2`, never a caller's `relative_error`.
The inclusive 5% boundary is compared in g-space, without an invented tolerance;
the reported divided error can round just above .05 at the inclusive endpoint.

Distinct raw labels do not prove independence. Only a trusted caller that has
authenticated the **exact panel's recording provenance** outside the dictionaries
may pass `independence_verified=True`; otherwise the verified independent count
is zero. IDs must be nonempty, case-sensitive and without surrounding whitespace.
Padding is rejected, not normalized; case differences neither prove nor disprove
physical independence. FF01/FF02 share the documented capture group. No provenance
authenticator or new metric grant is implemented; the actual-source CLI never
sets this flag. Synthetic true flags/coverage booleans exercise policy only.

R-M F3's unknown coverage is intentional; F4's suffix RMSE remains a diagnostic,
not a new Gate M/Gate RS threshold. F5/F6 conditional precision and small-error
adequacy still require independent evidence (see UNCERTAINTY.md); no residual,
chi-square, relative-uncertainty or interval multiplier gate was invented.

See `evidence/S07/S07f/ADJUDICATION.md` and `DECISION.md` for source response and
actual Apollo/fallback decision. Other-vendor follow-up of S07f gate changes is
required before controller acceptance. This evaluator does not enact calibrated
table-plane fallback, pass parent S07, or unlock S12.
