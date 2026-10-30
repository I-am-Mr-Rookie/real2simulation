# Library manifest v1 (S18a)

Offline **local-processing-only** contract. This does not publish demos, create routes,
authorize raw-media redistribution, or satisfy Gate D. S18f/g own route integration.
The current example is a validated **descriptor**, not a runnable/viewable asset bundle.

```powershell
python -m Build.library.example
python -m Build.library.validate test-data/library-artifacts/manifest.json
python -m unittest discover -s tests/library -v
```

## Format and immutability

`manifest.schema.json` is Draft 2020-12; `$defs/artifact` defines the artifact record.
`schema_version` is exact `1.0.0`; unknown fields/versions fail closed. Manifest max
256 KiB, 100 unique demo IDs; JSON artifacts max 64 MiB, matching viewer asset limits.

Artifacts are exact, unchanged UTF-8 JSON bytes from accepted evidence. Store at
`objects/sha256/<lowercase SHA256 of exact bytes>.json`; byte count and digest must
match. Whitespace/newlines affect the digest. Never overwrite: changed bytes get a
new digest/path and a new manifest reference. The example writer uses exclusive
creation and verifies existing bytes. Hash addressing detects mutation; it is not
an OS write-protection mechanism, signature, or proof of scientific correctness.
The manifest is a mutable local index; its objects are immutable by this convention.
The object directory's `.gitattributes` disables Git newline conversion. Evidence
references also hash exact checkout bytes; after an evidence checkout with different
line endings, regenerate the local manifest with `python -m Build.library.example`
rather than treating a hash mismatch as permission to skip validation.

Every demo has:
- Source clip ID, acquisition SHA256, source/licence URLs, licence, attribution.
  Validator re-derives these from `clips.csv`, S02c acquisition registry and the
  **current** scoped owner grant; old CSV approval flags are not authoritative.
- Artifact kind, MIME, byte count, SHA256 and digest-derived relative path.
- Actual run ID, hashed REPORT, hashed ledger, successful ledger app ID, hashed
  original evidence, and nonempty numeric provenance. Numeric RFC6901 pointers
  resolve to finite values in the artifact or **that app's** ledger job; equality
  is checked, not trusted from caller text. Names/units describe the evidence;
  they are not independently calibrated scientific claims.
- `measured`, `simulated`, or `fixture` labels; per-number labels match the demo.
  Measured reconstruction output is **not** physical measurement. Fixture values
  must never be presented as measured outputs. Simulation/fixture records require
  matching `clip_id` and `label` in their accepted JSON evidence and matching kind.
- `scale_verified: false`, `SCALE_UNVERIFIED`, Gate M/RS `NOT_MET`, Gate R
  `NOT_MET`/`NOT_RUN`, explicit limitations and `availability: metadata-only`.

v1 deliberately disallows passing gates, verified scale and playable/public status.
Promoting these requires a reviewed contract change backed by actual evidence;
callers cannot flip a flag. Do not infer gate success from successful validation.
Existing `public_receipt` restricts Gate RS physics categories; reconstruction
is not one of them. This validator reuses its authoritative `approved` and licence
allowlist helpers **without broadening** Gate RS eligibility or modifying that code.

Scene-descriptor payloads pass scene-v1 structural validation and viewer point/
asset-byte limits. Assets referenced inside the descriptor are **not bundled,
fetched, hashed or promised available** by S18a. Future precompute/bundle work must
validate the actual assets with `contracts/scene/validate_scene.py` and the viewer
loader before exposing a playable demo. No browser/runtime verification here.

## Example custody

`test-data/library-artifacts/manifest.json` derives RM02 from accepted S06d-orch23
scene metadata and job ledger. Its function duration is copied, not authored;
the exact scene descriptor bytes are stored content-addressed. Licensed PLY/frames
remain absent (not redistributed). Model nominal metric scale is unverified,
gravity unknown, physics disabled. S12e and parent S18/Gate D remain incomplete.

Evidence-root validation assumes a trusted repository checkout of accepted run
records: existence/hashes prove custody, not controller acceptance, model accuracy,
or an app's independent attestation of which pixels generated its output. No
network, GPU/API calls, dependency installation, secrets or canonical-control edits.
