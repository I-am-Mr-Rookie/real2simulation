// S09b renderer tests: real three.js core objects, fake GL context + minimal DOM so every
// resource (listeners, frames, GPU objects, DOM nodes, observers) is counted. No WebGL here;
// the real-GPU check is tests/viewer/browser-smoke.mjs.
import test from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { ROOT, loadFixtureBundle } from './fixture-bundle.mjs';
import { createViewerAdapter } from '../../Build/web/src/viewer/adapter.mjs';
import { createThreeRenderer, createOrbit, frameBounds } from '../../Build/web/src/viewer/three-renderer.mjs';
import { SYNTHETIC_FIXTURE, SYNTHETIC_BANNER } from '../../Build/web/src/viewer/fixture.mjs';

const THREE = await import(pathToFileURL(path.join(ROOT, 'Build/web/node_modules/three/build/three.module.js')).href);

function fakeEnv() {
  const live = { listeners: 0, nodes: 0, frames: new Map(), observers: 0, gl: 0, ctxLost: 0, renders: 0, gpu: 0, pixelRatio: null, glOpts: null };
  let nextFrame = 1;
  class El {
    constructor(doc, tag) { this.ownerDocument = doc; this.tag = tag; this.children = []; this.parent = null; this.l = new Map(); this.attrs = {}; this.style = {}; this.textContent = ''; this.clientWidth = 640; this.clientHeight = 480; }
    setAttribute(k, v) { this.attrs[k] = String(v); }
    appendChild(c) { c.parent = this; this.children.push(c); live.nodes++; return c; }
    remove() { if (this.parent) { this.parent.children.splice(this.parent.children.indexOf(this), 1); this.parent = null; live.nodes--; } }
    addEventListener(t, fn) { const s = this.l.get(t) ?? new Set(); if (!s.has(fn)) live.listeners++; s.add(fn); this.l.set(t, s); }
    removeEventListener(t, fn) { if (this.l.get(t)?.delete(fn)) live.listeners--; }
    fire(t, ev = {}) { let prevented = false; for (const fn of [...(this.l.get(t) ?? [])]) fn({ preventDefault() { prevented = true; }, ...ev }); return prevented; }
  }
  // S09f: the document is an event target with a mutable 'hidden' flag (Page Visibility API).
  const doc = Object.assign(new El(null, '#document'), { hidden: false, createElement: (tag) => new El(doc, tag) });
  const host = new El(doc, 'div');
  const io = { last: null };
  const deps = {
    THREE,
    createGLRenderer: (canvas, budget) => { live.gl++; live.glOpts = budget; return { setPixelRatio(r) { live.pixelRatio = r; }, setSize() {}, render() { live.renders++; }, dispose() { live.gl--; }, forceContextLoss() { live.ctxLost++; } }; },
    requestFrame: (cb) => { const id = nextFrame++; live.frames.set(id, cb); return id; },
    cancelFrame: (id) => { live.frames.delete(id); },
    ResizeObserverImpl: class { constructor(cb) { this.cb = cb; io.ro = this; } observe() { live.observers++; } disconnect() { live.observers--; } },
    IntersectionObserverImpl: class { constructor(cb) { this.cb = cb; io.last = this; } observe(el) { this.el = el; live.observers++; } disconnect() { live.observers--; } },
    device: () => ({ devicePixelRatio: 1, viewportWidthPx: 1440 }),
  };
  const flush = () => { const f = [...live.frames.values()]; live.frames.clear(); f.forEach((cb) => cb()); };
  return { live, host, deps, flush, doc, io };
}

// Track GPU-side three objects: every created geometry/material must emit 'dispose'.
function trackGpu(live) {
  const seen = new WeakSet();
  const watch = (o) => { if (seen.has(o)) return; seen.add(o); live.gpu++; o.addEventListener('dispose', () => { live.gpu--; }); };
  const G = THREE.BufferGeometry.prototype, M = THREE.Material.prototype;
  const { setAttribute } = G, { setValues } = M;
  G.setAttribute = function (...a) { watch(this); return setAttribute.apply(this, a); };
  M.setValues = function (...a) { if (this.isPointsMaterial || this.isLineBasicMaterial) watch(this); return setValues.apply(this, a); };
  return () => { G.setAttribute = setAttribute; M.setValues = setValues; };
}

