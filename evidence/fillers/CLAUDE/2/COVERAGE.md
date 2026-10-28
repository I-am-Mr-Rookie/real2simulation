# F-CLAUDE-2 — CLAUDE viewer modules: test-coverage map + independent probes of F-CLAUDE-1

Base: main `489c1be` (viewer src/tests identical to F-CLAUDE-1's `8722a99`). Baseline `node --test` 5 viewer files (main checkout) → 42/42 pass, exit 0.
Probe script: [probes.mjs](probes.mjs) (`node evidence/fillers/CLAUDE/2/probes.mjs <main root>`; fake DOM/GL, real three core). Not gate evidence.
Labels: **REPRODUCED** = probe shows claimed defect; **REFUTED** = probe/contract contradicts claim (as stated); **UNVERIFIED** = not executed here.
Item text lives in [../1/CHECKLIST.md](../1/CHECKLIST.md); only verdicts/evidence below.

## 1. Existing test map (42 tests)

| File | Tests | Covers | Notable gaps (no test exists) |
|---|---|---|---|
| viewer.test.mjs | 11 | fixture identity, PLY decode happy path, manifest/asset mismatch + tamper, adapter lifecycle/abort/dispose, request validation, mystery UNAVAILABLE, error codes | PLY token grammar (hex/exp/float colour), float32 overflow, label/geometry validation, `synthetic:false` happy path (line 74 only tests mismatch rejection) |
| three-renderer.test.mjs | 11 | frameBounds, orbit clamps, mount/unmount leak counts, 100 abort cycles, start-failure cleanup, non +Y rejection, colliders/labels/path playback (analytic −Z projection, l.186), pause/resume, 375 px + desktop budgets | label w/o anchor, play-while-paused, empty IO entries, two mounts/host, stylesheet-positioned host, context loss, no-ResizeObserver, multi-touch, reduced-motion |
| artifact-loader.test.mjs | 7 | transport load, adapter+loader codes, splat decode/reject, unsafe manifests, size/length/sha caps, abort | credentials in bundle URL, non-numeric Content-Length message, non-GET init, mid-stream network error, mobile asset budget |
| scene-overlays.test.mjs | 5 | alignment + misalignment cases, collider edges, path lerp/slerp/clamp, ndcToScreen | points-vs-bounds_m, malformed collider shape |
| render-budget.test.mjs | 8 | tiers, boundaries, fallbacks, determinism, probeDevice, decimation | none material for F-CLAUDE-1 items |

## 2. F-CLAUDE-1 high-risk claims — verdicts

| F-CLAUDE-1 item | Verdict | Evidence (probes.mjs key → output) |
|---|---|---|
| P1 Invalid geometry → RENDER_FAILED | **REPRODUCED** | `geom_boundsMissingMax`, `geom_colliderNoHalfExtents`, `geom_coordinatesNoUp` → all `RENDER_FAILED: Renderer could not start` (expected INVALID_ARTIFACT) |
| P1 Label w/o `position_m` crashes every frame | **REPRODUCED** | `labelNoPosition` → mount succeeds, 3/3 frames throw TypeError |
| P1 Missing/null label text → "undefined" | **PARTLY REFUTED** | missing text → `"undefined"` (`labelTextMissing`) reproduced; `text:null` → `"null"`; a `null` label *entry* does not render "undefined": `buildSceneModel` throws TypeError → adapter `INVALID_ARTIFACT` (`labelNullEntryViaAdapter`) |
| P1 Points never checked vs `bounds_m` | **REPRODUCED** | `pointOutlierVsBounds`: point x=1e6 → `overlayAlignment` ok=true, 0 issues |
| P1 Camera-pose convention unverified | **REFUTED (viewer side)** | `contracts/scene/scene.schema.json:13` const `camera_forward:"-Z"`; README l.19–23 puts CV→viewer transform on upstream adapters; three-renderer.test l.186 asserts analytic −Z projection. Residual risk moves to S05 adapter tests, not viewer |
| P1 PLY float32 overflow / non-decimal tokens | already [V] in F-CLAUDE-1; not re-probed | — |
| P1 Phone path decodes full asset | **REPRODUCED (static)** | loader fetches only `render.asset_id`; `mobileAssetId` carried but unused (rg: no fetch use). Peak memory UNVERIFIED |
| P1 WebGL context loss unhandled | **REPRODUCED (static)** | rg `contextlost` → 0 hits in src/viewer |
| P2 Play pressed while paused "jumps ahead" | **REFUTED as stated; different defect REPRODUCED** | `playWhilePausedMeasured`: 1 s after resume camera is still at first key `[0,1,3]` vs unpaused `[0.25,1,3]`. `playStart += now-pausedAt` over-shifts by pause→play gap (4 s here): playback **stalls**, not skips |
| P2 Two mounts in one host | **REPRODUCED** | `twoMountsOneHost`: before `relative`, after disposing A `""` while B live |
| P2 Host position override | **REPRODUCED (inline only)** | `hostPositionOverride` inline `relative`; stylesheet-computed case UNVERIFIED (fake DOM has no getComputedStyle; rg 0 hits) |
| P2 Empty IntersectionObserver entries | **REPRODUCED** | `ioEmptyEntries` → throws TypeError |
| P2 No resize without ResizeObserver; multi-touch; wheel; reduced-motion; orientation; banner clip; point size | **UNVERIFIED** | need browser/device; wheel `preventDefault` is asserted *as intended* by three-renderer.test l.111 |
| P2 Reconstructed path untested | **REPRODUCED (coverage)** | only test with `synthetic=false` is mismatch rejection (viewer.test l.74) |
| P3 Credentials in bundleUrl | **REPRODUCED** | `loaderCredentialsUrl` → fetch called with `https://u:p@…/scene.json` |
| P3 Non-numeric Content-Length message | **REPRODUCED** | `INVALID_ARTIFACT: manifest exceeds size limit` |
| P3 `init.method/body` not restricted | **REPRODUCED** | `loaderInitMethodPost` → method `POST` sent |
| P3 Throwing onError replaces ViewerError | **REPRODUCED** | `throwingOnError` → plain `Error("cb boom")`, code null |
| P3 Mount without signal | **REPRODUCED** | `mountWithoutSignal` → TypeError |
| Other P3 (mid-stream error, mobile=main id, obj_info, zero splat scale, far clip) | **UNVERIFIED** | not probed (time box) |

## 3. Missing tests to add (owner S09h; each = 1 assertion on current failure above)

1. Adapter: bad `bounds_m` / collider / `coordinates.up` → `INVALID_ARTIFACT`.
2. Renderer: label without `position_m` → mount rejects or label hidden, no frame throws.
3. Model: label missing `text` → rejected/skipped (not "undefined").
4. Overlays: outlier point outside `bounds_m` → reported issue.
5. Renderer: play while paused → elapsed 0 at resume (assert pose advances 1 s after resume).
6. Renderer: `io.cb([])` no throw; mount A+B, dispose A → host position kept.
7. Loader: reject `user:pass@` URL; non-GET init; non-numeric Content-Length message.
8. Adapter: throwing `onError` still rejects with ViewerError; missing signal → documented error.
9. Model/viewer: `synthetic:false` + `evidence:'reconstructed'` happy path → no banner, `gateEvidence:false`.
10. Renderer: injected `webglcontextlost` → error state (needs implementation first).

