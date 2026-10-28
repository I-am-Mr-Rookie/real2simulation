# S02d plan

Objective: audit each accepted clip manifest row against actual local video metadata and existing source/scale evidence; preserve uncertainty and abstention.

Owns: `clips.csv`, `evidence/clips/`, `test-data/public/`, and `Run-System/Runs/S02d/`. This run will write only the S02d audit/report and, if warranted, narrowly update manifest metadata. Canonical controls/merge are serialized by the controller.

Checks: compare fresh ffprobe container/video metadata with every present manifest file; record missing files explicitly, source-backed scale references versus unknown and scene-only treatment, and capture/slow-motion uncertainty; preserve AP15 NOT_TRACKABLE and ST05 HOLD. No acquisition, calibration invention, GPU, upload or approval substitution.

## Recovery continuation — 2026-10-28

Objective: resolve only FF03/FF04/RM01/RM03 metadata gaps using retained rejected files and their hashes first, then bounded known-source metadata. Owns unchanged. Preserve rejected disposition, all restrictions and prior report; no broad acquisition, dropped rows or substituted source labels for actual file measurements. Twenty-minute limit; sole worker holds serialized control windows. Verify the manifest and acquisition checks fresh; otherwise retain PARTIAL.

## Q6-A continuation — 2026-10-28 02:38 UTC

Objective: measure actual RM01/RM03 file FPS/duration via smallest normally provided Pexels rendition (Q2 bounded provisional download), hash + ffprobe, outside repo. Owns unchanged. Then fresh s02a/s02b/acquisition checks, explicit 23-row metadata inventory, verified FF merge only if all green. 20m ceiling; sole worker.
