// S13h: load the live RM04 bundle through the viewer's own scene model (Build/web/src/viewer, unedited).
// node evidence/S13/S13h/viewer_check.mjs <bundle_dir>
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { buildSceneModel } from '../../../Build/web/src/viewer/scene-model.mjs';

const dir = process.argv[2];
const t0 = performance.now();
const manifest = JSON.parse(readFileSync(join(dir, 'scene.json'), 'utf8'));
const assets = Object.fromEntries(manifest.assets.map((a) => [a.id, new Uint8Array(readFileSync(join(dir, a.path)))]));
const ref = { scene_id: manifest.id, scene_version: manifest.schema_version, evidence: manifest.synthetic ? 'synthetic' : 'real' };
const m = await buildSceneModel({ manifest, assets }, ref);
console.log(JSON.stringify({ viewer_model: 'ok', sceneId: m.sceneId, kind: m.render.kind, points: m.render.positions.length / 3,
  banner: m.banner, gateEvidence: m.gateEvidence, ms: Math.round(performance.now() - t0) }));
