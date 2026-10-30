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

Every clip-backed demo has:
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

S18b adds a disjoint **local synthetic** source/provenance variant to v1.
It does not invent footage, a licence, a source clip ID, GPU job or paid ledger.
These records use `source.kind: synthetic`, `label: simulated`,
`artifact.kind: simulation-record` and
`provenance.execution: accepted-local-simulation`. The original acceptance file
must declare `source: simulated` and the synthetic four-template scope. A record
pointer selects a passed deterministic free-fall case; every numeric pointer is
confined to that case. The hashed actual run report must identify the original
evidence path. Clip-backed entries still require the unchanged current approval,
acquisition, licence, successful app/ledger and clip-identity checks.
Neither variant proves independent controller acceptance; the evidence checkout
must be trusted.

## Precomputed free-fall display catalogue (S18b)

```powershell
python -B -m Build.library.free_fall
python -B -m Build.library.validate test-data/library-artifacts/free-fall.json
python -B -m unittest discover -s tests/library -t tests/library
```

`free-fall.json` contains four **SIMULATED, display-only** cases from the actual
`S10hi-gate` acceptance run: baseline-short, upward-launch, tiny-height and
low-gravity-long-horizon. Its single shared content-addressed object preserves
the entire original acceptance JSON byte-for-byte (including other templates);
only the four free-fall records are indexed. Numeric values are copied through
verified JSON pointers, never recomputed or authored by this builder.
Stored replay/trace hashes are historical outputs, not bundled replay samples.

The fifth entry is the already-licensed RM02 S06d reconstruction **descriptor
only**, checked again against current scoped approval and acquisition receipts.
It is NOT a measured free-fall demo and is not the source of the synthetic
numbers. No PLY, raw media or playable trajectory is bundled. The builder reuses
the S18a example writer (refreshing `manifest.json`) and create-once object store.

Every entry retains `SCALE_UNVERIFIED` and the verbatim physical readiness label
`Gate M: NOT_MET_INPUT_READINESS` from `evidence/S10/GATE-P.json`.
The actual S07f Gate M receipt independently retains the same status, zero
eligible/measured trials and physical evaluation `NOT_RUN`. S07c-e synthetic
verification does not qualify a real clip for metric fitting; no real g/uncertainty
is asserted here. Routes/playback remain S18f/g work; successful offline validation
does not unblock physical gates or demonstrate guest UI playback.

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
