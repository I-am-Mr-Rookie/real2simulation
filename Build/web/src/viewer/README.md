# Viewer adapter v1 (S09a) + three.js points renderer (S09b) + artifact loader (S09c) + overlays (S09d) + render budget (S09e) + compact layout (S09g)

Implements the S04a viewer contract ([../shell/README.md](../shell/README.md) → Viewer adapter)
over frozen scene-v1 ([contracts/scene](../../../../contracts/scene/README.md)). Framework-free
ES modules; no package manifest (S04 owns deps; three 0.186.1 is in Build/web/package.json).
S09b adds the three.js points renderer + orbit camera. Node lifecycle tests plus one headless
Chromium WebGL2 (SwiftShader) smoke on the synthetic fixture. Not yet mounted by any app route.

| File | Role |
|---|---|
| adapter.mjs | createViewerAdapter({ createRenderer }).mount(host, request, services) → { dispose } |
| scene-model.mjs | ValidatedSceneBundle → frozen renderer-independent model; strict PLY xyz/rgb decode |
| fixture.mjs | SYNTHETIC_FIXTURE (S04a mount for synthetic-room-v1) + SYNTHETIC_BANNER |
| common.mjs | ViewerError, abortError, deepFreeze |
| three-renderer.mjs | createThreeRenderer({ THREE, createGLRenderer?, requestFrame?, cancelFrame?, ResizeObserverImpl? }) → createRenderer; frameBounds, createOrbit |
| three-viewer.mjs | Browser entry: createThreeViewer() = adapter + real three (imports 'three') |
| artifact-loader.mjs | createArtifactLoader({ bundleUrl, fetch?, limits?, init? }) → loadScene(sceneRef, signal); checkManifest |
| scene-overlays.mjs | Pure: colliderEdgePositions, overlayAlignment, prepareCameraPath/sampleCameraPath (slerp), ndcToScreen |
| render-budget.mjs | Pure: renderBudget(device) → frozen { tier, pixelRatio, maxPoints, antialias }; probeDevice(); decimatePoints |

## Compact layout and controls (S09g)

- Canvas CSS is display:block, width/height 100% of the host: the DPR-scaled drawing buffer no longer sets the CSS size
  (before S09g a 375 px phone at DPR 1.5 scrolled horizontally to 546 px). Banner wraps (overflow-wrap:anywhere).
- Host gets position:relative whenever it had none (labels and toolbar are absolute overlays); restored on dispose.
- Toolbar [data-viewer-controls] role=toolbar, bottom-right: Zoom in, Zoom out, Play camera path (only with a valid path);
  native buttons ≥ 44×44 CSS px, so touch users can zoom without wheel/keyboard. Drag still orbits.
- Layout per resize: host < 480 CSS px → compact (labels max-width 40%, ellipsis, 12 px), else full. handle.layout and
  data-viewer-layout on the toolbar expose it. Point budget stays S09e (decided per mount, not per resize).
- Not yet: pinch zoom, landscape/short-height tuning, real-phone check (headless Chromium device emulation only).

## Render budget (S09e)

- Decided once per mount from device facts (createThreeRenderer option device = () => probeDevice()); same facts → same frozen budget.
- reduced tier if viewport < 768 CSS px, deviceMemory < 4 GiB or < 4 cores (unknown/invalid facts ignored): DPR cap 1.5,
  ≤ 250 000 points, no antialias. Otherwise full: DPR cap 2, ≤ 2 000 000 points (loader limit), antialias. Invalid DPR → 1.
- probeDevice width = min(innerWidth, screen.width) so phone pages without a viewport meta (980 px layout) still count as phones.
- Points over the cap are decimated deterministically (every ceil(n/max)-th point). handle.budget and handle.pointCount expose the result.
  createGLRenderer(canvas, budget) receives the budget (antialias). Budget is not re-evaluated on resize/DPR change.
