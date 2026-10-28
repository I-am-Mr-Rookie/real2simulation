# F-CLAUDE-1 — CLAUDE viewer modules: missing-case checklist

Scope: read-only analysis of the finished CLAUDE-owned viewer modules S09a–S09g at main `8722a99`
(`Build/web/src/viewer/*.mjs`, `tests/viewer/*`). No product edits. Line numbers refer to that SHA.
Baseline: `node --test` on the 5 viewer test files in the main checkout → 42/42 pass.
Labels: **[V]** = verified by probe in this run; **[R]** = found by code reading, not executed.
Priority: P1 = can break real-scene integration (S09h) or show wrong output; P2 = robustness/UX; P3 = minor.

## P1 — fix or test before S09h real scenes

- [ ] **PLY float32 overflow accepted** [V] — `scene-model.mjs:39-41` checks `Number.isFinite` on the double, then stores into `Float32Array`; `1e39` becomes `Infinity`. Need: reject |x| > 3.4028235e38 (or check finiteness after the float32 store). Probe: `decodePlyXyzRgb` row `1e39 …` → positions `["Infinity",…]`.
- [ ] **Non-decimal PLY tokens accepted** [V] — `Number()` accepts `0x10` (→16), and `1e2`/`255.0` as uchar colours (→100/255). Need: decimal-only token regex matching the Python scene-v1 writer; add case to `viewer.test.mjs`.
- [ ] **Render points never checked against `bounds_m`** [R] — `frameBounds` frames `bounds_m` only (`three-renderer.mjs:19-25,131`); `overlayAlignment` checks colliders/labels, not points. Real reconstructions with outliers or a wrong `bounds_m` render off-frame or get clipped by far = 10·distance. Need: count/report points outside bounds; test with an outlier.
- [ ] **Camera-pose convention unverified for real paths** [R] — path mode copies `rotation_xyzw` straight onto a three.js camera (`three-renderer.mjs:144-147`; looks down −Z, +Y up). S05 reconstruction poses (COLMAP/OpenCV: +Z forward, +Y down) would face backwards/upside down. Need: confirm scene-v1 camera convention in `contracts/scene`; test a known look-at pose.
- [ ] **Invalid manifest geometry misreported as RENDER_FAILED** [R] — loader/model do not validate `bounds_m`, `colliders`, `coordinates` (`artifact-loader.mjs:51-76`, `scene-model.mjs:104-113`); bad values throw inside `createRenderer` (`frameBounds`, `colliderEdgePositions`→`boxCorners`) and the adapter maps them to `RENDER_FAILED` (`adapter.mjs:65-66`), not `INVALID_ARTIFACT`. Need: validate in `buildSceneModel`; tests for bad bounds, bad collider, missing `coordinates.up`.
- [ ] **Label without `position_m` crashes every frame** [R] — `new THREE.Vector3(...L.anchor)` in `draw` (`three-renderer.mjs:155`) throws a TypeError inside the rAF callback when the anchor is undefined, and again on every later frame; `overlayAlignment` only records an issue. Need: drop/hide invalid labels at mount; test.
- [ ] **Missing label text renders literally "undefined"** [R] — `String(l.text)` / `String(l.id)` (`scene-model.mjs:113`, `three-renderer.mjs:104-105`); `null` label entries become text "undefined". Need: reject or skip non-string text/id; test.
- [ ] **Phone path decodes the full-detail asset before decimating** [R, structural bottleneck] — reduced tier caps at 250k points, but the loader always fetches the main asset (`artifact-loader.mjs:103`; mobile LOD unused) and `decodePlyXyzRgb` decodes the whole file to one string and `split`s it into lines (`scene-model.mjs:20-21`) for up to 2M points / 64 MiB before `decimatePoints`. Full splat `scales/opacity/rotations` stay in the frozen model though only centres are drawn. Need: fetch `mobile_asset_id` on the reduced tier (S09h/S09i), line-scan PLY without a giant split, measure peak memory on the 375 px budget.
- [ ] **WebGL context loss not handled** [R] — no `webglcontextlost/restored` listeners; a mobile GPU reset leaves a black canvas with no shell error state. Need: listener → `onError` or re-init; test with an injected event.

