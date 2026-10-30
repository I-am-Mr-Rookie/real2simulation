# S18d offline catalogue verification

Scope: accepted synthetic pendulum summaries and accepted scene display descriptors
only. No new GPU/API/simulator execution or authored experiment numbers.

- `pendulum.json`: four passed deterministic S10hi-gate pendulum cases, exact
  `evidence/S10/acceptance/acceptance.json` bytes; six numeric pointers per case.
- `scenes.json`: RM02 S06d and RM04 S06f exact scene-v1 descriptors. Licence,
  attribution, source URLs, acquisition hashes and current approval rechecked.
  RM04 uses ledger job 1 (successful), not job 0 (refused preflight).
- `defaults`: shortest accepted pendulum horizon; RM02 scene first. Numeric
  pendulum fields are copied references, not newly authored settings. No scene
  physics parameters. Autoplay/physics OFF; real-scene prediction WITHHELD.
- S12f fallback hash and referenced Gate RS hash validated; VIRTUAL_LAB_ONLY,
  NOT_MET, SCALE_UNVERIFIED and metadata-only availability remain.
- RM05 accepted raw S05 reconstruction is not converted into an unaccepted scene;
  linked `RM05-scene-UNAVAILABLE.md` records that distinction.

Fresh checks and source custody are saved beside this file. Unit tests exercise
all catalogue entries, build reproducibility, existing catalogue preservation,
numeric pointers, malformed defaults, source/credit forgery, refused-job selection,
fallback decision/hash tampering, and gate/scale/playable promotion refusal.

Limit: these are local metadata indexes, not playable trajectories/PLY media,
real-scene prediction, calibrated physics, or independent acceptance attestation.
Trusted checkout hashes establish custody only; no publication rights are inferred.
