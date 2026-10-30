// S04k: serve the S18k guest projection from an immutable snapshot that infra/railway/dev/stage.py writes at staging
// time by running Build/library/guest.py load_guest() (single source of truth for custody/answer-withholding).
// The web image has no Python, so production never spawns it; local dev without a snapshot falls back to live python.
import { execFile } from 'node:child_process';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import path from 'node:path';

export const ROOT = process.env.R2S_REPO_ROOT || path.resolve(process.cwd(), '../..');
export const SNAPSHOT = process.env.R2S_GUEST_SNAPSHOT || path.resolve(process.cwd(), 'library-snapshot/guest.json');
// Same one-liner as stage.py GUEST: emits {"manifest", "objects": {sha256: base64}}.
export const GUEST_SCRIPT = 'import base64,json,sys;from Build.library.guest import load_guest;m,o=load_guest();' +
  'sys.stdout.write(json.dumps({"manifest":m,"objects":{k:base64.b64encode(v).decode() for k,v in o.items()}}))';
const ID = /^[a-f0-9]{64}$/, ARTIFACT_BYTES = 262144, SNAPSHOT_BYTES = 4 << 20;
const sha = (data) => createHash('sha256').update(data).digest('hex');
const json = (status, body, headers = { 'cache-control': 'no-store' }) => Response.json(body, { status,
  headers: { ...headers, 'x-content-type-options': 'nosniff' } });
const error = (status, code) => json(status, { status: 'error', error: { code } });
const fail = (why) => { throw new Error('guest snapshot rejected: ' + why); };
const cache = new Map();

// Rejects anything but sha-addressed, size-bounded objects that every manifest artifact resolves to.
export function verifySnapshot(snap) {
  const { manifest, objects } = snap ?? {};
  if (!Array.isArray(manifest?.demos) || !objects || typeof objects !== 'object') fail('shape');
  const bytes = new Map();
  for (const [id, b64] of Object.entries(objects)) {
    if (!ID.test(id) || typeof b64 !== 'string') fail('object id');
    const data = Buffer.from(b64, 'base64');
    if (data.length > ARTIFACT_BYTES || sha(data) !== id) fail('object bytes');
    bytes.set(id, data);
  }
  for (const d of manifest.demos) if (d.artifact && !bytes.has(d.artifact.sha256)) fail('missing object');
  return { manifest, objects: bytes, etag: `"${sha(JSON.stringify(manifest))}"` };
}

async function readSnapshot(file) {
  const raw = await readFile(file);
  if (raw.length > SNAPSHOT_BYTES) fail('size');
  return verifySnapshot(JSON.parse(raw.toString('utf8')));
}

function spawnGuest(root) {
  return new Promise((resolve, reject) => execFile(process.env.R2S_PYTHON || 'python', ['-B', '-c', GUEST_SCRIPT],
    { cwd: root, timeout: 20000, maxBuffer: SNAPSHOT_BYTES, windowsHide: true },
    (err, stdout) => { if (err) return reject(err); try { resolve(verifySnapshot(JSON.parse(stdout))); } catch (e) { reject(e); } }));
}

// Snapshot is immutable per deployment: verify once per process (R-L P3), keep failures sticky (fail closed).
export async function loadGuest(file = SNAPSHOT, root = ROOT) {
  if (!cache.has(file)) cache.set(file, readSnapshot(file));
  try { return await cache.get(file); } catch (e) {
    if (e?.code !== 'ENOENT' || process.env.NODE_ENV === 'production') throw e;
    cache.delete(file); // local dev only: no staged snapshot -> live projection (needs python + fastapi), never cached
    return spawnGuest(root);
  }
}

export async function manifestResponse(file, root) {
  try {
    const { manifest, etag } = await loadGuest(file, root);
    return json(200, manifest, { 'cache-control': 'no-cache', etag });
  } catch { return error(503, 'library_unavailable'); }
}

export async function artifactResponse(id, file, root) {
  if (typeof id !== 'string' || !ID.test(id)) return error(400, 'invalid_artifact_id');
  let objects;
  try { ({ objects } = await loadGuest(file, root)); } catch { return error(503, 'library_unavailable'); }
  const data = objects.get(id);
  if (!data) return error(404, 'artifact_not_found');
  if (data.length > ARTIFACT_BYTES || sha(data) !== id) return error(503, 'artifact_unavailable'); // recheck on read
  return new Response(data, { headers: { 'content-type': 'application/json',
    'cache-control': 'public, max-age=31536000, immutable', etag: `"${id}"`, 'x-content-type-options': 'nosniff' } });
}
