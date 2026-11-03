# N80: crop fixes, negative SF3D acceptance result

**PARTIAL. Do not promote this candidate pack.** Crops are cleaner, but all four outputs are not convincingly recognisable furniture. The original shared N75 pack and both committed manifests remain unchanged. No deploy or push.

## Diagnosis and bounded changes

- Original crops were 464x130, 518x140, 279x195 and 194x211. Alpha came from depth/collision support, deleting parts of solid tops and thin legs. Original RGB views show papers causing enclosed SAM holes. Object 2 is also laptop-occluded and cut by the frame. Missing pixels/legs cannot be recovered honestly from that view.
- Keep collision geometry unchanged. Appearance uses the original SAM silhouette. Select an already-associated same-category view by `area / (1 + cut_edge_pixels / sqrt(area))`, not only 3D point count. A tiny complete silhouette cannot automatically beat a much larger slightly clipped view. Do not swap views for size-prior partitions or desk/hutch cross-category merges.
- Repair enclosed table/desk holes only with valid, horizontal, same-height, similar-colour source pixels. This is **MODEL-ESTIMATED mask repair**, not inpainting or calibrated segmentation. No RGB is invented. Open boundaries, chair openings, missing depth and partitions stay untouched. The 0.06 nominal-height band and 0.2 RGB-channel tolerance are heuristics, not measured uncertainties.
- Square 512 RGBA inputs use 85% foreground extent, aspect-preserving resampling, centred padding and zero RGB under transparent pixels. Upsampling adds no observed detail. The deployed SF3D wrapper already calls upstream `resize_foreground(..., 0.85)`, so non-square inputs alone were not the root cause.
- Carry the selected view's camera into mesh fitting in both synchronous and deferred paths. Fit normalisation itself is deliberately unchanged: the client independently stretches GLB axes to the proxy box, so a Python-only uniform-normalisation change would not preserve visual aspect and could misalign geometry. Renderer changes are outside Owns.

## Live public-only experiment

Used `evidence/N75/build_sample.py` with the approved RM02 archive SHA `82e6cc99142b9791ad30c18ac2c92106a30a0082b61d6063aace74d31c986154`, cached N52 public SAM replies, existing deployed `r2s-sf3d/generate`, `generate_remote`, `SerialBatch`, and the canonical daily ledger. No new SAM/MapAnything calls.

1. Four initial crops, objects 1/2/4/7. Poor output retained only as an ablation.
2. One changed object-1 crop after depth/material-supported enclosed-hole repair. Three byte-identical crop/fit results reused, no inference for them.
3. Three changed view selections, objects 2/4/7. Object 1 reused with byte-identical crop and proxy. No further calls.

**8 crop calls, 3 separately reserved conservative idle tails, $1.04994430 ledger estimate of the $3 cap. Not a provider bill.** UTC, reservation, settlement and per-job units are in `spend.json`. The first wrapper's postcheck read the wrong metadata field after all four successful calls; fixed the check and recovered existing outputs without retrying them.

## Visual acceptance

In-app browser, actual production `sf3d-shape.mjs`, same cameras and proxy dimensions, all eight GLBs loaded. Final angle/front/top comparisons are `compare-angle.jpg`, `compare-front.jpg`, `compare-top.jpg`. `local-lab.jpg` shows the final candidate in an isolated GET-only local production build, not DEV/auth E2E. No private owner room or N06 accessed.

| Object | Final visual assessment, subjective, not a recognition metric |
|---|---|
| 1 | Paper hole removed, but SF3D produces an upright slab, not a complete table. |
| 2 | Occluded/cut tabletop remains an irregular cluster. Not acceptable furniture. |
| 4 | Top remains dark and incomplete, legs sparse. No clear overall improvement. |
| 7 | Broader white top, but still largely a strip with incomplete support. Not a complete table. |

`audit.json` derives per-axis fit-scale max/min ratios 4.339, 18.694, 3.540 and 4.939 from the final GLB accessor bounds and existing proxy dimensions. These diagnose anisotropic deformation, not physical error or calibrated accuracy. A follow-up needs renderer-aware aspect-preserving visual fitting and/or better-observed inputs; absent legs and occluded surfaces must remain explicitly uncertain.

## Verification

- CPython 3.14: reconstruction + API-storage **127 passed, 6 subtests passed**.
- CPython 3.12 with production NumPy 2.2.6, Pillow 11.3.0, FastAPI 0.124.4, jsonschema 4.23.0, python-multipart 0.0.20: same **127 passed, 6 subtests passed**. Deprecation warnings only.
- `npm run build --prefix Build/web`: PASS. No frontend source change.
- Actual candidate hashes verified; 23 scene objects, same positions/sizes/rotations, exactly four mesh IDs. Original shared pack hashes unchanged. Actual candidate legacy repair, repeated seed and second-user seed passed with inference functions forbidden.
- Existing N75-shell to new-pack-hash migration was not implemented or tested because no pack was promoted. Current sample.py deliberately preserves existing/user-built shells; any future promotion must handle that guard without overwriting user edits.
- Browser comparison and final local lab: no captured console errors. All checks are local/public/simulated, not physical calibration, paid billing reconciliation, production deployment or signed-in E2E.
- Temporary browser tabs and verified own loopback helpers were closed. Named-file staged secret/path scan and diff checks passed. Remote idle-state snapshots are in idle-after.json; a runner count is not a provider billing measurement.
- At 00:26:16 UTC, the read-only Modal snapshot showed zero runners, running inputs and backlog. An earlier 00:22:27 snapshot had one idle runner, so scale-to-zero was not assumed merely from the configured timeout.

## Reproduction and safety

`diagnose.py <approved-public-bundle> <N52-public-sam-cache>` and `audit.py` are CPU-only. `serve_compare.py` serves only loopback allowlisted public assets and installed Three.js; `serve_local.py` is a loopback GET-only adapter to Next on 3080, using a synthetic owner. Both include no upload, agent or inference endpoint. Paid `build_paid.py` refuses an existing started build, prefixes canonical reservations with N80, and preserves the N75 manifests/receipt. `--reuse-dir` reuses only exact crop bytes and proxy metadata from this run's local evidence. Do not rerun paid work merely to reproduce screenshots.

Ignored local bundles retain all candidates and before-state binaries for review. No GLB/NPZ/video/cache is committed. No new project dependency, production configuration, provider, permission or secret was changed.
