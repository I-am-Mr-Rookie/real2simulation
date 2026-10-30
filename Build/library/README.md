# Library manifest v1 (S18a)

## Anonymous read-only API (S18f)

`Build.library.guest.create_app(root=ROOT)` is an unmounted FastAPI factory.
No credentials, providers, guardrails, inference, network requests, asset fetches,
or writes are needed. S18f does **not** change the deployed health API or web app.
See [the exact S18g interface](../../evidence/S18/S18f-GUEST-INTERFACE.md).

- `GET /api/library/manifest`: `guest-1.0.0` guest projection of five explicitly
  selected, validated catalogues. Includes SIMULATED / SCALE_UNVERIFIED display-only
  entries, UNAVAILABLE Apollo/bounce/RM05, safe per-demo/default selection, and
  content-addressed guest artifact URLs. Successful manifest and handler errors use
  `Cache-Control: no-store`.
- `GET /api/library/artifacts/{sha256}`: only lowercase 64-hex hashes present in
  the validated guest projection. JSON bytes are bounded and SHA-256 checked;
  success has quoted ETag, JSON content type, byte Content-Length, nosniff and
  `Cache-Control: public, max-age=31536000, immutable`.
- Guest objects are read-only in-memory projections, not newly persisted local
  artifacts. Scene descriptor/challenge bytes keep their original object hashes.
  Simulation objects expose only selected setup metadata and have **new hashes**;
  raw local acceptance objects (including a known source hash) are not addressable.
  Audit reports/ledgers are never followed by the HTTP artifact route.
- All guest defaults expose no numeric parameters; no alternative catalogue can
  disclose the Mystery-g gravity/seed/replay/diagnostic answer. Repository/source
  access is still outside this guest security boundary.
- Validation is request-time, not startup-only: revocations or changed/missing
  source/evidence bytes fail closed with 503 on the next request. Invalid IDs
  return 400, valid unknown hashes 404, non-GET methods 405. No path is formed
  from the user ID. Canonical catalogue paths and object refs reuse containment
  validation, byte limits, custody and owner-grant checks.

This is metadata, **not playable demos**: no PLY/frames/trajectories are bundled,
no public raw-media redistribution is authorized, no calibration/gate is promoted.
Current tradeoff: all five small catalogues are validated for each valid request;
cache/precompute only with an explicit authority/custody invalidation design if
the library grows. The existing validator's numeric/fitter imports are offline
helpers; provider/GPU/guardrail imports and process/network calls are tested absent.

## Apollo and Mystery-g (S18e)

- [Apollo 15 — UNAVAILABLE / Moon result not measured](../../evidence/S18/Apollo-UNAVAILABLE.md).
  AP15 is excluded by current owner approval and not trackable; no Apollo demo,
  fitter result or lunar numeric claim is fabricated.
- `python -B -m Build.library.mystery_g` reproducibly builds
  `test-data/library-artifacts/mystery-g.json` from accepted S10 lab records.
  This is SIMULATED, metadata-only, not a new Mystery-g run or playable replay.
  It links the existing `/lab` challenge; its server-owned session/fit handles reveal.
- `challenge-record` is a content-addressed **allowlist projection** containing
  only simulated setup duration/time step and challenge labels. Both numbers
  retain artifact JSON pointers and are compared to the accepted source case.
  Gravity, seed, trajectory, replay hashes and diagnostic metrics are absent;
  defaults expose no parameters and leave autoplay/physics OFF. Validator rejects
  raw acceptance bytes, rehashed extra fields, answer metadata and reveal flags.
- The provenance source/report references are **offline audit custody**, not a
  public challenge payload. A future guest endpoint must serve only the selected
  challenge object, never follow audit refs or expose arbitrary catalogue objects.
  Other local catalogues intentionally include answers; repository access is not
  a hidden-answer security boundary. S18f/g still own guest routing/UI integration.
- SCALE_UNVERIFIED, Gate M/RS NOT_MET, real-scene prediction WITHHELD and S12f
  VIRTUAL_LAB_ONLY remain unchanged. No GPU/API/simulator run is needed to rebuild.

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
pointer selects a passed deterministic free-fall, projectile or pendulum case; every numeric
pointer is confined to that case. Its ID must match the selected template and case.
The hashed actual run report must identify the original
evidence path. Clip-backed entries still require the unchanged current approval,
acquisition, licence, successful app/ledger and clip-identity checks.
Neither variant proves independent controller acceptance; the evidence checkout
must be trusted.

## Pendulum and scene display catalogues (S18d)

```powershell
python -B -m Build.library.pendulum
python -B -m Build.library.scenes
python -B -m Build.library.validate test-data/library-artifacts/pendulum.json
python -B -m Build.library.validate test-data/library-artifacts/scenes.json
python -B -m unittest discover -s tests/library -t tests/library
```

