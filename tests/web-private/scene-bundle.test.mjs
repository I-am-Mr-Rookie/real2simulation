// S13m: PrivateWorkspace hands the viewer a real loadScene that fetches the owner-scoped API bundle through the BFF.
import assert from 'node:assert/strict';
import test from 'node:test';
import { readFile } from 'node:fs/promises';

test('PrivateWorkspace passes loadScene; it fetches /api/workspace/scenes/<job>/bundle/scene.json', async () => {
  const seen = [];
  globalThis.location ??= { origin: 'http://localhost' };
  const fetch0 = globalThis.fetch;
  globalThis.fetch = async (url) => { seen.push(url); return new Response('{}', { status: 503 }); };
  try {
    const { loadScene, SCENE_LABEL } = await import('../../Build/web/src/shell/PrivateWorkspace.mjs');
    await assert.rejects(loadScene({ scene_id: 'job_' + '0'.repeat(32), scene_version: '1.0.0', evidence: 'reconstructed' }));
    assert.equal(new URL(seen[0]).pathname, '/api/workspace/scenes/job_' + '0'.repeat(32) + '/bundle/scene.json');
    assert.match(SCENE_LABEL, /Display only, scale unverified, not a measurement/);
  } finally { globalThis.fetch = fetch0; }
  const src = await readFile(new URL('../../Build/web/src/shell/PrivateWorkspace.mjs', import.meta.url), 'utf8');
  assert.match(src, /createElement\(Workspace, \{ state: s\.state, adapter, loadScene,/);
});