- Not yet: mobile_asset_id loading (still main asset only), real-device fps measurement, decimated point-size compensation.

## Overlays (S09d)

- Colliders: box edges as one THREE.LineSegments (colour 0x33ff88), from pose + unit quaternion (|q|−1 ≤ 1e-3).
- Labels: role-less div per label inside a [data-viewer-labels] layer, text via textContent only, positioned each draw from
  the projected 3D anchor (hidden when clipped/behind). Host gets position:relative only if it had none; restored on dispose.
- Camera path: keys validated once (strictly increasing time, finite, unit quats, 0<fov<180; invalid → playback disabled +
  alignment issue). setCameraTime(t) and playCameraPath() / 'p' key; lerp position/fov, shortest-arc slerp; frames only
  while playing, stops on the last key. Any orbit input returns to orbit (fov restored).
- handle.alignment = overlayAlignment(model): collider face vs surface plane gap, surface origin in footprint, bounds,
  points on face, labels in bounds. Report only (not rejected, not shown in UI); never measured/simulated or gate evidence.

## Artifact loader (S09c)

- loadScene for real bundles: GET <root>/scene.json, client-side manifest gate, then GET only the main
  render asset. bundleUrl(sceneRef) returns the transport-resolved root (http(s), ends with /, no query/hash).
- Fail-closed before parsing assets: schema 1.0.0 + id + synthetic↔evidence match; unique ids; path allowlist
  (same regex as scene.schema.json; resolved URL must stay under root); extension↔format; kind↔format for main
  and mobile; sha256 shape; 1 ≤ bytes ≤ limits.assetBytes; 1 ≤ point_count ≤ limits.points; splats bytes = 32×count.
- Transport: redirect 'error', caller signal, non-2xx → LOAD_FAILED; Content-Length precheck and streamed byte cap
  (manifest 256 KiB, asset = declared bytes, default asset limit 64 MiB, 2 M points); exact length + SHA-256.
  buildSceneModel re-checks length/SHA again (defence in depth).
- Codes: LOAD_FAILED (transport), INVALID_ARTIFACT (content), UNSUPPORTED (mesh/GLB). The adapter now passes
  these viewer-authored ViewerErrors through; any other loader error stays LOAD_FAILED with a viewer message.
- Splats: strict scene-v1 32-byte record decode (finite positions, finite ≥0 scales, |q|≈1 within 0.05 because of
  uint8 quantisation). Model keeps render.kind='points' (drawn as centre points) and render.sourceKind='splats',
  with render.splat { scales, opacity, rotations } for a later Gaussian rasteriser. No Gaussian splatting yet.
- Not covered: duplicate JSON keys (JSON.parse keeps last; the Python validator rejects them), full schema,
  provenance/licence authenticity (S02/S05 gates), mobile LOD fetch, GLB. Real S05 artifacts not yet available.

## Renderer (S09b)

- Points only (+Y up required, else RENDER_FAILED). THREE.Points with vertex colours; camera
  framed from bounds_m (bounding sphere fits the 50° vfov).
- Orbit: drag (one pointer, captured), wheel zoom (default prevented, clamped 0.2×–5×),
  keyboard arrows / + / - on the focusable canvas. Polar angle clamped away from the poles.
- Render on demand: one rAF per change; no idle loop.
- Synthetic banner rendered as a role=note div via textContent.
- dispose(): cancels pending frame, removes all listeners, disconnects ResizeObserver,
  disposes geometry + material + WebGLRenderer, forces context loss, removes canvas + banner.
  Partial construction failures free what was created.

## Contract details fixed here

- Bundle: { manifest: scene-v1 JSON already validated by contracts/scene, assets: { [assetId]: Uint8Array } }.
  The viewer re-checks once per mount: request/manifest id, version, synthetic↔evidence label,
  render asset byte length + SHA-256, PLY structure and point_count. Not per frame.