const services = (bundle, signal, states, errors) => ({ loadScene: async () => bundle, signal, onState: (s) => states.push(s), onError: (e) => errors.push(e) });

test('frameBounds centres target and frames the bounding sphere', () => {
  const f = frameBounds({ min: [-1, -0.05, -1], max: [1, 0.75, 1] }, 50);
  assert.deepEqual(f.target.map((v) => +v.toFixed(6)), [0, 0.35, 0]);
  assert.ok(f.distance * Math.sin((25 * Math.PI) / 180) > f.sphereRadius, 'sphere fits in vfov');
  assert.throws(() => frameBounds({ min: [0, 0], max: [1, 1, 1] }));
});

test('orbit rotates at constant distance, clamps poles and zoom, ignores non-finite input', () => {
  const o = createOrbit({ target: [0, 1, 0], distance: 4 });
  const dist = () => Math.hypot(...o.position().map((v, i) => v - o.target[i]));
  const p0 = o.position();
  o.rotate(0.7, 0.2);
  assert.notDeepEqual(o.position(), p0);
  assert.ok(Math.abs(dist() - 4) < 1e-9);
  o.rotate(0, 100); assert.ok(o.state.phi <= Math.PI - 0.05 + 1e-12);
  o.rotate(0, -100); assert.ok(o.state.phi >= 0.05 - 1e-12);
  o.zoom(1e9); assert.equal(o.state.distance, 20);
  o.zoom(1e-9); assert.ok(Math.abs(o.state.distance - 0.8) < 1e-12);
  const s = o.state; o.rotate(NaN, 1); o.zoom(-1); o.zoom(Infinity); assert.deepEqual(o.state, s);
});

test('fixture mounts through the adapter, renders points with banner, orbits and unmounts with zero live resources', async () => {
  const { live, host, deps, flush } = fakeEnv();
  const untrack = trackGpu(live);
  try {
    const bundle = await loadFixtureBundle();
    const states = [], errors = [];
    const ac = new AbortController();
    let handle;
    const adapter = createViewerAdapter({ createRenderer: (h, m, s) => (handle = createThreeRenderer(deps)(h, m, s)) });
    const viewer = await adapter.mount(host, SYNTHETIC_FIXTURE.request, services(bundle, ac.signal, states, errors));
    assert.deepEqual(states, ['loading', 'ready']); assert.deepEqual(errors, []);
    const [canvas, banner, labels] = host.children;
    assert.equal(canvas.tag, 'canvas');
    assert.equal(banner.textContent, SYNTHETIC_BANNER);
    assert.equal(labels.attrs['data-viewer-labels'], '');
    // S09d: points geometry+material and collider-edge geometry+material
    // S09f: + IntersectionObserver and the document visibilitychange listener
    // S09g: + 3 control-button click listeners
    assert.equal(live.gl, 1); assert.equal(live.gpu, 4); assert.equal(live.observers, 2);
    assert.equal(live.listeners, 10);
    flush(); assert.equal(live.renders, 1);
    assert.equal(handle.pendingFrame, false, 'no idle render loop');

    const before = handle.camera.position.toArray();
    canvas.fire('pointerdown', { pointerId: 1, clientX: 100, clientY: 100 });
    canvas.fire('pointermove', { pointerId: 1, clientX: 160, clientY: 90 });
    canvas.fire('pointermove', { pointerId: 2, clientX: 400, clientY: 400 }); // other pointer ignored
    canvas.fire('pointerup', { pointerId: 1 });
    canvas.fire('pointermove', { pointerId: 1, clientX: 300, clientY: 300 }); // after up: ignored
    flush();
    const after = handle.camera.position.toArray();
    assert.notDeepEqual(after, before, 'drag orbits camera');
    const d0 = handle.orbit.state.distance;
    assert.equal(canvas.fire('wheel', { deltaY: 100 }), true, 'wheel default prevented');
    assert.ok(handle.orbit.state.distance > d0);
    assert.equal(canvas.fire('keydown', { key: 'ArrowLeft' }), true);
    assert.equal(canvas.fire('keydown', { key: 'Tab' }), false, 'unrelated keys untouched');
    flush(); assert.equal(live.renders, 3);

    canvas.fire('wheel', { deltaY: 10 }); // leaves a pending frame to prove cancel on dispose
    viewer.dispose(); viewer.dispose();
    assert.deepEqual({ gl: live.gl, gpu: live.gpu, nodes: live.nodes, listeners: live.listeners, frames: live.frames.size, observers: live.observers },
      { gl: 0, gpu: 0, nodes: 0, listeners: 0, frames: 0, observers: 0 });
    assert.equal(live.ctxLost, 1);
    assert.deepEqual(states, ['loading', 'ready']);
  } finally { untrack(); }
});

