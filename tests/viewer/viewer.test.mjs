// S09a: viewer adapter contract + synthetic fixture scene. Run: node --test tests/viewer/
import test from 'node:test';
import assert from 'node:assert/strict';
import { createViewerAdapter, ViewerError } from '../../Build/web/src/viewer/adapter.mjs';
import { buildSceneModel } from '../../Build/web/src/viewer/scene-model.mjs';
import { SYNTHETIC_FIXTURE, SYNTHETIC_BANNER } from '../../Build/web/src/viewer/fixture.mjs';
import { loadFixtureBundle, loadFixtureMount } from './fixture-bundle.mjs';

const clone = (v) => structuredClone(v);
const host = {}; // adapter never touches the DOM itself; the injected renderer owns the canvas
const REQ = SYNTHETIC_FIXTURE.request;

function fakeRenderer() {
  const log = { created: 0, disposed: 0, model: null, fail: false };
  return {
    log,
    createRenderer: async (h, model) => {
      if (log.fail) throw new Error('gpu lost');
      log.created++; log.model = model;
      return { dispose() { log.disposed++; } };
    },
  };
}

function services(bundle, extra = {}) {
  const ac = new AbortController();
  const states = []; const errors = [];
  return {
    ac, states, errors,
    svc: {
      loadScene: extra.loadScene ?? (async () => clone(bundle)),
      signal: ac.signal,
      onState: (s) => states.push(s),
      onError: (e) => errors.push(e),
    },
  };
}

test('fixture scene is the S04a mount, marked synthetic, not Gate R evidence', async () => {
  const mount = await loadFixtureMount();
  assert.equal(REQ.scene.scene_id, mount.scene_id);
  assert.equal(REQ.scene.evidence, 'synthetic');
  assert.equal(SYNTHETIC_FIXTURE.repositoryManifest, mount.repository_manifest);
  assert.equal(SYNTHETIC_FIXTURE.gateEvidence, false);
  assert.match(SYNTHETIC_BANNER, /SYNTHETIC/);
  assert.match(SYNTHETIC_BANNER, /not .*Gate R evidence/i);
  assert.ok(Object.isFrozen(SYNTHETIC_FIXTURE) && Object.isFrozen(REQ.scene));
});

test('scene model decodes PLY points and carries synthetic banner, physics disabled', async () => {
  const model = await buildSceneModel(await loadFixtureBundle(), REQ.scene);
  assert.equal(model.sceneId, 'synthetic-room-v1');
  assert.equal(model.synthetic, true);
  assert.equal(model.banner, SYNTHETIC_BANNER);
  assert.equal(model.gateEvidence, false);
  assert.equal(model.physicsEnabled, false);
  assert.equal(model.render.kind, 'points');
  assert.equal(model.render.count, 8);
  assert.ok(model.render.positions instanceof Float32Array && model.render.positions.length === 24);
  assert.deepEqual([...model.render.positions.slice(12, 15)].map((v) => +v.toFixed(6)), [-0.5, 0.75, -0.3]);
  assert.deepEqual([...model.render.colors.slice(0, 3)], [120, 140, 160]);
  assert.equal(model.surfaces.length, 2);
  assert.equal(model.colliders.length, 2);
  assert.equal(model.cameraPath[0].vertical_fov_deg, 50);
  assert.equal(typeof model.labels[0].text, 'string');
  assert.ok(Object.isFrozen(model) && Object.isFrozen(model.render) && Object.isFrozen(model.surfaces[0]));
});

test('scene model rejects mismatches and tampered bytes', async () => {
  const good = await loadFixtureBundle();
  const cases = [
    ['wrong id', (b) => { b.manifest.id = 'other'; }],
    ['schema version', (b) => { b.manifest.schema_version = '2.0.0'; }],
    ['synthetic vs reconstructed', (b) => { b.manifest.synthetic = false; }],
    ['missing asset bytes', (b) => { delete b.assets.points; }],
    ['byte length', (b) => { b.assets.points = b.assets.points.slice(1); }],
    ['sha256', (b) => { const a = b.assets.points.slice(); a[a.length - 2] ^= 1; b.assets.points = a; }],
    ['point count', (b) => { b.manifest.render.point_count = 9; }],
    ['unsupported render kind', (b) => { b.manifest.render.kind = 'splats'; }],
  ];
  for (const [name, mutate] of cases) {
    const b = { manifest: clone(good.manifest), assets: { ...good.assets } }; mutate(b);
    await assert.rejects(buildSceneModel(b, REQ.scene), (e) => e instanceof ViewerError && ['INVALID_ARTIFACT', 'UNSUPPORTED'].includes(e.code), name);
  }
});

