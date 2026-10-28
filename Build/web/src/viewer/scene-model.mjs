// ValidatedSceneBundle -> immutable, renderer-independent scene model (S09a).
// Bundle = { manifest: scene-v1 JSON (already validated by contracts/scene), assets: { [assetId]: Uint8Array } }.
// Runs once per mount (never per frame). Re-checks the identity/integrity facts the viewer relies on.
import { ViewerError, deepFreeze } from './common.mjs';
import { SYNTHETIC_BANNER } from './fixture.mjs';

const SUPPORTED_RENDER_KINDS = new Set(['points', 'splats']); // mesh: later S09 run
const KIND_FORMAT = { points: 'ply-ascii-xyzrgb', splats: 'splat' };
const QUAT_TOL = 0.05; // uint8 quaternion quantisation ((b-128)/128) cannot meet the 1e-5 float tolerance
const PLY_PROPS = ['float x', 'float y', 'float z', 'uchar red', 'uchar green', 'uchar blue'];
const bad = (msg) => { throw new ViewerError('INVALID_ARTIFACT', msg); };

async function sha256Hex(bytes) {
  const d = new Uint8Array(await globalThis.crypto.subtle.digest('SHA-256', bytes));
  return Array.from(d, (b) => b.toString(16).padStart(2, '0')).join('');
}

/** Strict PLY ASCII 1.0 vertex-only x/y/z float + r/g/b uchar decoder (scene-v1 points format). */
export function decodePlyXyzRgb(bytes, expectedCount) {
  for (const b of bytes) if (b > 0x7e || (b < 0x20 && b !== 0x0a && b !== 0x0d && b !== 0x09)) bad('PLY is not plain ASCII');
  const lines = new TextDecoder('utf-8').decode(bytes).split(/\r?\n/);
  let i = 0;
  const next = () => (i < lines.length ? lines[i++].trim() : bad('PLY header truncated'));
  if (next() !== 'ply' || next() !== 'format ascii 1.0') bad('PLY must be format ascii 1.0');
  let line = next();
  while (line.startsWith('comment ')) line = next();
  const m = /^element vertex (\d+)$/.exec(line);
  if (!m) bad('PLY must declare element vertex first');
  const count = Number(m[1]);
  if (count !== expectedCount) bad('PLY vertex count does not match point_count');
  for (const p of PLY_PROPS) if (next() !== 'property ' + p) bad('PLY properties must be x y z red green blue');
  if (next() !== 'end_header') bad('PLY must be vertex-only');
  const positions = new Float32Array(count * 3);
  const colors = new Uint8Array(count * 3);
  for (let v = 0; v < count; v++) {
    const t = next().split(/\s+/);
    if (t.length !== 6) bad('PLY vertex row must have 6 values');
    for (let k = 0; k < 3; k++) {
      const x = Number(t[k]);
      if (!Number.isFinite(x)) bad('PLY coordinate not finite');
      positions[v * 3 + k] = x;
      const c = Number(t[k + 3]);
      if (!Number.isInteger(c) || c < 0 || c > 255) bad('PLY colour out of range');
      colors[v * 3 + k] = c;
    }
  }
  while (i < lines.length) if (lines[i++].trim() !== '') bad('PLY has trailing data');
  return { positions, colors, count };
}

/**
 * Strict scene-v1 splat decoder: 32-byte LE records = position f32[3], scale f32[3], RGBA u8[4],
 * quaternion u8[4] wxyz decoded (b-128)/128. Validates finite positions, finite non-negative scales,
 * near-unit quaternions. Renderers without a Gaussian rasteriser draw centres as points.
 */
export function decodeSplats(bytes, expectedCount) {
  if (!Number.isSafeInteger(expectedCount) || expectedCount < 1) bad('splat point_count invalid');
  if (bytes.byteLength !== expectedCount * 32) bad('splat byte length must be point_count x 32');
  const n = expectedCount;
  const dv = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  const positions = new Float32Array(n * 3); const scales = new Float32Array(n * 3);
  const colors = new Uint8Array(n * 3); const opacity = new Uint8Array(n); const rotations = new Float32Array(n * 4);
  for (let i = 0; i < n; i++) {
    const o = i * 32;
    for (let k = 0; k < 3; k++) {
      const p = dv.getFloat32(o + k * 4, true); const s = dv.getFloat32(o + 12 + k * 4, true);
      if (!Number.isFinite(p)) bad('splat position not finite');
      if (!Number.isFinite(s) || s < 0) bad('splat scale invalid');
      positions[i * 3 + k] = p; scales[i * 3 + k] = s;
      colors[i * 3 + k] = bytes[o + 24 + k];
    }
    opacity[i] = bytes[o + 27];
    let q2 = 0;
    for (let k = 0; k < 4; k++) { const q = (bytes[o + 28 + k] - 128) / 128; rotations[i * 4 + k] = q; q2 += q * q; }
    if (Math.abs(Math.sqrt(q2) - 1) > QUAT_TOL) bad('splat quaternion not unit');
  }
  return { positions, colors, count: n, splat: { scales, opacity, rotations } };
}

export async function buildSceneModel(bundle, sceneRef) {
  const m = bundle?.manifest;
  const assets = bundle?.assets;
  if (!m || typeof m !== 'object' || !assets || typeof assets !== 'object') bad('bundle needs manifest and assets');
  if (m.schema_version !== sceneRef.scene_version) bad('scene schema version mismatch');
  if (m.id !== sceneRef.scene_id) bad('scene id does not match the request');
  if (m.synthetic !== (sceneRef.evidence === 'synthetic')) bad('scene evidence label does not match the request');
  if (!SUPPORTED_RENDER_KINDS.has(m.render?.kind)) throw new ViewerError('UNSUPPORTED', 'render kind not supported by this viewer yet');
  const asset = Array.isArray(m.assets) ? m.assets.find((a) => a.id === m.render.asset_id) : undefined;
  if (!asset || asset.format !== KIND_FORMAT[m.render.kind]) bad('render asset missing or wrong format');
  const bytes = Object.hasOwn(assets, asset.id) ? assets[asset.id] : undefined;
  if (!(bytes instanceof Uint8Array)) bad('render asset bytes missing');
  if (bytes.byteLength !== asset.bytes) bad('render asset byte length mismatch');
  if ((await sha256Hex(bytes)) !== asset.sha256) bad('render asset sha256 mismatch');
  const sourceKind = m.render.kind;
  const points = sourceKind === 'splats' ? decodeSplats(bytes, m.render.point_count) : decodePlyXyzRgb(bytes, m.render.point_count);
  const copy = (v) => structuredClone(v ?? []);
  return deepFreeze({
    sceneId: m.id,
    label: String(m.label), // plain text only; renderers must use textContent, never HTML
    synthetic: m.synthetic === true,
    banner: m.synthetic === true ? SYNTHETIC_BANNER : null,
    gateEvidence: false, // viewer output is never gate evidence by itself
    physicsEnabled: false, // viewer never enables physics; S10 owns that decision
    coordinates: copy(m.coordinates),
    scale: copy(m.scale),
    gravity: copy(m.gravity), // preserved as-is (may be unknown); not for display in mystery mode
    boundsM: copy(m.bounds_m),
    // kind stays 'points' (what the renderer draws); sourceKind records the artifact type.
    render: { kind: 'points', sourceKind, assetId: asset.id, mobileAssetId: m.render.mobile_asset_id, ...points },
    surfaces: copy(m.surfaces),
    colliders: copy(m.colliders),
    cameraPath: copy(m.camera_path),
    labels: copy(m.labels).map((l) => ({ ...l, text: String(l.text) })),
  });
}
