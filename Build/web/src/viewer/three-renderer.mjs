// S09b: three.js points renderer + orbit camera for the S09a adapter's createRenderer slot.
// THREE, the GL renderer factory, frame scheduler and ResizeObserver are injected so the
// lifecycle is testable without WebGL. Renders on demand (no idle loop). dispose() frees all.
// S09d: collider box edges (LineSegments), scene labels (textContent DOM overlay projected from 3D)
// and camera_path playback ('p' key or handle.playCameraPath/setCameraTime). Orbit input returns to orbit.
// S09e: per-mount device budget (render-budget.mjs) caps DPR, sets antialias and decimates points to the tier cap.
// S09f: hidden tab (Page Visibility) or offscreen host (IntersectionObserver) pauses: no frames are scheduled,
// a pending frame is cancelled, playback time freezes; on resume a dirty view is redrawn once.
// S09g: canvas CSS size follows the host (no DPR-scaled overflow); host < 480 CSS px -> compact layout
// (truncated labels); a toolbar of >= 44 px buttons (zoom in/out, play path) works without wheel or keyboard.
import { colliderEdgePositions, overlayAlignment, prepareCameraPath, sampleCameraPath, ndcToScreen } from './scene-overlays.mjs';
import { renderBudget, probeDevice, decimatePoints } from './render-budget.mjs';

const TAU = Math.PI * 2;
const COMPACT_MAX_PX = 480;
const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));

/** Bounds -> orbit target (centre) and a distance that frames the bounding sphere for vfov. */
export function frameBounds(boundsM, vfovDeg = 50) {
  const { min, max } = boundsM ?? {};
  if (![min, max].every((v) => Array.isArray(v) && v.length === 3 && v.every(Number.isFinite))) throw new Error('bounds invalid');
  const target = min.map((a, i) => (a + max[i]) / 2);
  const r = Math.max(1e-3, Math.hypot(...max.map((b, i) => b - min[i])) / 2);
  return { target, sphereRadius: r, distance: (r / Math.sin((vfovDeg * Math.PI) / 360)) * 1.1 };
}

/** Spherical orbit around target (+Y up). theta: azimuth about +Y, phi: polar angle from +Y. */
export function createOrbit({ target, distance, minDistance = distance * 0.2, maxDistance = distance * 5, theta = 0, phi = Math.PI / 3 }) {
  const s = { theta, phi: clamp(phi, 0.05, Math.PI - 0.05), distance: clamp(distance, minDistance, maxDistance) };
  return {
    rotate(dTheta, dPhi) {
      if (!Number.isFinite(dTheta) || !Number.isFinite(dPhi)) return;
      s.theta = (s.theta + dTheta) % TAU; s.phi = clamp(s.phi + dPhi, 0.05, Math.PI - 0.05);
    },
    zoom(factor) { if (Number.isFinite(factor) && factor > 0) s.distance = clamp(s.distance * factor, minDistance, maxDistance); },
    get state() { return { ...s }; },
    target: Object.freeze([...target]),
    position() {
      const sp = Math.sin(s.phi);
      return [target[0] + s.distance * sp * Math.sin(s.theta), target[1] + s.distance * Math.cos(s.phi), target[2] + s.distance * sp * Math.cos(s.theta)];
    },
  };
}