- Renderer injection: createRenderer(host, model, signal) → { dispose() } (sync or async).
  Renderer owns canvas, listeners, animation loop and GPU resources; dispose must free all of them.
- States: loading → ready; error (INVALID_REQUEST, LOAD_FAILED, INVALID_ARTIFACT, UNSUPPORTED,
  RENDER_FAILED); unavailable (UNAVAILABLE: mystery mode until S10 redacted payload exists).
  Error messages are viewer-authored; upstream/transport text is never forwarded.
- Abort (shell signal): rejects with DOMException AbortError, no callbacks, partial renderer disposed;
  after ready, abort disposes. dispose() is idempotent; no callbacks after dispose.
- Render kinds: points and splats (as centre points, S09c). mesh → UNSUPPORTED until a later S09 run validates it.
  Only the main render asset is decoded; mobile_asset_id is carried for S09 LOD work.
- Model: physicsEnabled=false, gateEvidence=false always; gravity/scale preserved as-is;
  labels are plain strings (render with textContent). Synthetic scenes carry SYNTHETIC_BANNER,
  which renderers must show. Typed arrays (positions/colors) are not freezable: treat as read-only.

## Synthetic fixture

SYNTHETIC_FIXTURE points at the one existing S05a bundle via
Build/web/src/shell/fixture-mounts.json (no geometry copy). Authored geometry only:
**not reconstruction, measured/simulated, physics or Gate R evidence.**

## Idle and hidden pause (S09f)

The three renderer draws on demand only (no idle loop). It also pauses while the tab is hidden
(document visibilitychange / document.hidden) or the host is out of the viewport (IntersectionObserver,
injectable as IntersectionObserverImpl). While paused no frame is scheduled, a pending frame is cancelled,
and camera-path playback time freezes. On resume a view changed while paused is redrawn once and
playback continues from where it paused. handle.paused exposes the state.

## Check

    node --test tests/viewer/viewer.test.mjs tests/viewer/three-renderer.test.mjs
    node --test tests/viewer/artifact-loader.test.mjs tests/viewer/scene-overlays.test.mjs
    node tests/viewer/browser-smoke.mjs   # needs Build/web/node_modules + Playwright-cached chrome-headless-shell (or CHROME_BIN)

## Needs (requests, not edits)

None for S09b (three 0.186.1 supplied by S04b). Real-GPU, mobile and memory-profiler checks
remain for later S09 runs; app route mounting is S04/S15 composition.

## Real scene bundles (S09h)

- Non-synthetic bundles get banner SCALE_UNVERIFIED_BANNER (fixture.mjs) unless scale.status === 'measured';
  banner element data-viewer-banner = 'synthetic' | 'scale-unverified'. Gate R FAIL -> S05f Fallback 2: no calibrated-scale claim.
- RM02/RM04/RM05 MapAnything bundles load through the unchanged loader/adapter: tests/viewer/real-scenes.test.mjs (skips without
  gitignored media in evidence/S09/local/), visual page tests/viewer/real-scenes.html. Evidence: evidence/S09/S09h-real-scenes.md.

## Simulated-trajectory replay (S09k)

- trajectory-replay.mjs: traceFromBody(bytes, sha256) verifies exact body bytes (<=262144) then checkTrace; checkTrace validates the
  S18k DTO (evidence/S18/S18k-TRACE-CONTRACT.md): exact fields, simulated/synthetic/SIMULATED labels, 2..4096 dense samples,
  time_s === step*dt_s, finite |xyz| <= 1e4 m. mountTrajectoryReplay(host, trace, { mode, signal }) renders an SVG side view (x right,
  +Y up) with SIMULATED banner, dashed reference axes labelled "not scene geometry", play/pause button + native range scrub.
- Mystery mode throws UNAVAILABLE before touching host/trace. Not a scene-v1 bundle; createThreeViewer is unchanged.
  Dispose (or signal abort) cancels the frame, removes listeners and DOM. Tests: tests/viewer/trajectory-replay.test.mjs.
