// S09c: validating artifact loader + splat decoder. Synthetic bytes only (fixture or generated here):
// not reconstruction, measured/simulated or Gate R evidence. Real artifacts wait for S05.
import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { createArtifactLoader, checkManifest, DEFAULT_LIMITS } from '../../Build/web/src/viewer/artifact-loader.mjs';
import { buildSceneModel, decodeSplats } from '../../Build/web/src/viewer/scene-model.mjs';
import { createViewerAdapter, ViewerError } from '../../Build/web/src/viewer/adapter.mjs';
import { SYNTHETIC_FIXTURE } from '../../Build/web/src/viewer/fixture.mjs';
import { ROOT, loadFixtureMount } from './fixture-bundle.mjs';

const REQ = SYNTHETIC_FIXTURE.request;
const BASE = 'https://artifacts.test/bundles/synthetic-room-v1/';
const sha = (b) => createHash('sha256').update(b).digest('hex');
const enc = (o) => new TextEncoder().encode(JSON.stringify(o));

async function fixtureFiles() {
  const mount = await loadFixtureMount();
  const mPath = path.join(ROOT, mount.repository_manifest);
  const manifest = JSON.parse(await readFile(mPath, 'utf8'));
  const files = { 'scene.json': enc(manifest) };
  for (const a of manifest.assets) files[a.path] = new Uint8Array(await readFile(path.join(path.dirname(mPath), a.path)));
  return { manifest, files };
}

function splatBytes(n, edit) {
  const b = new Uint8Array(n * 32); const dv = new DataView(b.buffer);
  for (let i = 0; i < n; i++) {
    const o = i * 32;
    [i * 0.1, 0.5, -0.2].forEach((v, k) => dv.setFloat32(o + k * 4, v, true));
    [0.01, 0.02, 0.03].forEach((v, k) => dv.setFloat32(o + 12 + k * 4, v, true));
    b.set([200, 100, 50, 255], o + 24);
    b.set([255, 128, 128, 128], o + 28); // w ~= 0.992, identity
  }
  edit?.(b, dv);
  return b;
}

function splatFiles(manifest, bytes, n = bytes.byteLength / 32) {
  const m = structuredClone(manifest);
  m.assets = [{ id: 'splats', path: 'splats/main.splat', format: 'splat', sha256: sha(bytes), bytes: bytes.byteLength }];
  m.render = { kind: 'splats', asset_id: 'splats', mobile_asset_id: 'splats', point_count: n };
  return { manifest: m, files: { 'scene.json': enc(m), 'splats/main.splat': bytes } };
}

/** Fake transport: serves files under BASE, records requests; opts.lie overrides content-length. */
function fakeFetch(files, opts = {}) {
  const calls = [];
  const fn = async (url, init) => {
    calls.push({ url, init });
    if (init.signal?.aborted) throw new DOMException('aborted', 'AbortError');
    if (opts.hang) return new Promise((_, rej) => init.signal.addEventListener('abort', () => rej(new DOMException('aborted', 'AbortError'))));
    if (!url.startsWith(BASE)) return new Response('nope', { status: 404 });
    const rel = url.slice(BASE.length);
    if (!Object.hasOwn(files, rel)) return new Response('missing', { status: 404 });
    const body = files[rel];
    const headers = opts.lie?.[rel] != null ? { 'content-length': String(opts.lie[rel]) } : {};
    return new Response(body, { status: 200, headers });
  };
  return { fn, calls };
}

const loader = (files, opts, extra = {}) => {
  const f = fakeFetch(files, opts);
  return { f, load: createArtifactLoader({ bundleUrl: () => BASE, fetch: f.fn, ...extra }) };
};
const isCode = (code) => (e) => e instanceof ViewerError && e.code === code;

test('loads the fixture bundle over transport, fetches only manifest + render asset, safe fetch options', async () => {
  const { manifest, files } = await fixtureFiles();
  const { f, load } = loader(files);
  const ac = new AbortController();
  const bundle = await load(REQ.scene, ac.signal);
  assert.deepEqual(bundle.manifest, manifest);
  assert.deepEqual(Object.keys(bundle.assets), [manifest.render.asset_id]);
  assert.deepEqual(f.calls.map((c) => c.url), [BASE + 'scene.json', BASE + manifest.assets.find((a) => a.id === manifest.render.asset_id).path]);
  for (const c of f.calls) { assert.equal(c.init.redirect, 'error'); assert.equal(c.init.signal, ac.signal); }
  const model = await buildSceneModel(bundle, REQ.scene);
  assert.equal(model.render.sourceKind, 'points');
  assert.equal(model.render.count, 8);
});