export function createThreeRenderer({
  THREE,
  createGLRenderer = (canvas, budget) => new THREE.WebGLRenderer({ canvas, antialias: budget.antialias }),
  requestFrame = (cb) => globalThis.requestAnimationFrame(cb),
  cancelFrame = (id) => globalThis.cancelAnimationFrame(id),
  ResizeObserverImpl = globalThis.ResizeObserver,
  IntersectionObserverImpl = globalThis.IntersectionObserver,
  device = () => probeDevice(),
  pointSizeM = 0.04,
  vfovDeg = 50,
  now = () => globalThis.performance.now(),
  colliderColor = 0x33ff88,
} = {}) {
  if (!THREE) throw new TypeError('THREE is required');
  return function createRenderer(host, model) {
    if (model?.render?.kind !== 'points') throw new Error('points only');
    if (model.coordinates?.up !== '+Y') throw new Error('only +Y-up scenes are supported');
    const doc = host.ownerDocument;
    const budget = renderBudget(device());
    const cleanups = [];
    const listen = (el, type, fn, opts) => { el.addEventListener(type, fn, opts); cleanups.push(() => el.removeEventListener(type, fn, opts)); };
    let gl, geometry, material, lineGeometry, lineMaterial, frame = null, disposed = false;
    const dispose = () => {
      if (disposed) return;
      disposed = true;
      if (frame !== null) { cancelFrame(frame); frame = null; }
      while (cleanups.length) { try { cleanups.pop()(); } catch { /* keep freeing */ } }
      geometry?.dispose(); material?.dispose(); lineGeometry?.dispose(); lineMaterial?.dispose();
      if (gl) { gl.dispose(); gl.forceContextLoss?.(); }
    };
    try {
      const canvas = doc.createElement('canvas');
      canvas.tabIndex = 0;
      canvas.setAttribute('aria-label', '3D point view. Drag or arrow keys to orbit; wheel or +/- to zoom.');
      Object.assign(canvas.style, { touchAction: 'none', display: 'block', width: '100%', height: '100%', maxWidth: '100%' });
      host.appendChild(canvas);
      cleanups.push(() => canvas.remove());
      const prevPos = host.style.position; // overlays (labels, toolbar) are absolutely positioned
      if (!prevPos) { host.style.position = 'relative'; cleanups.push(() => { host.style.position = prevPos ?? ''; }); }
      if (model.banner) {
        const b = doc.createElement('div');
        b.setAttribute('role', 'note');
        b.setAttribute('data-viewer-banner', 'synthetic');
        b.textContent = model.banner; // plain text only, never HTML
        b.style.overflowWrap = 'anywhere';
        host.appendChild(b);
        cleanups.push(() => b.remove());
      }

      // Labels: plain-text DOM overlay, positioned per draw from the projected 3D anchor.
      const labelEls = [];
      if (Array.isArray(model.labels) && model.labels.length) {
        const layer = doc.createElement('div');
        layer.setAttribute('data-viewer-labels', '');
        Object.assign(layer.style, { position: 'absolute', left: '0', top: '0', width: '100%', height: '100%', pointerEvents: 'none', overflow: 'hidden' });
        host.appendChild(layer);
        cleanups.push(() => layer.remove());
        for (const l of model.labels) {
          const el = doc.createElement('div');
          el.setAttribute('data-viewer-label', String(l.id));
          el.textContent = String(l.text); // plain text only, never HTML
          Object.assign(el.style, { position: 'absolute', left: '0', top: '0', whiteSpace: 'nowrap', display: 'none' });
          layer.appendChild(el);
          cleanups.push(() => el.remove());
          labelEls.push({ id: l.id, el, anchor: l.position_m, screen: null });
        }
      }

      const pts = decimatePoints(model.render.positions, model.render.colors, budget.maxPoints);
      geometry = new THREE.BufferGeometry();
      geometry.setAttribute('position', new THREE.BufferAttribute(pts.positions, 3));
      geometry.setAttribute('color', new THREE.BufferAttribute(pts.colors, 3, true));
      material = new THREE.PointsMaterial({ size: pointSizeM, vertexColors: true, sizeAttenuation: true });
      const scene = new THREE.Scene();
      scene.add(new THREE.Points(geometry, material));
      const edges = colliderEdgePositions(model.colliders);
      if (edges.length) {
        lineGeometry = new THREE.BufferGeometry();
        lineGeometry.setAttribute('position', new THREE.BufferAttribute(edges, 3));
        lineMaterial = new THREE.LineBasicMaterial({ color: colliderColor });
        scene.add(new THREE.LineSegments(lineGeometry, lineMaterial));
      }
      const alignment = overlayAlignment(model);
      let pathKeys = null;
      try { pathKeys = prepareCameraPath(model.cameraPath); } catch { alignment.issues.push('camera_path invalid; playback disabled'); alignment.ok = false; }
      let mode = 'orbit', pose = null, playStart = null, size = [1, 1];
      const f = frameBounds(model.boundsM, vfovDeg);
      const camera = new THREE.PerspectiveCamera(vfovDeg, 1, f.distance / 100, f.distance * 10);
      const orbit = createOrbit({ target: f.target, distance: f.distance });

      gl = createGLRenderer(canvas, budget);
      gl.setPixelRatio(budget.pixelRatio);
      const draw = () => {
        frame = null;
        if (disposed) return;
        if (playStart !== null) {
          pose = sampleCameraPath(pathKeys, pathKeys[0].t + (now() - playStart) / 1000);
          if (pose.t >= pathKeys[pathKeys.length - 1].t) playStart = null;
        }
        if (mode === 'path' && pose) {
          camera.position.set(...pose.position);
          camera.quaternion.set(...pose.quaternion);
          if (camera.fov !== pose.fov) { camera.fov = pose.fov; camera.updateProjectionMatrix(); }
        } else {
          if (camera.fov !== vfovDeg) { camera.fov = vfovDeg; camera.updateProjectionMatrix(); }
          camera.position.set(...orbit.position());
          camera.lookAt(...orbit.target);
        }
        camera.updateMatrixWorld();
        for (const L of labelEls) {
          L.screen = ndcToScreen(new THREE.Vector3(...L.anchor).project(camera).toArray(), size[0], size[1]);
          if (!L.screen) { L.el.style.display = 'none'; continue; }
          L.el.style.display = '';
          L.el.style.transform = 'translate(' + L.screen[0].toFixed(1) + 'px,' + L.screen[1].toFixed(1) + 'px) translate(-50%,-100%)';
        }
        gl.render(scene, camera);
        if (playStart !== null) invalidate(); // playback only: stops at the last key
      };
      let hidden = !!doc.hidden, offscreen = false, dirty = false, pausedAt = null;
      const invalidate = () => {
        if (disposed) return;
        if (pausedAt !== null) { dirty = true; return; }
        if (frame === null) frame = requestFrame(draw);
      };
      const updatePause = () => {
        const pause = hidden || offscreen;
        if (disposed || pause === (pausedAt !== null)) return;
        if (pause) {
          pausedAt = now();
          if (frame !== null) { cancelFrame(frame); frame = null; dirty = true; }
        } else {
          if (playStart !== null) playStart += now() - pausedAt;
          pausedAt = null;
          if (dirty) { dirty = false; invalidate(); }
        }
      };
      const toOrbit = () => { mode = 'orbit'; playStart = null; };
      const setCameraTime = (t) => { if (!pathKeys || disposed) return false; toOrbit(); mode = 'path'; pose = sampleCameraPath(pathKeys, t); invalidate(); return true; };
      const playCameraPath = () => { if (!pathKeys || disposed) return false; mode = 'path'; pose = sampleCameraPath(pathKeys, pathKeys[0].t); playStart = now(); invalidate(); return true; };
      const bar = doc.createElement('div');
      bar.setAttribute('role', 'toolbar');
      bar.setAttribute('aria-label', 'View controls');
      bar.setAttribute('data-viewer-controls', '');
      Object.assign(bar.style, { position: 'absolute', right: '8px', bottom: '8px', display: 'flex', gap: '8px' });
      host.appendChild(bar);
      cleanups.push(() => bar.remove());
      const button = (text, label, fn) => {
        const el = doc.createElement('button');
        el.type = 'button'; el.textContent = text; el.setAttribute('aria-label', label);
        Object.assign(el.style, { minWidth: '44px', minHeight: '44px', fontSize: '18px' });
        bar.appendChild(el);
        cleanups.push(() => el.remove());
        listen(el, 'click', fn);
      };
      button('+', 'Zoom in', () => { toOrbit(); orbit.zoom(0.9); invalidate(); });
      button('\u2212', 'Zoom out', () => { toOrbit(); orbit.zoom(1 / 0.9); invalidate(); });
      if (pathKeys) button('\u25B6', 'Play camera path', () => playCameraPath());
      let layout = null;
      const setLayout = (next) => {
        if (next === layout) return;
        layout = next; bar.setAttribute('data-viewer-layout', next);
        const c = next === 'compact';
        for (const L of labelEls) Object.assign(L.el.style, c ? { maxWidth: '40%', overflow: 'hidden', textOverflow: 'ellipsis', fontSize: '12px' } : { maxWidth: '', overflow: '', textOverflow: '', fontSize: '' });
      };
      const resize = () => {
        if (disposed) return;
        const w = Math.max(1, host.clientWidth | 0), h = Math.max(1, host.clientHeight | 0);
        gl.setSize(w, h, false); size = [w, h];
        setLayout(w < COMPACT_MAX_PX ? 'compact' : 'full');
        camera.aspect = w / h; camera.updateProjectionMatrix();
        invalidate();
      };

      let drag = null;
      listen(canvas, 'pointerdown', (e) => { toOrbit(); drag = { id: e.pointerId, x: e.clientX, y: e.clientY }; canvas.setPointerCapture?.(e.pointerId); });
      listen(canvas, 'pointermove', (e) => {
        if (!drag || e.pointerId !== drag.id) return;
        const k = TAU / Math.max(1, host.clientHeight | 0);
        orbit.rotate(-(e.clientX - drag.x) * k, -(e.clientY - drag.y) * k);
        drag.x = e.clientX; drag.y = e.clientY;
        invalidate();
      });
      const end = (e) => { if (drag && e.pointerId === drag.id) drag = null; };
      listen(canvas, 'pointerup', end);
      listen(canvas, 'pointercancel', end);
      listen(canvas, 'wheel', (e) => { e.preventDefault(); toOrbit(); orbit.zoom(Math.exp(clamp(e.deltaY, -200, 200) * 0.001)); invalidate(); }, { passive: false });
      listen(canvas, 'keydown', (e) => {
        const step = { ArrowLeft: [0.1, 0], ArrowRight: [-0.1, 0], ArrowUp: [0, -0.1], ArrowDown: [0, 0.1] }[e.key];
        if (e.key === 'p' || e.key === 'P') { if (!playCameraPath()) return; e.preventDefault(); return; }
        if (step) { toOrbit(); orbit.rotate(...step); }
        else if (e.key === '+' || e.key === '=') { toOrbit(); orbit.zoom(0.9); }
        else if (e.key === '-') { toOrbit(); orbit.zoom(1 / 0.9); }
        else return;
        e.preventDefault(); invalidate();
      });
      if (ResizeObserverImpl) {
        const ro = new ResizeObserverImpl(resize);
        ro.observe(host);
        cleanups.push(() => ro.disconnect());
      }
      if (typeof doc.addEventListener === 'function') listen(doc, 'visibilitychange', () => { hidden = !!doc.hidden; updatePause(); });
      if (IntersectionObserverImpl) {
        const io = new IntersectionObserverImpl((entries) => { offscreen = !entries[entries.length - 1].isIntersecting; updatePause(); });
        io.observe(host);
        cleanups.push(() => io.disconnect());
      }
      updatePause();
      resize();
      return {
        dispose, orbit, camera, invalidate, alignment, setCameraTime, playCameraPath, budget, pointCount: pts.count,
        get cameraMode() { return mode; },
        get playing() { return playStart !== null; },
        get pendingFrame() { return frame !== null; },
        get paused() { return pausedAt !== null; },
        get layout() { return layout; },
        labelScreen: () => labelEls.map((L) => ({ id: L.id, screen: L.screen && [...L.screen] })),
      };
    } catch (e) {
      dispose(); // partial construction must not leak
      throw e;
    }
  };
}