test('100 mount/abort cycles leave no live resources', async () => {
  const { live, host, deps, flush } = fakeEnv();
  const untrack = trackGpu(live);
  try {
    const bundle = await loadFixtureBundle({ validate: false });
    const adapter = createViewerAdapter({ createRenderer: createThreeRenderer(deps) });
    for (let i = 0; i < 100; i++) {
      const ac = new AbortController();
      await adapter.mount(host, SYNTHETIC_FIXTURE.request, services(bundle, ac.signal, [], []));
      if (i % 2) flush();
      ac.abort(); // shell-driven unmount path
    }
    assert.deepEqual({ gl: live.gl, gpu: live.gpu, nodes: live.nodes, listeners: live.listeners, frames: live.frames.size, observers: live.observers },
      { gl: 0, gpu: 0, nodes: 0, listeners: 0, frames: 0, observers: 0 });
  } finally { untrack(); }
});

test('renderer start failure frees partial resources and reports RENDER_FAILED', async () => {
  const { live, host, deps } = fakeEnv();
  const untrack = trackGpu(live);
  try {
    const bundle = await loadFixtureBundle({ validate: false });
    const states = [], errors = [];
    const adapter = createViewerAdapter({ createRenderer: createThreeRenderer({ ...deps, createGLRenderer: () => { throw new Error('no webgl'); } }) });
    await assert.rejects(adapter.mount(host, SYNTHETIC_FIXTURE.request, services(bundle, new AbortController().signal, states, errors)));
    assert.deepEqual(errors.map((e) => e.code), ['RENDER_FAILED']);
    assert.ok(!errors[0].message.includes('webgl'), 'upstream text not forwarded');
    assert.deepEqual({ gpu: live.gpu, nodes: live.nodes, listeners: live.listeners }, { gpu: 0, nodes: 0, listeners: 0 });
  } finally { untrack(); }
});

test('non +Y-up model is rejected before touching the DOM', () => {
  const { live, host, deps } = fakeEnv();
  assert.throws(() => createThreeRenderer(deps)(host, { render: { kind: 'points' }, coordinates: { up: '+Z' } }));
  assert.equal(live.nodes, 0);
});