`pendulum.json` indexes all four accepted S10hi-gate pendulum cases from the same
immutable S10 acceptance object used by free-fall/projectile. Numbers retain exact
JSON pointers into their original case; labels are SIMULATED/SYNTHETIC. This is
acceptance-summary metadata, not a new simulation, trajectory, fitted real pendulum
or S12 held-out prediction. S11/S12 fixtures are not relabelled as measured data.

`scenes.json` indexes accepted RM02/S06d and RM04/S06f MapAnything scene descriptors,
byte-for-byte and content-addressed. Source licence/credit is verbatim `clips.csv`;
only the scene contract's known `Pexels License` -> `Pexels` spelling is normalized
for comparison. RM04 selects the successful ledger job, not its failed preflight.
The `measured` label means reconstruction/job output, never calibrated physics.
No raw clip, PLY asset, physical fit, collider or calibrated dimensions are bundled.
RM05's accepted S05 raw reconstruction is not a scene-v1 viewer descriptor: see
[`RM05-scene-UNAVAILABLE.md`](../../test-data/library-artifacts/RM05-scene-UNAVAILABLE.md).

Both new catalogues expose an optional v1 `defaults` object. Older v1 catalogues
remain valid unchanged. `demo_id` identifies the initial metadata selection:
the shortest accepted pendulum horizon (`short-small-angle`), or RM02 for scenes.
Pendulum `parameters` copy only the recorded gravity/duration/time-step numeric
entries, with their original units, simulated labels and evidence pointers.
Scene defaults expose no physics parameters. These are **not executable specs**;
there is no playback/UI wiring here. Autoplay and physics are fixed OFF, real-scene
prediction is WITHHELD. The validator rejects unknown demo IDs, fabricated or
cross-case defaults, executable safety-switch changes, missing/stale fallback
evidence, and parameters on display-only scene defaults.

Defaults hash-link the actual S12f fallback and its Gate RS record. The validator
requires `VIRTUAL_LAB_ONLY`, `WITHHELD`, and Gate RS `NOT_MET`; a changed gate/fallback
needs explicit review rather than silent promotion. SCALE_UNVERIFIED, metadata-only
availability, Gate M/RS NOT_MET and Gate R NOT_MET/NOT_RUN remain unchanged.

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

## Projectile catalogue and unavailable bounce (S18c)

```powershell
python -B -m Build.library.projectile
python -B -m Build.library.validate test-data/library-artifacts/projectile.json
python -B -m unittest discover -s tests/library -t tests/library
```

`projectile.json` indexes only the four accepted S10hi-gate projectile cases:
baseline-short, zero-horizontal, tiny-height and low-gravity-long-horizon.
It reuses `free_fall.simulated_demos`, the same immutable acceptance object,
numeric JSON pointers and original run report. Free-fall output stays unchanged.
There is no made-up PJ03/BN01/RM05 clip, licence, descriptor, job or ledger.
These are **SIMULATED, metadata-only, pre-contact** outputs, not real-clip
held-out comparisons, uncertainty estimates or playable trajectories.

Bounce is explicitly **UNAVAILABLE**; see
[`bounce-UNAVAILABLE.md`](../../test-data/library-artifacts/bounce-UNAVAILABLE.md).
BN01 chunk tracking stopped fail-closed, the accepted Gate RS bounce category
is an untracked shortfall, and S10/S11 contain no accepted bounce template.
No fake bounce manifest is generated. SCALE_UNVERIFIED, Gate M NOT_MET and
Gate RS NOT_MET remain unchanged; this partial child does not complete parent S18.

Existing `public_receipt` restricts Gate RS physics categories; reconstruction
is not one of them. This validator reuses its authoritative `approved` and licence
allowlist helpers **without broadening** Gate RS eligibility or modifying that code.

Scene-descriptor payloads pass scene-v1 structural validation and viewer point/
asset-byte limits. Assets referenced inside the descriptor are **not bundled,
fetched, hashed or promised available** by S18a. Future precompute/bundle work must
validate the actual assets with `contracts/scene/validate_scene.py` and the viewer
loader before exposing a playable demo. No browser/runtime verification here.

## Guest loader integration (S18g)

`loader.mjs` exports `loadLibraryEntry(entry, { signal, fetch })`: bounded,
SHA-verified guest metadata with SIMULATED / SCALE_UNVERIFIED / UNAVAILABLE labels
and immutable safe defaults. Real descriptors produce the unchanged viewer's
validated guest/inspect request; current entries cannot mount because the guest
API exposes metadata, not render assets or trajectories. No app/viewer edits.
See [exact one-call wiring and kind mapping](../../evidence/S18/S18g-LOADER-INTERFACE.md).
The standard library Python suite also runs the Node loader contract tests.

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
