# SAM 3.1 local training adapter (S07b)

**Implemented boundary, not verified live inference.** No weights, media decoder,
Torch, CUDA or SAM package was run in S07b. Transport tests are synthetic. Gate M
NOT RUN; S12 stays locked. Nothing here grants metric or remote-upload approval.

## Interface and custody

- `load_local_predictor(checkpoint_path, execute=False)` lazily imports the
  official `build_sam3_multiplex_video_predictor`. Requires explicit `execute=True`
  and an existing local nonsymlink checkpoint. Before importing SAM it checks
  exact byte size and streaming SHA256 against `facebook/sam3.1` revision
  `daa63191845a41281374e725f4c9e51c7a824460` (`sam3.1_multiplex.pt`,
  3502755717 bytes, SHA256
  `0567debeec80ba4ac6369540c6c248025283cb3ff2b92827509e57e2b3541cb6`).
  Wrong/truncated/other-version bytes fail closed; no default download/fallback.
  Identity source: `evidence/S07/S07b/recovery4/IDENTITY.md`. Hashing reads the
  whole file with bounded memory and counts toward the caller's runtime budget.
  Custodian must prevent mutation through verification AND model construction;
  this local loader does not lock the file or attest the installed SAM revision.
  This is a heavy CUDA boundary, not a CPU-compatible implementation promise.
- `track_training(predictor, prefix_dir, metadata, frame_map, *, prompt,
  object_id, execute=False)` requires explicit opt-in. Calls official
  `handle_request(start_session/add_prompt/close_session)` and
  `handle_stream_request(propagate_in_video)`. Always attempts session closure
  after receiving a valid session ID, including prompt/stream/parser failures.
- `sanitize_responses(responses, metadata, frame_map, *, object_id)` is the actual
  response parser, also usable without model execution. NumPy imports only here.
  It consumes original-resolution boolean `out_binary_masks` and integer
  `out_obj_ids`, NOT normalized boxes, arbitrary logits or invented detections.
- `metadata` is the frozen S07a record **without** `frames`/`held_out`. Preserve
  source hash, provenance/licence, approval receipt, scale/timebase (null if
  unknown), continuity evidence and `last_training_frame`. Evidence strings
  are declarations; the adapter is not a rights/calibration approval authority.
- `frame_map` is an ordered tuple of `(original_frame_index, original_pts_s)`
  entries for the training prefix ONLY. Local predictor index 0 maps to entry 0,
  not necessarily original frame 0. Entries must strictly increase in index and
  PTS, be finite/nonnegative and end exactly at the frozen training boundary.
  No sorting, interpolation, index/FPS clock inference or capture-time conversion.

**Do not pass a full video and rely on propagation limits.** Session initialization
loads its resource. The adapter therefore accepts only a separate directory with
exactly `00000.jpg` through the mapped final local JPEG, no extra files or symlinks.
URLs and UNC paths are rejected before filesystem probes. The custodian must
prepare this training-only resource independently, verify source-byte hash,
dimensions, unmodified geometry, JPEG/source index/PTS correspondence and custody,
and prevent concurrent file mutation. Filename/count checks do **not** prove the
contents belong to the prefix. This run creates no real prefix or media exports.

Only training data reaches the predictor; suffix images/coordinates must remain
under independent custody. Prompt/object ID selection, tuning and calibration
must not consult that suffix. The adapter uses forward propagation from local
zero over the whole prefix session WITHOUT `max_frame_num_to_track` (the session
contains only the prefix). Upstream f1647e8 multiplex detector prefetch treats
`start + max` as an exclusive end, so `max = len - 1` gave the last frame an empty
backbone batch (`expand ... [5184, 0, 256]`, S07b-orch13; root-caused in orch14).
Propagated responses, not provisional prompt previews, are canonical.

## Result and failure semantics

`TrainingTrack` is frozen and contains immutable S07a `Frame`s, missing source
indices, a metadata JSON snapshot and explicit object ID. `training_record()`
returns a fresh JSON-compatible **prefix-only** record plus adapter/method
provenance. It is not itself a complete valid S07a evaluation record.