test('adapter end-to-end with the loader: loading -> ready; loader codes pass through', async () => {
  const { files } = await fixtureFiles();
  const run = async (load) => {
    const states = []; const errors = []; let created = 0;
    const adapter = createViewerAdapter({ createRenderer: () => { created++; return { dispose() {} }; } });
    const ac = new AbortController();
    const p = adapter.mount({}, REQ, { loadScene: load, signal: ac.signal, onState: (s) => states.push(s), onError: (e) => errors.push(e) });
    return { p, states, errors, created: () => created };
  };
  const ok = await run(loader(files).load);
  (await ok.p).dispose();
  assert.deepEqual(ok.states, ['loading', 'ready']);
  const tampered = { ...files }; const t = files['points/room-v1.ply'] ?? Object.values(files)[1];
  const key = Object.keys(files).find((k) => k !== 'scene.json'); tampered[key] = t.slice(); tampered[key][5] ^= 1;
  const badRun = await run(loader(tampered).load);
  await assert.rejects(badRun.p, isCode('INVALID_ARTIFACT'));
  assert.deepEqual(badRun.states, ['loading', 'error']);
  assert.deepEqual(badRun.errors, [{ code: 'INVALID_ARTIFACT', message: 'render asset sha256 mismatch' }]);
  assert.equal(badRun.created(), 0);
  const foreign = await run(async () => { throw new Error('upstream secret detail'); });
  await assert.rejects(foreign.p, isCode('LOAD_FAILED'));
  assert.doesNotMatch(foreign.errors[0].message, /secret/);
});

test('splat bundle: loads, decodes centres/colours/scales/quaternions, renders as points', async () => {
  const { manifest } = await fixtureFiles();
  const s = splatFiles(manifest, splatBytes(3));
  const bundle = await loader(s.files).load(REQ.scene, new AbortController().signal);
  const model = await buildSceneModel(bundle, REQ.scene);
  assert.equal(model.render.kind, 'points');
  assert.equal(model.render.sourceKind, 'splats');
  assert.equal(model.render.count, 3);
  assert.deepEqual([...model.render.positions.slice(3, 6)].map((v) => +v.toFixed(5)), [0.1, 0.5, -0.2]);
  assert.deepEqual([...model.render.colors.slice(0, 3)], [200, 100, 50]);
  assert.equal(model.render.splat.opacity[2], 255);
  assert.equal(+model.render.splat.scales[2].toFixed(5), 0.03);
  assert.deepEqual([...model.render.splat.rotations.slice(0, 4)], [127 / 128, 0, 0, 0]);
  assert.equal(model.gateEvidence, false); assert.equal(model.physicsEnabled, false);
});

test('decodeSplats rejects bad records', () => {
  const cases = [
    ['length', splatBytes(2).slice(1), 2],
    ['count 0', new Uint8Array(0), 0],
    ['NaN position', splatBytes(2, (b, dv) => dv.setFloat32(32 + 4, NaN, true)), 2],
    ['Inf position', splatBytes(2, (b, dv) => dv.setFloat32(0, Infinity, true)), 2],
    ['negative scale', splatBytes(2, (b, dv) => dv.setFloat32(12, -1, true)), 2],
    ['NaN scale', splatBytes(2, (b, dv) => dv.setFloat32(20, NaN, true)), 2],
    ['zero quaternion', splatBytes(2, (b) => b.set([128, 128, 128, 128], 32 + 28)), 2],
    ['long quaternion', splatBytes(2, (b) => b.set([255, 255, 128, 128], 28)), 2],
  ];
  for (const [name, bytes, n] of cases) assert.throws(() => decodeSplats(bytes, n), isCode('INVALID_ARTIFACT'), name);
});

