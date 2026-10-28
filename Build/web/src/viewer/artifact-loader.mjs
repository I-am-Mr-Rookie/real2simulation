// Validating scene-artifact loader (S09c): implements the shell's loadScene(sceneRef, signal)
// for real point-cloud/splat bundles served from a transport-resolved bundle root.
// Fail-closed before parsing: path allowlist, kind/format pairing, declared size + point limits,
// streamed byte caps, exact byte length and SHA-256 (rechecked again by buildSceneModel).
// The full scene-v1 schema stays in contracts/scene (Python); this is the client-side gate only.
import { ViewerError } from './common.mjs';

export const DEFAULT_LIMITS = Object.freeze({ manifestBytes: 256 * 1024, assetBytes: 64 * 1024 * 1024, points: 2_000_000 });
// Same pattern as contracts/scene/scene.schema.json asset.path.
const PATH_RE = /^(?!.*\.\.)(?:[A-Za-z0-9_-]+\/)*[A-Za-z0-9_-]+\.(ply|glb|splat)$/;
const FORMAT_EXT = { 'ply-ascii-xyzrgb': 'ply', glb: 'glb', splat: 'splat' };
const KIND_FORMAT = { points: 'ply-ascii-xyzrgb', splats: 'splat', mesh: 'glb' };
const LOADABLE_KINDS = new Set(['points', 'splats']); // mesh/GLB: later S09 run
const ID_RE = /^[a-z0-9][a-z0-9-]{0,63}$/;
const SHA_RE = /^[a-f0-9]{64}$/;

const bad = (msg) => { throw new ViewerError('INVALID_ARTIFACT', msg); };
const loadFail = (msg) => { throw new ViewerError('LOAD_FAILED', msg); };
const isInt = (n) => Number.isSafeInteger(n);

async function sha256Hex(bytes) {
  const d = new Uint8Array(await globalThis.crypto.subtle.digest('SHA-256', bytes));
  return Array.from(d, (b) => b.toString(16).padStart(2, '0')).join('');
}

/** Read a response body with a hard byte cap (Content-Length precheck + streamed count). */
export async function readCapped(res, max, what) {
  if (!res || !res.ok) loadFail(what + ' could not be fetched');
  const len = res.headers?.get?.('content-length');
  if (len != null && len !== '' && !(Number(len) <= max)) bad(what + ' exceeds size limit');
  if (!res.body?.getReader) {
    const buf = new Uint8Array(await res.arrayBuffer());
    if (buf.byteLength > max) bad(what + ' exceeds size limit');
    return buf;
  }
  const reader = res.body.getReader();
  const chunks = []; let total = 0;
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    total += value.byteLength;
    if (total > max) { try { await reader.cancel(); } catch { /* ignore */ } bad(what + ' exceeds size limit'); }
    chunks.push(value);
  }
  const out = new Uint8Array(total); let o = 0;
  for (const c of chunks) { out.set(c, o); o += c.byteLength; }
  return out;
}

/** Client-side manifest gate. Returns the render asset entry. Throws ViewerError. */
export function checkManifest(m, sceneRef, limits = DEFAULT_LIMITS) {
  if (!m || typeof m !== 'object' || Array.isArray(m)) bad('manifest must be an object');
  if (m.schema_version !== '1.0.0' || m.schema_version !== sceneRef.scene_version) bad('scene schema version mismatch');
  if (m.id !== sceneRef.scene_id) bad('scene id does not match the request');
  if (typeof m.synthetic !== 'boolean' || m.synthetic !== (sceneRef.evidence === 'synthetic')) bad('scene evidence label does not match the request');
  if (!Array.isArray(m.assets) || m.assets.length < 1) bad('manifest has no assets');
  const byId = new Map();
  for (const a of m.assets) {
    if (!a || typeof a.id !== 'string' || !ID_RE.test(a.id) || byId.has(a.id)) bad('asset ids must be unique and valid');
    if (typeof a.path !== 'string' || !PATH_RE.test(a.path)) bad('asset path not allowlisted');
    if (!Object.hasOwn(FORMAT_EXT, a.format) || !a.path.endsWith('.' + FORMAT_EXT[a.format])) bad('asset format/extension mismatch');
    if (!isInt(a.bytes) || a.bytes < 1 || a.bytes > limits.assetBytes) bad('asset size missing or over limit');
    if (typeof a.sha256 !== 'string' || !SHA_RE.test(a.sha256)) bad('asset sha256 invalid');
    byId.set(a.id, a);
  }
  const r = m.render;
  if (!r || !Object.hasOwn(KIND_FORMAT, r.kind)) bad('render kind invalid');
  const main = byId.get(r.asset_id); const mobile = byId.get(r.mobile_asset_id);
  if (!main || !mobile) bad('render asset missing');
  if (main.format !== KIND_FORMAT[r.kind] || mobile.format !== KIND_FORMAT[r.kind]) bad('render asset format does not match render kind');
  if (!LOADABLE_KINDS.has(r.kind)) throw new ViewerError('UNSUPPORTED', 'render kind not supported by this viewer yet');
  if (!isInt(r.point_count) || r.point_count < 1) bad('point_count invalid');
  if (r.point_count > limits.points) bad('point_count over viewer limit');
  if (r.kind === 'splats' && main.bytes !== 32 * r.point_count) bad('splat count/size mismatch');
  return main;
}

/**
 * @param {{ bundleUrl(sceneRef): string|URL, fetch?: typeof fetch, limits?: Partial<typeof DEFAULT_LIMITS>, init?: RequestInit }} opts
 * bundleUrl returns the transport-resolved bundle root (directory URL containing scene.json).
 * Only the main render asset is fetched (mobile LOD is a later S09 run).
 */
export function createArtifactLoader({ bundleUrl, fetch: fetchImpl = globalThis.fetch, limits = {}, init = {} } = {}) {
  if (typeof bundleUrl !== 'function') throw new TypeError('bundleUrl is required');
  if (typeof fetchImpl !== 'function') throw new TypeError('fetch is required');
  const L = Object.freeze({ ...DEFAULT_LIMITS, ...limits });
  return async function loadScene(sceneRef, signal) {
    let root;
    try { root = new URL(String(bundleUrl(sceneRef))); } catch { loadFail('bundle root unavailable'); }
    if (!['https:', 'http:'].includes(root.protocol) || root.search || root.hash || !root.pathname.endsWith('/')) loadFail('bundle root invalid');
    const opts = { ...init, signal, redirect: 'error' };
    const get = async (rel, max, what) => {
      const u = new URL(rel, root);
      if (u.origin !== root.origin || !u.pathname.startsWith(root.pathname)) bad(what + ' escapes bundle root');
      let res;
      try { res = await fetchImpl(u.href, opts); } catch (e) { if (signal?.aborted) throw e; loadFail(what + ' could not be fetched'); }
      return readCapped(res, max, what);
    };
    const mBytes = await get('scene.json', L.manifestBytes, 'manifest');
    let manifest;
    try { manifest = JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(mBytes)); } catch { bad('manifest is not valid JSON'); }
    const asset = checkManifest(manifest, sceneRef, L);
    const bytes = await get(asset.path, asset.bytes, 'render asset');
    if (bytes.byteLength !== asset.bytes) bad('render asset byte length mismatch');
    if ((await sha256Hex(bytes)) !== asset.sha256) bad('render asset sha256 mismatch');
    return { manifest, assets: { [asset.id]: bytes } };
  };
}