## P2 — robustness / UX

- [ ] **Host `position` override** [R] — `three-renderer.mjs:82-83` reads only inline `host.style.position`; a host positioned absolute/fixed/sticky by a stylesheet is forced to inline `relative`. Need: `getComputedStyle(host).position === 'static'` check.
- [ ] **Two mounts in one host** [R] — second mount sees the first's inline `relative` and pushes no cleanup; disposing the first resets `position` while the second is live. Test: mount A, mount B, dispose A.
- [ ] **Play pressed while paused jumps ahead** [R] — `playCameraPath` sets `playStart = now()` after an older `pausedAt`; resume adds `now() - pausedAt` (`three-renderer.mjs:176,183`), skipping the pause-to-play interval. Reachable via the handle API while offscreen. Need: shift by `now() - max(pausedAt, playStart)`; test.
- [ ] **No resize without ResizeObserver** [R] — without `ResizeObserverImpl`, size is set once (1×1 if the host is `display:none` at mount); no `window.resize` fallback.
- [ ] **Empty IntersectionObserver entries** [R] — `entries[entries.length - 1].isIntersecting` throws on `[]` (`three-renderer.mjs:247`).
- [ ] **Multi-touch** [R] — a second finger's `pointerdown` replaces `drag` (no pinch-zoom; view jumps). Toolbar zoom compensates; record as known limit or add pinch.
- [ ] **Wheel always `preventDefault`** [R] — page scroll trapped while the cursor is over the viewer.
- [ ] **No `prefers-reduced-motion`** [R] — camera-path playback ignores reduced motion.
- [ ] **Orientation change keeps mount-time tier** [R] — budget fixed per mount (by design); Android `screen.width` changes on rotation, iOS does not. Document expected behaviour for S09i.
- [ ] **Synthetic banner layout** [R] — banner is in normal flow after a 100%-height canvas (`three-renderer.mjs:84-92`); fixed-height or `overflow:hidden` hosts may clip it. Check in the 375 px browser smoke.
- [ ] **Fixed point size** [R] — `pointSizeM = 0.04` ignores scene scale and decimation stride; small scenes overdraw, decimated scenes look sparse. Manifest `scale` is copied but unused — confirm scene-v1 scale semantics.
- [ ] **Reconstructed (non-synthetic) path untested** [R] — all tests use `evidence: 'synthetic'`; add `reconstructed` + `synthetic:false` → no banner, `gateEvidence:false` still.

## P3 — minor / contract hygiene

- [ ] Adapter: a throwing `onState/onError` replaces the `ViewerError` with the callback error (`adapter.mjs:37-41`); mount without `signal` throws TypeError (document the contract or default it).
- [ ] Loader: `bundleUrl` with `user:pass@` credentials not rejected (`artifact-loader.mjs:90`); non-numeric Content-Length reports "exceeds size limit" (fail-closed, wrong message); a mid-stream non-abort network error escapes raw from `loadScene` (adapter maps it to `LOAD_FAILED`); `init.method/body` not restricted to GET.
- [ ] Loader: `mobile_asset_id === asset_id` allowed; mobile asset bytes/point budget unchecked (matters once mobile LOD loads).
- [ ] PLY: `obj_info` lines and comments after `element` rejected — confirm the Python writer never emits them.
- [ ] Splats: zero scale and zero opacity accepted (valid but invisible); confirm intended.
- [ ] Renderer: camera-path poses beyond far = 10·distance clip the scene.

## Process note

- In a fresh `.worktrees/<ID>` checkout, `tests/viewer/three-renderer.test.mjs` fails with ERR_MODULE_NOT_FOUND for `Build/web/node_modules/three` (gitignored, not installed). The main checkout has it and reproduces S09g's 42/42. Future viewer runs need `npm ci` in the worktree (CODEX-2 owns `Build/web/package.json`) or must run viewer tests from main.

Recommended owner: P1 items → S09h (CLAUDE) before real-scene integration; camera convention and scale semantics need confirmation against `contracts/scene` (S05 owner). Nothing here is gate evidence.
