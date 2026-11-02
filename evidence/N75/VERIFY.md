# N75: once-computed public classroom SAMPLE

## Result

- Reused the N49 public RM02 archive (SHA-256 `82e6cc99142b9791ad30c18ac2c92106a30a0082b61d6063aace74d31c986154`) and N52 public SAM cache, through the existing N53/N59 `build_shell_files` + deferred SF3D pipeline. No new segmentation/reconstruction call.
- 23 scene objects: floor/extent-wall/window pieces and 9 furniture objects. Four actual SF3D GLBs completed; other furniture keeps its parametric proxy. The four walls are scan-edge EXTENT estimates, not observed planes. Geometry MODEL-ESTIMATED, scale unverified, shape MODEL-GENERATED.
- Four canonical `daily_cap` reservations settled, USD **1.36696416** total conservative GPU wall-time/idle estimates, not a provider bill. Per-row ceiling USD 3 including outstanding reservations. `spend.json` records IDs, UTC, model, units and costs. Actual GPU reported NVIDIA A10 / A10G; first model load 84.951 s, later loads 0 s.

## Shipping and repair

- The existing `Build/pipeline/recorded/RM04-S13l-mapanything.json` retains the legacy RM04 display bundle and adds a `sample_shell` section with flat, hash-checked RM02 assets. No staging code change needed: `infra/railway/dev/stage.py api ...` already includes every listed asset.
- Eight new public files are retained in canonical ignored `evidence/S13l/reconstruct/bundle/`, plus the run's ignored `evidence/N75/bundle.local/`. All 12 combined manifest entries were verified by size/SHA-256. **No GLB/NPZ/PLY/image binary is committed.** Local files are required for the controller's future API stage; Git alone does not carry the pack.
- New users copy the pack without inference. Existing cloud-only samples backfill on files/projects list or the pre-N58 archive/result repair path, even when an old archive already exists. Older experiment-only seeds can gain their missing sample room. Mesh URLs are rebound to each user's room ID; asset endpoints retain owner checks.
- A marker prevents later list/result reads from overwriting edits or restoring deleted scene objects. Missing binary assets can be repaired. User-added basic objects and scene settings are preserved; previous room/scene JSON is retained in the sample directory for recovery from the RM04-to-RM02 frame migration.
- Deliberately do not replace an explicitly user-built shell, clicked real-object/wall IDs, or a custom scene that would exceed the existing 50-object limit. This protects user assets/edits instead of silently overwriting meshes or making a scene unloadable. Deleted sample projects are not resurrected. No private owner room or N06 data was opened or changed.

## Verification

- `pytest tests/api-storage tests/reconstruction -q`: **122 passed**, 6 subtests; existing Pillow/Starlette deprecation warnings. After moving validation ahead of binary reads for full custom scenes, the two affected corruption/full-scene tests also passed.
- `node --test tests/api-storage/proxy_files.test.mjs`: **3 passed**.
- Fresh local `npm run build`: PASS (17.5 s compilation). No web source changed.
- `check_real_bundle.py <canonical-bundle>`: actual old RM04 archive/empty SAMPLE migrates to 23 RM02 objects and 4 hash-matching meshes, remains idempotent, and seeds a second isolated user with zero inference calls (`real-bundle-check.json`).
- In-app browser, actual local production build through the GET-only loopback fixture adapter: sample opens with 23 objects, floor/walls/windows/green chairs and four textured meshes; all GLB GETs, PLY and view PNG return 200; Room panel displays SAMPLE / RECORDED; expanded honesty shows **one** Stability credit; Play runs, Reset returns Ready/t=0; no console errors observed (`ui-summary.json`).
- This fixture adapter uses real seed/storage/room routes but synthetic authentication. It blocks all browser writes/paid operations. It is **not** deployed Clerk/BFF end-to-end evidence. No DEV/judging deployment or push performed.

## Remaining caveats

The cloud-only showcase gap is addressed, but SF3D surfaces are visibly fragmented/coarse and are not photorealistic or physically calibrated. Extent walls/openings are inferred; scale uncertainty is unknown. Existing custom semantic samples are preserved rather than forced to this template. Future DEV behavior still requires controller merge/stage/deploy approval flow and recheck.

Local-only screenshots: `C:/Users/HP/.codex/visualizations/2026/11/02/01a19dda-5200-73a2-8e88-b2ec3eaae909/N75/` (`sample-shell-and-sf3d.jpg`, `sample-room-provenance.jpg`, `sample-reset.jpg`).

## Reproduction

- Offline public bundle check: `python evidence/N75/check_real_bundle.py <canonical-bundle>` with the existing API dependencies.
- UI: run the local Next build on 127.0.0.1:3075; run `python evidence/N75/serve_local.py <canonical-bundle>`; open the printed loopback URL in the in-app browser. Never deploy the fixture adapter.
- Paid builder is provenance only, **do not rerun**: `build_sample.py SOURCE_JOB N52_SAM_CACHE CANONICAL_LEDGER --paid-once` rejects a non-RM02 input and an existing output directory. The completed pack is already available; users never call this script.
