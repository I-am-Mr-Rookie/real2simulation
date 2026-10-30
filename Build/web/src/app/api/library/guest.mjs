// S04j: serve S18k guest projection read-only. Calls Build/library/guest.py load_guest itself (single source of
// truth: custody/sha/size/answer-withholding), so no validation logic is duplicated in JS.
// shortcut: needs python + fastapi + repo files at runtime; S15k must stage them (see evidence/S04j/STAGING.md).
import { execFile } from 'node:child_process';
import { createHash } from 'node:crypto';
import path from 'node:path';

export const ROOT = process.env.R2S_REPO_ROOT || path.resolve(process.cwd(), '../..');
const ID = /^[a-f0-9]{64}$/, ARTIFACT_BYTES = 262144;
const SCRIPT = 'import base64,json,sys;from Build.library.guest import load_guest;m,o=load_guest();' +
  'sys.stdout.write(json.dumps({"manifest":m,"objects":{k:base64.b64encode(v).decode() for k,v in o.items()}}))';
const json = (status, body, cache = 'no-store') => Response.json(body, { status,
  headers: { 'cache-control': cache, 'x-content-type-options': 'nosniff' } });
const error = (status, code) => json(status, { status: 'error', error: { code } });

// No caching of authority: revocation/corruption must affect the next request (guest.py contract).
export function loadGuest(root = ROOT) {
  return new Promise((resolve, reject) => execFile(process.env.R2S_PYTHON || 'python', ['-c', SCRIPT],
    { cwd: root, timeout: 20000, maxBuffer: 4 << 20, windowsHide: true },
    (err, stdout) => { if (err) return reject(err); try { resolve(JSON.parse(stdout)); } catch (e) { reject(e); } }));
}

export async function manifestResponse(root) {
  try { return json(200, (await loadGuest(root)).manifest, 'no-cache'); }
  catch { return error(503, 'library_unavailable'); }
}

export async function artifactResponse(id, root) {
  if (typeof id !== 'string' || !ID.test(id)) return error(400, 'invalid_artifact_id');
  let objects;
  try { ({ objects } = await loadGuest(root)); } catch { return error(503, 'library_unavailable'); }
  if (!Object.hasOwn(objects, id)) return error(404, 'artifact_not_found');
  const data = Buffer.from(objects[id], 'base64');
  if (data.length > ARTIFACT_BYTES || createHash('sha256').update(data).digest('hex') !== id) {
    return error(503, 'artifact_unavailable');
  }
  return new Response(data, { headers: { 'content-type': 'application/json',
    'cache-control': 'public, max-age=31536000, immutable', etag: `"${id}"`, 'x-content-type-options': 'nosniff' } });
}