One declared object ID is selected; there is no first/largest/highest-score
heuristic or automatic identity switch. Other IDs may coexist. Missing object,
empty mask or omitted frame => missing, never zero coordinates or interpolation.
Duplicate IDs/frames, out-of-order or out-of-prefix frames, wrong mask dimensions,
nonboolean/nonfinite masks, malformed IDs/output or invalid mapping => `ValueError`.
Provider/import/runtime failures propagate; they are not converted into success.

The point is the foreground **pixel-index centroid** (x right, y down), not a
measured centre of mass, 3D point or metric position. Vectorized axis counts avoid
allocating per-foreground-pixel coordinate lists. Shape checks forbid implicit
resize/crop conversion. Segmentation bias, occlusion, JPEG artefacts and identity
quality still need actual validation and measurement uncertainty treatment.

A separate custodian can append its untouched evaluation suffix to the returned
prefix and call `inputs.validate_input`; tests exercise that real integration.
Fewer than three observations, missing final training observation or absent suffix
will fail S07a. Scientific blockers remain authoritative; neither successful
parsing nor a declared calibration establishes metric eligibility/verification.

## Source/runtime assumptions checked 2026-10-28

Upstream revision observed: `f1647e8d0c1d280991f4d1b7d974c2704537fe66`.

- [Official release](https://github.com/facebookresearch/sam3/blob/f1647e8d0c1d280991f4d1b7d974c2704537fe66/RELEASE_SAM3p1.md):
  SAM 3.1 multiplex uses the new checkpoints, not an alias for an older model.
- [Official builder](https://github.com/facebookresearch/sam3/blob/f1647e8d0c1d280991f4d1b7d974c2704537fe66/sam3/model_builder.py):
  exact entry point and local checkpoint option; defaults may download if omitted;
  model ends on CUDA. Adapter supplies a checkpoint and disables compile/warm-up
  and asynchronous frame loading. No provider/API protocol is guessed.
- [Shared predictor](https://github.com/facebookresearch/sam3/blob/f1647e8d0c1d280991f4d1b7d974c2704537fe66/sam3/model/sam3_base_predictor.py)
  and [video output implementation](https://github.com/facebookresearch/sam3/blob/f1647e8d0c1d280991f4d1b7d974c2704537fe66/sam3/model/sam3_video_inference.py):
  request names, keys, session lifetime, forward bounds, NumPy IDs/masks and source
  dimensions checked. These are version-sensitive, not live-runtime proof.
- [Official installation README](https://github.com/facebookresearch/sam3/blob/f1647e8d0c1d280991f4d1b7d974c2704537fe66/README.md):
  Python >=3.12, PyTorch >=2.7 and CUDA >=12.6 prerequisites; checkpoint access is
  gated. This host has Python 3.14.5/NumPy, but no Torch/SAM installed. Compatibility
  with a supported actual CUDA environment remains untested.
- [Official SAM licence](https://github.com/facebookresearch/sam3/blob/f1647e8d0c1d280991f4d1b7d974c2704537fe66/LICENSE)
  is a custom SAM agreement, not an assumed MIT/Apache grant. No weights copied,
  terms accepted or model redistribution authorized. Direct SAM3.1 model-card read
  returned restricted-access denial; no authentication or bypass attempted.

Next: controller reviews/merges this isolated implementation; independently
resolve approved runtime/checkpoint/licence and prefix custody before any later
authorized live run. Record exact checkpoint hash/config/software and actual
execution evidence externally; this adapter cannot attest model identity/accuracy.

Checks: `python -m unittest discover -s tests/measurement -v`.

## Runtime attempt S07b-orch13 (2026-10-29)

Modal A10 run: preflight PASS (exact lock), gated checkpoint SHA/size verified, predictor loaded, session+text prompt OK; propagation failed (0-batch expand). Driver needs use_fa3=False, an offload_state_to_cpu shim and extra imports (setuptools<81, einops, pycocotools). See evidence/S07/S07b/orch13/README.md. No track output yet.