test('mount: loading -> ready, idempotent dispose, no callbacks after dispose', async () => {
  const bundle = await loadFixtureBundle({ validate: false });
  const r = fakeRenderer(); const s = services(bundle);
  const handle = await createViewerAdapter(r).mount(host, REQ, s.svc);
  assert.deepEqual(s.states, ['loading', 'ready']);
  assert.equal(r.log.model.banner, SYNTHETIC_BANNER);
  handle.dispose(); handle.dispose();
  assert.equal(r.log.disposed, 1);
  s.ac.abort();
  assert.deepEqual(s.states, ['loading', 'ready']);
  assert.equal(s.errors.length, 0);
});

test('shell abort after ready disposes the renderer once', async () => {
  const bundle = await loadFixtureBundle({ validate: false });
  const r = fakeRenderer(); const s = services(bundle);
  const handle = await createViewerAdapter(r).mount(host, REQ, s.svc);
  s.ac.abort(); handle.dispose();
  assert.equal(r.log.disposed, 1);
});

test('mount rejects invalid requests before loading', async () => {
  const bundle = await loadFixtureBundle({ validate: false });
  const bad = [
    { ...clone(REQ), contract_version: '2.0.0' },
    { ...clone(REQ), kind: 'job' },
    { ...clone(REQ), extra: 1 },
    { ...clone(REQ), scene: { ...REQ.scene, access: 'private' } },
    { ...clone(REQ), scene: { ...REQ.scene, scene_version: '0.9.0' } },
    { ...clone(REQ), scene: { ...REQ.scene, scene_id: '../etc' } },
  ];
  for (const req of bad) {
    let loads = 0; const r = fakeRenderer();
    const s = services(bundle, { loadScene: async () => { loads++; return clone(bundle); } });
    await assert.rejects(createViewerAdapter(r).mount(host, req, s.svc), (e) => e.code === 'INVALID_REQUEST');
    assert.equal(loads, 0); assert.equal(r.log.created, 0);
    assert.deepEqual(s.states, ['error']); assert.equal(s.errors[0].code, 'INVALID_REQUEST');
  }
});

test('mystery mode is unavailable until S10 redacted payload exists', async () => {
  const bundle = await loadFixtureBundle({ validate: false });
  const r = fakeRenderer(); let loads = 0;
  const s = services(bundle, { loadScene: async () => { loads++; return clone(bundle); } });
  await assert.rejects(createViewerAdapter(r).mount(host, { ...clone(REQ), mode: 'mystery' }, s.svc), (e) => e.code === 'UNAVAILABLE');
  assert.equal(loads, 0); assert.deepEqual(s.states, ['unavailable']);
});

test('abort during load rejects, never renders, stays silent', async () => {
  const bundle = await loadFixtureBundle({ validate: false });
  const r = fakeRenderer(); let release;
  const s = services(bundle, { loadScene: () => new Promise((res) => { release = () => res(clone(bundle)); }) });
  const p = createViewerAdapter(r).mount(host, REQ, s.svc);
  await new Promise((res) => setImmediate(res));
  s.ac.abort(); release();
  await assert.rejects(p, (e) => e.name === 'AbortError');
  assert.equal(r.log.created, 0);
  assert.deepEqual(s.states, ['loading']); assert.equal(s.errors.length, 0);
});

test('already-aborted signal rejects immediately', async () => {
  const bundle = await loadFixtureBundle({ validate: false });
  const r = fakeRenderer(); const s = services(bundle); s.ac.abort();
  await assert.rejects(createViewerAdapter(r).mount(host, REQ, s.svc), (e) => e.name === 'AbortError');
  assert.deepEqual(s.states, []);
});

test('abort while renderer is being created disposes the partial renderer', async () => {
  const bundle = await loadFixtureBundle({ validate: false });
  const log = { disposed: 0 }; const s = services(bundle);
  const adapter = createViewerAdapter({ createRenderer: async () => { s.ac.abort(); return { dispose() { log.disposed++; } }; } });
  await assert.rejects(adapter.mount(host, REQ, s.svc), (e) => e.name === 'AbortError');
  assert.equal(log.disposed, 1); assert.deepEqual(s.states, ['loading']);
});

test('load and renderer failures report error state with plain codes', async () => {
  const bundle = await loadFixtureBundle({ validate: false });
  const s1 = services(bundle, { loadScene: async () => { throw new Error('secret transport detail https://x?token=1'); } });
  await assert.rejects(createViewerAdapter(fakeRenderer()).mount(host, REQ, s1.svc), (e) => e.code === 'LOAD_FAILED');
  assert.deepEqual(s1.states, ['loading', 'error']);
  assert.equal(s1.errors[0].code, 'LOAD_FAILED');
  assert.doesNotMatch(s1.errors[0].message, /token|https/);
  const r = fakeRenderer(); r.log.fail = true; const s2 = services(bundle);
  await assert.rejects(createViewerAdapter(r).mount(host, REQ, s2.svc), (e) => e.code === 'RENDER_FAILED');
  assert.deepEqual(s2.states, ['loading', 'error']);
});
