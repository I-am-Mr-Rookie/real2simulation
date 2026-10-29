// S09h: three real MapAnything scene bundles (RM02/RM04/RM05) through the existing loader + adapter.
// Media is gitignored (evidence/S09/local/<RM>/, built offline by Build/gpu/scene_job.py --npz, CPU only);
// absent media -> those tests skip, the in-memory banner test always runs. Not Gate R, physics or calibrated-scale evidence.
import test from 'node:test';
import assert from 'node:assert/strict';
import { existsSync } from 'node:fs';
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { createArtifactLoader } from '../../Build/web/src/viewer/artifact-loader.mjs';
import { createViewerAdapter, checkViewerRequest } from '../../Build/web/src/viewer/adapter.mjs';
import { buildSceneModel } from '../../Build/web/src/viewer/scene-model.mjs';
import { SCALE_UNVERIFIED_BANNER } from '../../Build/web/src/viewer/fixture.mjs';
import { ROOT, loadFixtureBundle } from './fixture-bundle.mjs';

const LOCAL = path.join(ROOT, 'evidence/S09/local');
const BASE = 'https://artifacts.test/scenes/';
const request = (id) => ({ contract_version: '1.0.0', kind: 'viewer', audience: 'guest', mode: 'inspect',
  scene: { scene_id: id, scene_version: '1.0.0', access: 'public-library', evidence: 'reconstructed' } });

// Read-only fake transport over the local bundle dir (same shape a static host would serve).
const fsFetch = (dir) => async (url) => {
  const rel = url.slice(BASE.length);
  if (!url.startsWith(BASE) || rel.includes('..')) return new Response('nope', { status: 404 });
  try { return new Response(await readFile(path.join(dir, rel)), { status: 200 }); } catch { return new Response('missing', { status: 404 }); }
};

for (const rm of ['RM02', 'RM04', 'RM05']) {
  const dir = path.join(LOCAL, rm);
  test(rm + ' real bundle loads through loader + adapter with scale-unverified banner', { skip: !existsSync(path.join(dir, 'scene.json')) && 'local media absent' }, async () => {
    const manifest = JSON.parse(await readFile(path.join(dir, 'scene.json'), 'utf8'));
    const req = request(manifest.id);
    assert.equal(checkViewerRequest(req), null);
    const loadScene = createArtifactLoader({ bundleUrl: () => BASE, fetch: fsFetch(dir) });
    let model; const states = []; const errors = [];
    const viewer = createViewerAdapter({ createRenderer: (h, m) => { model = m; return { dispose() {} }; } });
    const ac = new AbortController();
    const handle = await viewer.mount({}, req, { loadScene, signal: ac.signal, onState: (s) => states.push(s), onError: (e) => errors.push(e) });
    assert.deepEqual(states, ['loading', 'ready']); assert.deepEqual(errors, []);
    assert.equal(model.synthetic, false);
    assert.equal(model.banner, SCALE_UNVERIFIED_BANNER);
    assert.equal(model.scale.status, 'estimated');
    assert.equal(model.physicsEnabled, false); assert.equal(model.gateEvidence, false);
    assert.equal(model.render.count, manifest.render.point_count);
    const [lo, hi] = [manifest.bounds_m.min, manifest.bounds_m.max];
    for (let i = 0; i < model.render.count; i++) for (let k = 0; k < 3; k++) {
      const v = model.render.positions[i * 3 + k];
      assert.ok(Number.isFinite(v) && v >= lo[k] - 1e-3 && v <= hi[k] + 1e-3, 'point outside bounds_m');
    }
    handle.dispose();
  });
}

test('real (non-synthetic) scene without measured scale always carries the scale-unverified banner', async () => {
  const b = await loadFixtureBundle({ validate: false });
  const m = { ...structuredClone(b.manifest), synthetic: false, scale: { status: 'estimated', metres_per_source_unit: 1, evidence: 'test' } };
  const ref = request(m.id).scene;
  assert.equal((await buildSceneModel({ manifest: m, assets: b.assets }, ref)).banner, SCALE_UNVERIFIED_BANNER);
  m.scale = { status: 'unknown', metres_per_source_unit: null, evidence: 'test' };
  assert.equal((await buildSceneModel({ manifest: m, assets: b.assets }, ref)).banner, SCALE_UNVERIFIED_BANNER);
});
