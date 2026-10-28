// F-CLAUDE-2 read-only probes of F-CLAUDE-1 [R] claims. Imports product code from the main checkout
// (worktree lacks Build/web/node_modules). Run: node evidence/fillers/CLAUDE/2/probes.mjs <mainRoot>
import { pathToFileURL } from 'node:url';
import path from 'node:path';
const ROOT = path.resolve(process.argv[2] ?? '.');
const imp = (p) => import(pathToFileURL(path.join(ROOT, p)).href);
const THREE = await imp('Build/web/node_modules/three/build/three.module.js');
const { createViewerAdapter } = await imp('Build/web/src/viewer/adapter.mjs');
const { createThreeRenderer } = await imp('Build/web/src/viewer/three-renderer.mjs');
const { buildSceneModel } = await imp('Build/web/src/viewer/scene-model.mjs');
const { overlayAlignment } = await imp('Build/web/src/viewer/scene-overlays.mjs');
const { createArtifactLoader, readCapped } = await imp('Build/web/src/viewer/artifact-loader.mjs');
const { SYNTHETIC_FIXTURE } = await imp('Build/web/src/viewer/fixture.mjs');
const { loadFixtureBundle } = await imp('tests/viewer/fixture-bundle.mjs');

function fakeEnv() {
  const live = { frames: new Map(), renders: 0 }; let nf = 1;
  class El { constructor(d, t) { this.ownerDocument = d; this.tag = t; this.children = []; this.parent = null; this.l = new Map(); this.attrs = {}; this.style = {}; this.textContent = ''; this.clientWidth = 640; this.clientHeight = 480; }
    setAttribute(k, v) { this.attrs[k] = String(v); } appendChild(c) { c.parent = this; this.children.push(c); return c; }
    remove() { if (this.parent) { this.parent.children.splice(this.parent.children.indexOf(this), 1); this.parent = null; } }
    addEventListener(t, f) { const s = this.l.get(t) ?? new Set(); s.add(f); this.l.set(t, s); } removeEventListener(t, f) { this.l.get(t)?.delete(f); }
    fire(t, ev = {}) { for (const f of [...(this.l.get(t) ?? [])]) f({ preventDefault() {}, ...ev }); } }
  const doc = Object.assign(new El(null, '#doc'), { hidden: false, createElement: (t) => new El(doc, t) });
  const host = new El(doc, 'div'); const io = {};
  const deps = { THREE, createGLRenderer: () => ({ setPixelRatio() {}, setSize() {}, render() { live.renders++; }, dispose() {}, forceContextLoss() {} }),
    requestFrame: (cb) => { const id = nf++; live.frames.set(id, cb); return id; }, cancelFrame: (id) => live.frames.delete(id),
    ResizeObserverImpl: class { observe() {} disconnect() {} },
    IntersectionObserverImpl: class { constructor(cb) { this.cb = cb; io.last = this; } observe() {} disconnect() {} },
    device: () => ({ devicePixelRatio: 1, viewportWidthPx: 1440 }) };
  const flush = () => { const f = [...live.frames.values()]; live.frames.clear(); f.forEach((cb) => cb()); };
  return { live, host, doc, deps, flush, io, El };
}
const out = {};
const run = async (name, fn) => { try { out[name] = await fn(); } catch (e) { out[name] = { probeThrew: String(e?.code ?? '') + ' ' + String(e?.message ?? e) }; } };
const REQ = SYNTHETIC_FIXTURE.request;
async function mountWith(edit, env = fakeEnv(), extra = {}) {
  const b = await loadFixtureBundle({ validate: false }); edit?.(b.manifest);
  const errors = [], states = []; let handle, rejected = null; const ac = new AbortController();
  const adapter = createViewerAdapter({ createRenderer: (h, m, s) => (handle = createThreeRenderer({ ...env.deps, ...extra })(h, m, s)) });
  try { await adapter.mount(env.host, REQ, { loadScene: async () => b, signal: ac.signal, onState: (s) => states.push(s), onError: (e) => errors.push(e) }); }
  catch (e) { rejected = e?.code ?? String(e); }
  return { env, handle, errors: errors.map((e) => e.code + ': ' + e.message), states, rejected, ac };
}
// 1. invalid manifest geometry -> which error code?
for (const [k, edit] of Object.entries({
  boundsMissingMax: (m) => { m.bounds_m = { min: [0, 0, 0] }; },
  colliderNoHalfExtents: (m) => { delete m.colliders[0].half_extents_m; delete m.colliders[0].size_m; },
  coordinatesNoUp: (m) => { delete m.coordinates.up; },
})) await run('geom_' + k, async () => { const r = await mountWith(edit); return { rejected: r.rejected, errors: r.errors }; });
// 2. label without position_m: crash per frame?
await run('labelNoPosition', async () => {
  const r = await mountWith((m) => { m.labels = [{ id: 'x', text: 't' }]; });
  if (r.rejected) return { rejected: r.rejected, errors: r.errors };
  const thrown = []; for (let i = 0; i < 3; i++) { try { r.env.flush(); thrown.push('ok'); } catch (e) { thrown.push(e.constructor.name); } r.handle.invalidate?.(); }
  return { mounted: true, frames: thrown };
});
// 3. null / missing label text
await run('labelTextNull', async () => { const b = await loadFixtureBundle({ validate: false }); b.manifest.labels = [{ id: 'a', text: null, position_m: [0, 0, 0] }, null].slice(0, 1);
  const m = await buildSceneModel(b, REQ.scene); return { text: m.labels[0].text }; });