test('S09d fixture interaction: aligned colliders, projected text labels, camera path playback, clean unmount', async () => {
  const { live, host, deps, flush } = fakeEnv();
  const untrack = trackGpu(live);
  let clock = 1000;
  try {
    const bundle = await loadFixtureBundle();
    bundle.manifest.labels.push({ id: 'html-probe', text: '<img src=x onerror=alert(1)>', position_m: [0.5, 0.75, 0.3] });
    const ac = new AbortController();
    let handle;
    const adapter = createViewerAdapter({ createRenderer: (h, m, s) => (handle = createThreeRenderer({ ...deps, now: () => clock })(h, m, s)) });
    const viewer = await adapter.mount(host, SYNTHETIC_FIXTURE.request, services(bundle, ac.signal, [], []));
    assert.equal(host.style.position, 'relative');
    assert.deepEqual(handle.alignment.issues, []);
    assert.deepEqual(handle.alignment.colliders.map((c) => c.pointsOnFace), [4, 4]);
    const layer = host.children[2];
    assert.deepEqual(layer.children.map((e) => [e.attrs['data-viewer-label'], e.textContent]),
      [['fixture-warning', 'SYNTHETIC — no accuracy or performance claim'], ['html-probe', '<img src=x onerror=alert(1)>']]);
    assert.ok(layer.children.every((e) => e.children.length === 0 && !('innerHTML' in e)), 'labels are text nodes only');
    flush();
    const inView = (s) => s && s[0] >= 0 && s[0] <= 640 && s[1] >= 0 && s[1] <= 480;
    assert.ok(handle.labelScreen().every((l) => inView(l.screen)), 'orbit view shows every label');
    assert.equal(layer.children[0].style.display, '');

    // camera_path key 0: camera (0,1,3) looking -Z, vfov 50, 640x480 -> analytic projection of (0,0.75,0)
    assert.equal(handle.setCameraTime(0), true); flush();
    const s0 = handle.labelScreen()[0].screen;
    const f = 1 / Math.tan((25 * Math.PI) / 180);
    assert.ok(Math.abs(s0[0] - 320) < 1e-6 && Math.abs(s0[1] - (1 + (0.25 / 3) * f) / 2 * 480) < 1e-6, 'label at analytic pixel ' + s0);
    assert.equal(handle.cameraMode, 'path'); assert.equal(handle.camera.fov, 50);
    handle.setCameraTime(1); flush();
    const s1 = handle.labelScreen()[0].screen;
    const dx = (0.25 / 3) * f * (480 / 2); // camera +0.25 m -> label moves left by this many px
    assert.ok(Math.abs(s0[0] - s1[0] - dx) < 1e-6 && Math.abs(s1[1] - s0[1]) < 1e-6, 'label tracks camera path');
    assert.match(layer.children[0].style.transform, /^translate\(/);

    // playback via 'p': frames only while playing, stops on the last key
    const renders0 = live.renders;
    assert.equal(canvas(host).fire('keydown', { key: 'p' }), true);
    assert.equal(handle.playing, true);
    flush(); clock += 500; flush();
    assert.deepEqual(handle.camera.position.toArray().map((v) => +v.toFixed(9)), [0.125, 1, 3]);
    clock += 700; flush();
    assert.equal(handle.playing, false); assert.equal(handle.pendingFrame, false, 'no loop after path end');
    assert.deepEqual(handle.camera.position.toArray(), [0.25, 1, 3]);
    assert.equal(live.renders - renders0, 3);

    // orbit input leaves path mode
    canvas(host).fire('pointerdown', { pointerId: 1, clientX: 1, clientY: 1 });
    assert.equal(handle.cameraMode, 'orbit');
    canvas(host).fire('pointerup', { pointerId: 1 });

    handle.playCameraPath(); // pending frame at dispose
    ac.abort();
    assert.deepEqual({ gl: live.gl, gpu: live.gpu, nodes: live.nodes, listeners: live.listeners, frames: live.frames.size, observers: live.observers },
      { gl: 0, gpu: 0, nodes: 0, listeners: 0, frames: 0, observers: 0 });
    assert.equal(host.style.position, '', 'host style restored');
    assert.equal(handle.setCameraTime(0), false, 'no work after dispose');
    viewer.dispose();
  } finally { untrack(); }
});

function canvas(host) { return host.children.find((c) => c.tag === 'canvas'); }

// S09f: hidden tab or offscreen host -> no frames scheduled; resume redraws once and playback continues where it paused.
test('S09f pauses rendering while hidden or offscreen and resumes correctly', async () => {
  const { live, host, deps, flush, doc, io } = fakeEnv();
  let clock = 1000;
  const bundle = await loadFixtureBundle();
  const ac = new AbortController();
  let handle;
  const adapter = createViewerAdapter({ createRenderer: (h, m, s) => (handle = createThreeRenderer({ ...deps, now: () => clock })(h, m, s)) });
  await adapter.mount(host, SYNTHETIC_FIXTURE.request, services(bundle, ac.signal, [], []));
  flush();
  assert.equal(io.last.el, host, 'observes the host');
  const setHidden = (v) => { doc.hidden = v; doc.fire('visibilitychange'); };
  const key = (k) => canvas(host).fire('keydown', { key: k });

  // hidden tab: input is absorbed without frames; showing redraws exactly once
  let r = live.renders;
  setHidden(true);
  assert.equal(handle.paused, true);
  key('ArrowLeft'); handle.invalidate(); handle.setCameraTime(0.5);
  assert.equal(live.frames.size, 0, 'no frame scheduled while hidden'); flush();
  assert.equal(live.renders, r);
  setHidden(false);
  assert.equal(handle.paused, false); assert.equal(live.frames.size, 1, 'dirty view redraws on resume');
  flush(); assert.equal(live.renders, r + 1); assert.equal(handle.pendingFrame, false);

  // a frame pending at hide is cancelled, then redrawn on show; clean show schedules nothing
  key('ArrowRight'); assert.equal(live.frames.size, 1);
  setHidden(true); assert.equal(live.frames.size, 0, 'pending frame cancelled');
  setHidden(false); assert.equal(live.frames.size, 1); flush();
  setHidden(true); setHidden(false); assert.equal(live.frames.size, 0, 'nothing to redraw');

  // offscreen host (IntersectionObserver) pauses independently of tab visibility
  r = live.renders;
  io.last.cb([{ isIntersecting: false }]);
  assert.equal(handle.paused, true);
  key('ArrowLeft'); flush(); assert.equal(live.renders, r);
  setHidden(true); setHidden(false); assert.equal(handle.paused, true, 'still offscreen');
  io.last.cb([{ isIntersecting: true }]);
  assert.equal(handle.paused, false); flush(); assert.equal(live.renders, r + 1);

  // playback clock freezes while hidden: 500 ms played, 10 s hidden, resumes at t=0.5
  key('p'); flush(); clock += 500; flush();
  assert.deepEqual(handle.camera.position.toArray().map((v) => +v.toFixed(9)), [0.125, 1, 3]);
  setHidden(true); clock += 10000; flush();
  assert.equal(handle.playing, true); assert.equal(live.frames.size, 0);
  setHidden(false); flush();
  assert.deepEqual(handle.camera.position.toArray().map((v) => +v.toFixed(9)), [0.125, 1, 3], 'no jump after resume');
  clock += 700; flush();
  assert.equal(handle.playing, false); assert.equal(handle.pendingFrame, false);

  // mounted while hidden: first frame waits for visibility; dispose frees observers and listeners
  setHidden(true); ac.abort();
  assert.deepEqual({ listeners: live.listeners, frames: live.frames.size, observers: live.observers }, { listeners: 0, frames: 0, observers: 0 });
  const env2 = fakeEnv(); env2.doc.hidden = true;
  const h2 = createThreeRenderer(env2.deps)(env2.host, bigModel(10));
  assert.equal(h2.paused, true); assert.equal(env2.live.frames.size, 0);
  env2.doc.hidden = false; env2.doc.fire('visibilitychange'); env2.flush();
  assert.equal(env2.live.renders, 1);
  h2.dispose();
});

// S09e: budget is decided once at mount from injected device facts.
const bigModel = (n) => ({
  render: { kind: 'points', positions: Float32Array.from({ length: n * 3 }, (_, i) => (i % 3) / 10), colors: new Uint8Array(n * 3), count: n },
  coordinates: { up: '+Y' }, boundsM: { min: [0, 0, 0], max: [1, 1, 1] }, colliders: [], labels: [], surfaces: [], cameraPath: null,
});

test('375 px phone budget: DPR 3 -> 1.5, no antialias, 600k points decimated to 200k', () => {
  const { live, host, deps } = fakeEnv();
  const handle = createThreeRenderer({ ...deps, device: () => ({ devicePixelRatio: 3, viewportWidthPx: 375 }) })(host, bigModel(600_000));
  try {
    assert.equal(live.pixelRatio, 1.5);
    assert.equal(live.glOpts.antialias, false);
    assert.deepEqual({ ...handle.budget }, { tier: 'reduced', pixelRatio: 1.5, maxPoints: 250_000, antialias: false });
    assert.equal(handle.pointCount, 200_000); // stride ceil(600000/250000)=3
  } finally { handle.dispose(); }
  assert.equal(live.gl, 0);
});

test('S09g 375 px compact layout: canvas fits host, reduced label detail, touch-size controls zoom/play, full again when wide', async () => {
  const { live, host, deps, flush, io } = fakeEnv();
  host.clientWidth = 375; host.clientHeight = 300;
  const bundle = await loadFixtureBundle({ validate: false });
  let h;
  const viewer = await createViewerAdapter({ createRenderer: (x, m, s) => (h = createThreeRenderer(deps)(x, m, s)) })
    .mount(host, SYNTHETIC_FIXTURE.request, services(bundle, new AbortController().signal, [], []));
  const [canvas] = host.children;
  assert.deepEqual([canvas.style.display, canvas.style.width, canvas.style.height, canvas.style.maxWidth], ['block', '100%', '100%', '100%'], 'canvas CSS size follows host, never the DPR-scaled buffer');
  assert.equal(host.style.position, 'relative');
  const bar = host.children.find((c) => c.attrs['data-viewer-controls'] !== undefined);
  assert.ok(bar, 'controls toolbar'); assert.equal(bar.attrs.role, 'toolbar');
  assert.equal(h.layout, 'compact'); assert.equal(bar.attrs['data-viewer-layout'], 'compact');
  const btns = bar.children;
  assert.deepEqual(btns.map((b) => b.attrs['aria-label']), ['Zoom in', 'Zoom out', 'Play camera path']);
  for (const b of btns) { assert.equal(b.type, 'button'); assert.equal(b.style.minWidth, '44px'); assert.equal(b.style.minHeight, '44px'); }
  const layer = host.children.find((c) => c.attrs['data-viewer-labels'] !== undefined);
  const lab = layer.children[0];
  assert.deepEqual([lab.style.maxWidth, lab.style.overflow, lab.style.textOverflow], ['40%', 'hidden', 'ellipsis'], 'labels truncated in compact');
  flush();
  const d0 = h.orbit.state.distance;
  btns[0].fire('click'); assert.ok(h.orbit.state.distance < d0, 'zoom in'); assert.equal(h.pendingFrame, true);
  flush(); btns[1].fire('click'); btns[1].fire('click'); assert.ok(h.orbit.state.distance > d0, 'zoom out');
  btns[2].fire('click'); assert.equal(h.playing, true); assert.equal(h.cameraMode, 'path');
  host.clientWidth = 900; io.ro.cb([]);
  assert.equal(h.layout, 'full'); assert.equal(bar.attrs['data-viewer-layout'], 'full'); assert.equal(lab.style.maxWidth, '');
  viewer.dispose();
  assert.deepEqual({ nodes: live.nodes, listeners: live.listeners, observers: live.observers }, { nodes: 0, listeners: 0, observers: 0 });
  assert.equal(host.style.position, '');
});

test('desktop budget: DPR 3 -> 2, antialias, points untouched; same device twice -> same budget', () => {
  const { live, host, deps } = fakeEnv();
  const make = createThreeRenderer({ ...deps, device: () => ({ devicePixelRatio: 3, viewportWidthPx: 1920, deviceMemoryGiB: 8, cores: 8 }) });
  const a = make(host, bigModel(600_000));
  assert.equal(live.pixelRatio, 2); assert.equal(live.glOpts.antialias, true); assert.equal(a.pointCount, 600_000);
  a.dispose();
  const b = make(host, bigModel(600_000));
  assert.deepEqual(b.budget, a.budget); assert.equal(b.pointCount, 600_000);
  b.dispose();
});
