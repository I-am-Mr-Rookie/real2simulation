# S07 tracking input contract v1 (local, no fitter yet)

`inputs.validate_input(record)` validates a JSON-compatible object. Malformed
data raises `ValueError`. Valid scene/tracking input may carry abstention
`blockers`; an empty list means declared prerequisites are present, **not** that
rights/calibration were independently verified or Gate M passed. No model,
tracking, fitting, download, remote call or physical number is produced here.
This function is not an approval authority: a trusted run must resolve evidence,
licence and scope before use. Never manufacture `metric_measurement` approval.
Current S02 approval grants `scene_tracking` only for the ten listed IDs.

## Record

| Field | Contract |
|---|---|
| `clip_id`, `source_sha256` | Stable ID and exact source-byte SHA256 (64 lowercase hex). Changes to crop/edit/source require a new receipt and split. |
| `licence`, `provenance` | Nonempty source/licence identifier and reviewable receipt reference; preserve original attribution/rights in clips.csv. Presence is not rights clearance. |
| `approval` | `{scope: "scene_tracking" or "metric_measurement", evidence: receipt reference}`; missing approval fails, scene scope always blocks metric use. |
| `motion` | Nonempty classification; only `earth_free_fall` can be Earth-g eligible. Projectile, bounce, pendulum, ISS and lunar scenes never substitute. |
| `width_px`, `height_px` | Positive integer original image dimensions. Coordinates are source pixels: x right, y down, no silent resize/crop conversion. |
| `continuous_segment_evidence` | Reviewed uninterrupted, non-reversed, pre-impact fall segment. Null/empty => abstain. Repeats/edits/occlusions need explicit segment/time mapping before any fit. |
| `scale` | Null if unknown; otherwise independent in-plane reference with fields below. Unknown is not zero. |
| `timebase` | Null if unknown; otherwise verified capture-time mapping with fields below. File/container FPS alone cannot fill it. |
| `frames` | Ordered observations `{frame_index, pts_s, x_px, y_px}`; nonnegative integer source frame index, finite nonnegative PTS/coordinates within image, strictly increasing index AND PTS. No sorting, duplicates, interpolation or fabricated observations. |
| `last_training_frame` | Exact source index ending a >=3-observation prefix; must leave >=1-observation suffix. Split is fixed **before** calibration/fitting/evaluation. |

Scale fields: `method: "independent_reference"`, positive `m_per_px`, nonnegative
`uncertainty_m_per_px` (absolute one-standard uncertainty), `plane_verified: true`,
nonempty `evidence`. Reference receipt must state independently measured length,
its uncertainty, pixel extent/uncertainty, motion/reference coplanarity and camera
assumptions. Do not derive scale from fall time, assumed g, estimated ball/apple
diameter, model depth, an unrelated ruler segment or unverified standard sizes.
If perspective/camera motion invalidates a constant scale, abstain; a future
homography/world mapping is outside this v1 contract, not approximated here.

Timebase fields: positive `capture_seconds_per_pts_second`, nonnegative
`uncertainty_factor` (absolute one-standard uncertainty of that ratio),
`verified: true`, nonempty `evidence`. On a reviewed constant-rate continuous
segment, capture elapsed seconds = (PTS - first segment PTS) * ratio. Receipt
must establish the actual capture clock, slow-motion/edit factor and any clock
precision, timestamp jitter or repeated-frame treatment. PTS are presentation
seconds, **not** capture seconds. For VFR use actual per-frame PTS; if the capture
mapping is not constant/verified, leave timebase unknown. Do not silently use
`frame_index / file_fps`. Nonlinear mappings are outside this v1 contract.

## Held-out custody and uncertainty

The result contains frozen tuples of frozen `Frame`s: `training` prefix and
`held_out` suffix. Input mutation cannot alter them. A trusted custodian stores
source hash, selected segment, immutable split, calibration evidence and config
hash **before** any fit. Send only `training` and frozen prefix-derived calibration
to S07b/S07c. Keep suffix coordinates/frames out of tracking tuning, calibration,
model prompts and fitting; evaluate predictions once against the withheld suffix.
Changing the split after viewing errors invalidates that evaluation. This local
validator cannot enforce external storage custody or prevent a caller from
reading `held_out`; downstream integration must enforce it. It does not seal a
dataset or authenticate caller-supplied evidence strings.

S07d must propagate scale, time-ratio, per-frame timestamp/coordinate precision,
tracking error and covariance/systematic effects; this validator merely preserves
declared calibration requirements and rejects malformed numbers. Uncertainty in
g depends on scale and inverse-square capture-time ratio, so playback acceleration
is not g. Never set uncertainty to an invented value to unlock a fit; if unknown,
set the whole calibration object null. No uncertainty propagation is implemented
or claimed in S07a. Zero is allowed only when independently justified in evidence.

## Checks / limits

`python -m unittest discover -s tests/measurement -v`

Tests use explicit synthetic calibration/approval only; none authorizes real
clips. See `evidence/S07/S07a-input-audit.md`: literal three-candidate acceptance
is unmet, all real metric fits abstain, Gate M NOT RUN. S07b requires a separate
authorized run and controller acceptance of this still-PARTIAL prerequisite.