await run('labelNullEntry', async () => { const b = await loadFixtureBundle({ validate: false }); b.manifest.labels = [null];
  const m = await buildSceneModel(b, REQ.scene); return { text: m.labels[0].text, id: m.labels[0].id }; });
await run('labelTextMissing', async () => { const b = await loadFixtureBundle({ validate: false }); b.manifest.labels = [{ id: 'a', position_m: [0, 0, 0] }];
  const m = await buildSceneModel(b, REQ.scene); return { text: m.labels[0].text }; });
await run('labelNullEntryViaAdapter', async () => { const r = await mountWith((m) => { m.labels = [null]; }); return { rejected: r.rejected, errors: r.errors }; });
// 4b. measured: camera position 1 s after resume vs 1 s after an unpaused play
await run('playWhilePausedMeasured', async () => {
  const pos = async (paused) => { let clock = 1000; const env = fakeEnv(); const r = await mountWith(null, env, { now: () => clock }); env.flush();
    if (paused) { env.doc.hidden = true; env.doc.fire('visibilitychange'); clock = 5000; r.handle.playCameraPath(); clock = 6000; env.doc.hidden = false; env.doc.fire('visibilitychange'); }
    else { clock = 6000; r.handle.playCameraPath(); }
    clock += 1000; env.flush(); return r.handle.camera.position.toArray().map((v) => +v.toFixed(4)); };
  const first = async () => { let clock = 1000; const env = fakeEnv(); const r = await mountWith(null, env, { now: () => clock }); env.flush(); r.handle.playCameraPath(); env.flush(); return r.handle.camera.position.toArray().map((v) => +v.toFixed(4)); };
  return { unpausedAt1s: await pos(false), playPressedWhilePausedAt1sAfterResume: await pos(true), firstKey: await first() };
});
// 4. play pressed while paused
await run('playWhilePaused', async () => {
  let clock = 1000; const env = fakeEnv(); const r = await mountWith(null, env, { now: () => clock }); env.flush();
  env.doc.hidden = true; env.doc.fire('visibilitychange'); clock = 5000; r.handle.playCameraPath(); clock = 6000;
  env.doc.hidden = false; env.doc.fire('visibilitychange');
  // expected elapsed playback = 0 s at resume (play was pressed while paused); observe elapsed from camera pose
  const elapsedAtResume = r.handle.playing ? 'playing' : 'stopped'; env.flush();
  return { pausedThenPlay: elapsedAtResume, note: 'see pose in playStartShift', playStartShift: 'playStart(5000) += 6000-1000 => 10000; now 6000 -> elapsed -4 s (clamped to first key) instead of 0' };
});
// 5. empty IntersectionObserver entries
await run('ioEmptyEntries', async () => { const env = fakeEnv(); await mountWith(null, env); try { env.io.last.cb([]); return 'no throw'; } catch (e) { return 'throws ' + e.constructor.name; } });
// 6. two mounts in one host
await run('twoMountsOneHost', async () => { const env = fakeEnv(); const a = await mountWith(null, env); const b = await mountWith(null, env);
  const before = env.host.style.position; a.ac.abort(); return { before, afterDisposeA: env.host.style.position, bLive: !!b.handle }; });
// 7. stylesheet-positioned host (inline style empty) gets forced relative
await run('hostPositionOverride', async () => { const env = fakeEnv(); await mountWith(null, env); return { inlineAfterMount: env.host.style.position }; });
// 8. points outside bounds_m
await run('pointOutlierVsBounds', async () => { const b = await loadFixtureBundle({ validate: false }); const m = await buildSceneModel(b, REQ.scene);
  const p = Float32Array.from(m.render.positions); p[0] = 1e6; const a = overlayAlignment(m, { positions: p }); return { ok: a.ok, issues: (a.issues ?? []).length }; });
// 9. loader: credentials URL, non-numeric content-length, non-GET init
const BASE = 'https://artifacts.test/b/';
await run('loaderCredentialsUrl', async () => { const calls = []; const ld = createArtifactLoader({ bundleUrl: () => 'https://u:p@artifacts.test/b/', fetch: async (u) => { calls.push(u); throw new Error('net'); } });
  try { await ld(REQ.scene); } catch (e) { return { code: e.code, fetchedUrl: calls[0] }; } });
await run('contentLengthNonNumeric', async () => { try { await readCapped(new Response('abc', { headers: { 'content-length': 'abc' } }), 1000, 'manifest'); return 'accepted'; } catch (e) { return e.code + ': ' + e.message; } });
await run('loaderInitMethodPost', async () => { const seen = []; const ld = createArtifactLoader({ bundleUrl: () => BASE, init: { method: 'POST', body: 'x' }, fetch: async (u, i) => { seen.push(i.method); throw new Error('stop'); } });
  try { await ld(REQ.scene); } catch {} return { methodSent: seen[0] }; });
// 10. throwing onError replaces ViewerError
await run('throwingOnError', async () => { const ac = new AbortController(); const ad = createViewerAdapter({ createRenderer: () => { throw new Error('x'); } }); const b = await loadFixtureBundle({ validate: false });
  try { await ad.mount(fakeEnv().host, REQ, { loadScene: async () => b, signal: ac.signal, onState() {}, onError() { throw new Error('cb boom'); } }); } catch (e) { return { name: e.constructor.name, code: e.code ?? null, message: e.message }; } });
await run('mountWithoutSignal', async () => { const ad = createViewerAdapter({ createRenderer: () => ({ dispose() {} }) });
  try { await ad.mount(fakeEnv().host, REQ, { loadScene: async () => ({}), onState() {}, onError() {} }); return 'ok'; } catch (e) { return e.constructor.name + (e.code ? ' ' + e.code : ''); } });
console.log(JSON.stringify(out, null, 1));

