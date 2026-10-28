// Node-only test helper: resolves the S04a fixture mount to a ValidatedSceneBundle.
// Reads the single existing S05a fixture (no copy) and runs the S05a validator once.
import { readFile } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');

export async function loadFixtureMount(sceneId = 'synthetic-room-v1') {
  const mounts = JSON.parse(await readFile(path.join(ROOT, 'Build/web/src/shell/fixture-mounts.json'), 'utf8'));
  const mount = mounts.mounts.find((m) => m.scene_id === sceneId);
  if (!mount || mount.evidence !== 'synthetic' || mount.read_only !== true) throw new Error('fixture mount missing or not synthetic/read-only');
  return mount;
}

export async function loadFixtureBundle({ sceneId = 'synthetic-room-v1', validate = true } = {}) {
  const mount = await loadFixtureMount(sceneId);
  const manifestPath = path.join(ROOT, mount.repository_manifest);
  if (validate) execFileSync('python', [path.join(ROOT, 'contracts/scene/validate_scene.py'), manifestPath], { stdio: 'pipe' });
  const manifest = JSON.parse(await readFile(manifestPath, 'utf8'));
  const assets = {};
  for (const a of manifest.assets) assets[a.id] = new Uint8Array(await readFile(path.join(path.dirname(manifestPath), a.path)));
  return { manifest, assets };
}
