// S13m: the real viewer loader accepts the API-served RM04 bundle (scene.json id re-bound to the job, as jobs.py serves it).
import { readFile } from 'node:fs/promises';
import { createArtifactLoader } from '../../Build/web/src/viewer/artifact-loader.mjs';
const dir = new URL('../S13l/reconstruct/bundle/', import.meta.url), job = 'job_' + 'a'.repeat(32);
const fetch = async (u) => {
  const name = new URL(u).pathname.split('/').pop(); let b = await readFile(new URL(name, dir));
  if (name === 'scene.json') b = Buffer.from(JSON.stringify({ ...JSON.parse(b), id: job }));
  return new Response(b, { status: 200 });
};
const load = createArtifactLoader({ bundleUrl: (s) => `http://localhost/api/workspace/scenes/${s.scene_id}/bundle/`, fetch });
const r = await load({ scene_id: job, scene_version: '1.0.0', access: 'private', evidence: 'reconstructed' });
console.log(JSON.stringify({ ok: true, id: r.manifest.id, point_count: r.manifest.render.point_count, assets: Object.keys(r.assets) }));
