# N81: uniform SF3D visuals, unchanged physics

## Scope and implementation
- Production change: `Build/web/src/lab-editor/sf3d-shape.mjs` only. No Python fitter, scene schema, collider, shared pack, deployment or API changes.
- Callers inspected: `LabEditor.jsx` creates the proxy-scaled body and rebuilds it after scene edits; `physics.mjs` independently uses saved colliders; `scene.mjs` retains legacy fields. No caller migration is needed.
- Rotate the loaded GLB by the existing quarter turns, compute its bounds, then use `min(proxy.x / extent.x, proxy.y / extent.y, proxy.z / extent.z)` once. Zero-extent axes do not constrain the fit.
- The fit group divides that scale by each proxy dimension to cancel the parent's anisotropic scale. Net visual scaling is uniform in room units. Centre X/Z and align its lowest vertex with the proxy bottom.
- Visual support-plane remapping is removed, but its saved metadata and legacy physics paths remain untouched. Invalid/empty GLBs retain the visible collider placeholder instead of causing an uncaught fit error.

## Automated checks
- `node --test tests/lab-editor/*.test.mjs`: **46 passed**, zero failures. Six new tests cover non-cubic bounds, all four yaw rotations, uniform effective scale, containment, bottom/centre alignment, flat geometry, invalid bounds/dimensions, and invalid loaded-GLB fallback.
- Existing tests additionally cover old saved-scene JSON round trips, measured box collider identity, editor edits, legacy support-plane/trimesh physics and movable hull collisions.
- `python -m pytest tests/reconstruction/test_object_lift.py tests/reconstruction/test_shape_upgrade.py -q`: **28 passed**; one installed anyio/pytest deprecation warning.
- `npm run build --prefix Build/web`: **PASS**, including production compilation, TypeScript and route generation. Rebuilt after the final fallback change, restarted Next and rechecked both AFTER labs.
- `git diff --check`: PASS. `asset-audit.json` records fresh SHA-256 checks against both existing manifests and HTTP 200 for all four GLBs in all four lab fixtures. Neither pack was modified.

## In-app browser evidence
- Actual local `/lab` UI: original N75 public RM02 pack and the available N80 candidate pack, each with BEFORE and UNIFORM builds. Clicked Fit view to the room in each, saw 23 objects and the existing MODEL-ESTIMATED / scale-unverified warning, then saved `n75-lab-before.jpg`, `n75-lab-after.jpg`, `n80-lab-before.jpg`, `n80-lab-after.jpg`.
- These are isolated synthetic-owner GET-only adapters using the actual sample seeder and storage/room APIs. BEFORE uses a local snapshot of the already-built N80 Next app; AFTER uses this run's rebuilt production app. No upload, agent turn, private room, external inference, authentication bypass in production or write request was used.
- `compare.html` uses the actual old loader from base `4eaf48583c2eeca2811309ca4a11cb7dd9f12759` and current loader, with identical asset bytes, cameras and lighting. All 16 textured views loaded; angle/front/top screenshots show the same unchanged proxy wire boxes. This isolates transform effects from model quality.
- `browser-console.json`: no captured lab errors or gallery errors/warnings. The pre-existing `PCFSoftShadowMap` deprecation warning appears in both old and new actual labs; it falls back to PCFShadowMap.
- Browser tabs closed and local listeners 3081, 3083, 8083 through 8087 stopped and verified closed after the checks.

## Visual judgment and limits
- **N80 is not clearly better overall after removing stretch.** Object 1 has a more filled tabletop/slab than N75's partial ring; object 7 has a fuller white top. Object 2 is still fragmented, and object 4 remains incomplete/dark. This is a qualitative inspection, not a recognition score or a calibrated physical result.
- The old renderer amplified thin or partial meshes into tall blobs. Uniform fitting fixes that distortion, not missing geometry. Thin fragments now honestly remain thin and can sit near the proxy bottom; the unchanged physics surface can therefore lie above the visible fragment.
- Do not promote the N80 pack on this evidence. Scale and generated geometry remain unverified. No new inference/GPU jobs, paid calls, private-owner assets, deploy or push. Authentication/deployment E2E and calibrated contact alignment were not tested.

## Reproduction helpers
- `serve_lab.py <bundle> <manifest> <port> <next-port>` binds loopback only and supports GET only. It writes ignored synthetic fixture data under this evidence directory; it does not use real accounts.
- `python evidence/N81/serve_compare.py` serves the allowlisted public assets and installed Three.js at `http://localhost:8087`; startup asserts manifest hashes and rejects traversal / `.env` access. N80 candidate assets must still be available at the documented local path in the helper. No model binaries or build caches are committed here.
