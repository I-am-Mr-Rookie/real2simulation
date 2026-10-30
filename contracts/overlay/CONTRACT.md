# overlay/2.0.0 (S12d; v2 by S12e-fix2b, R-RS F1-R)

Ties each immutable predicted trace (S12c `Build.real2sim.predict.Prediction`) to one clip, its source
file sha and the source PTS frame timebase, so a renderer can draw prediction over actual frames.
Builder: `Build/real2sim/overlay.build`. Validator: [validate.py](validate.py) (stdlib only).

| Field | Rule |
|---|---|
| `contract_version` | `overlay/2.0.0` (`overlay/1.0.0` readable only with `legacy=True`, audit-only, never new evidence) |
| `clip_id`, `source_sha256` | must equal the clip/source the consumer is showing |
| `provenance` | `synthetic` or `image-derived` |
| `units` | `image-height fraction` (scale-free, Owner Q15=A) |
| `gate_m`, `limits` | `NOT_MET`; no calibrated or physical-accuracy claim |
| `timebase` | `{kind: pts_s, frame_map_sha256, sources}`; sha of sorted `[[frame_index, pts_s], ...]` of the source frame map (errata-corrected where one exists) |
| `traces[]` | `Prediction` JSON: `kind, clip_id, training_sha256, suffix_identity_sha256, model, trace, sha256, gate_m, source_sha256, suffix_count, commitment`; rows `[frame_index, pts_s, value, sigma or null]` |

`validate(doc, clip_id, source_sha256, frame_map, legacy=False)` rejects: unknown/missing fields, other version, gate_m
other than NOT_MET, other clip or source sha, a frame map whose hash differs, any row whose frame is absent
from the map or whose PTS differs by more than 1e-6 s, non-increasing frames, and any trace whose
`sha256` no longer matches the `prediction/v2` commitment over `[prediction/v2, kind, model, trace, clip_id,
source_sha256, training_sha256, suffix_identity_sha256, suffix_count]` (v1 legacy: `[kind, model, trace]`),
whose `suffix_identity_sha256` is not the hash of its complete `[[frame_index, pts_s], ...]` rows, or whose
`suffix_count` differs from its row count (R-RS F1/F1-R; the builder requires v2 bound to the boundary's
clip, source, training and seal). It returns a tuple of immutable `Trace` named tuples (with `commitment`);
renderers read those only and never recompute or edit predictions.

Values may lie outside [0, 1] (ballistic ST03 runs past the image bottom); renderers clip, not the contract.
Scoring against observations is S12e, not this contract.