test('loader rejects unsafe or inconsistent manifests before fetching assets', async () => {
  const { manifest, files } = await fixtureFiles();
  const rid = manifest.render.asset_id;
  const cases = [
    ['traversal path', (m) => { m.assets[0].path = '../secret.ply'; }, 'INVALID_ARTIFACT'],
    ['absolute url path', (m) => { m.assets[0].path = 'https://evil.test/x.ply'; }, 'INVALID_ARTIFACT'],
    ['backslash path', (m) => { m.assets[0].path = 'a\\b.ply'; }, 'INVALID_ARTIFACT'],
    ['query path', (m) => { m.assets[0].path = 'a.ply?x=1'; }, 'INVALID_ARTIFACT'],
    ['ext/format mismatch', (m) => { m.assets[0].path = 'points/x.glb'; }, 'INVALID_ARTIFACT'],
    ['duplicate id', (m) => { m.assets.push(structuredClone(m.assets[0])); }, 'INVALID_ARTIFACT'],
    ['declared bytes over limit', (m) => { m.assets[0].bytes = DEFAULT_LIMITS.assetBytes + 1; }, 'INVALID_ARTIFACT'],
    ['bad sha field', (m) => { m.assets[0].sha256 = 'ABC'; }, 'INVALID_ARTIFACT'],
    ['id mismatch', (m) => { m.id = 'other-scene'; }, 'INVALID_ARTIFACT'],
    ['evidence mismatch', (m) => { m.synthetic = false; }, 'INVALID_ARTIFACT'],
    ['schema version', (m) => { m.schema_version = '2.0.0'; }, 'INVALID_ARTIFACT'],
    ['missing render asset', (m) => { m.render.asset_id = 'nope'; }, 'INVALID_ARTIFACT'],
    ['kind/format mismatch', (m) => { m.render.kind = 'splats'; }, 'INVALID_ARTIFACT'],
    ['point_count over limit', (m) => { m.render.point_count = DEFAULT_LIMITS.points + 1; }, 'INVALID_ARTIFACT'],
    ['point_count zero', (m) => { m.render.point_count = 0; }, 'INVALID_ARTIFACT'],
    ['mesh unsupported', (m) => { m.render.kind = 'mesh'; m.render.point_count = 0; Object.assign(m.assets.find((a) => a.id === rid), { format: 'glb', path: 'mesh/room.glb' }); }, 'UNSUPPORTED'],
  ];
  for (const [name, mutate, code] of cases) {
    const m = structuredClone(manifest); mutate(m);
    const { f, load } = loader({ ...files, 'scene.json': enc(m) });
    await assert.rejects(load(REQ.scene, new AbortController().signal), isCode(code), name);
    assert.equal(f.calls.length, 1, name + ': no asset fetch after manifest rejection');
  }
  assert.throws(() => checkManifest([], REQ.scene), isCode('INVALID_ARTIFACT'));
});

test('loader enforces transport integrity: status, JSON, size caps, length and sha', async () => {
  const { manifest, files } = await fixtureFiles();
  const a = manifest.assets.find((x) => x.id === manifest.render.asset_id);
  const cases = [
    ['manifest 404', () => loader({}), 'LOAD_FAILED'],
    ['asset 404', () => { const f = { ...files }; delete f[a.path]; return loader(f); }, 'LOAD_FAILED'],
    ['manifest not JSON', () => loader({ ...files, 'scene.json': new TextEncoder().encode('{bad') }), 'INVALID_ARTIFACT'],
    ['manifest over cap', () => loader(files, {}, { limits: { manifestBytes: 16 } }), 'INVALID_ARTIFACT'],
    ['content-length over declared', () => loader(files, { lie: { [a.path]: a.bytes + 1 } }), 'INVALID_ARTIFACT'],
    ['body longer than declared', () => { const f = { ...files }; f[a.path] = new Uint8Array([...files[a.path], 10]); return loader(f); }, 'INVALID_ARTIFACT'],
    ['body shorter than declared', () => { const f = { ...files }; f[a.path] = files[a.path].slice(1); return loader(f); }, 'INVALID_ARTIFACT'],
    ['sha mismatch, same length', () => { const f = { ...files }; f[a.path] = files[a.path].slice(); f[a.path][3] ^= 1; return loader(f); }, 'INVALID_ARTIFACT'],
    ['network error', () => ({ load: createArtifactLoader({ bundleUrl: () => BASE, fetch: async () => { throw new TypeError('net down'); } }) }), 'LOAD_FAILED'],
    ['bad bundle root (query)', () => ({ load: createArtifactLoader({ bundleUrl: () => BASE + '?sig=1', fetch: fakeFetch(files).fn }) }), 'LOAD_FAILED'],
    ['bad bundle root (no slash)', () => ({ load: createArtifactLoader({ bundleUrl: () => BASE.slice(0, -1), fetch: fakeFetch(files).fn }) }), 'LOAD_FAILED'],
    ['bad bundle root (file:)', () => ({ load: createArtifactLoader({ bundleUrl: () => 'file:///C:/x/', fetch: fakeFetch(files).fn }) }), 'LOAD_FAILED'],
  ];
  for (const [name, make, code] of cases) await assert.rejects(make().load(REQ.scene, new AbortController().signal), isCode(code), name);
});

test('abort during fetch rejects with AbortError and adapter stays silent', async () => {
  const { files } = await fixtureFiles();
  const { load } = loader(files, { hang: true });
  const ac = new AbortController(); const states = []; const errors = [];
  const adapter = createViewerAdapter({ createRenderer: () => { throw new Error('must not render'); } });
  const p = adapter.mount({}, REQ, { loadScene: load, signal: ac.signal, onState: (s) => states.push(s), onError: (e) => errors.push(e) });
  await new Promise((r) => setTimeout(r, 5)); ac.abort();
  await assert.rejects(p, (e) => e.name === 'AbortError');
  assert.deepEqual(states, ['loading']); assert.deepEqual(errors, []);
});
