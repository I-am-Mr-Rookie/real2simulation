// S10a: validated synthetic apparatus placement. No renderer or physics defaults.
const validated = new WeakSet();
const finite = (n) => typeof n === 'number' && Number.isFinite(n);
const vec3 = (v) => Array.isArray(v) && v.length === 3 && v.every(finite);
const fail = (message) => { throw new TypeError(`INVALID_APPARATUS: ${message}`); };

function validateSnapshot(raw) {
  if (!raw || typeof raw !== 'object' || raw.schema_version !== '1.0.0' || typeof raw.scene_id !== 'string') fail('snapshot schema');
  const b = raw.bounds_m;
  if (!b || !vec3(b.min) || !vec3(b.max) || b.min.some((x, i) => x >= b.max[i])) fail('snapshot bounds');
  if (!Array.isArray(raw.surfaces) || raw.surfaces.some((s) => !s || typeof s.id !== 'string' || !vec3(s.normal) || !finite(s.offset) || Math.abs(Math.hypot(...s.normal) - 1) > 1e-6)) fail('snapshot surfaces');
  const copy = structuredClone({ schema_version: raw.schema_version, scene_id: raw.scene_id, bounds_m: raw.bounds_m, surfaces: raw.surfaces });
  Object.freeze(copy.bounds_m.min); Object.freeze(copy.bounds_m.max); Object.freeze(copy.bounds_m);
  copy.surfaces.forEach((s) => { Object.freeze(s.normal); Object.freeze(s); }); Object.freeze(copy.surfaces); Object.freeze(copy);
  validated.add(copy); return copy;
}

const quatRotate = (q, v) => {
  const [x, y, z, w] = q, [vx, vy, vz] = v;
  const tx = 2 * (y * vz - z * vy), ty = 2 * (z * vx - x * vz), tz = 2 * (x * vy - y * vx);
  return [vx + w * tx + y * tz - z * ty, vy + w * ty + z * tx - x * tz, vz + w * tz + x * ty - y * tx];
};
const add = (a, b) => a.map((v, i) => v + b[i]);
const dot = (a, b) => a.reduce((s, v, i) => s + v * b[i], 0);

export function validatePlacementSnapshot(raw) { return validateSnapshot(raw); }

export function placeApparatus(snapshot, apparatus) {
  if (!validated.has(snapshot)) fail('snapshot must be a validated snapshot returned by validatePlacementSnapshot');
  if (!apparatus || apparatus.shape !== 'box' || typeof apparatus.id !== 'string') fail('apparatus schema');
  const p = apparatus.pose, e = apparatus.half_extents_m;
  if (!p || !vec3(p.position_m) || !Array.isArray(p.rotation_xyzw) || p.rotation_xyzw.length !== 4 || !p.rotation_xyzw.every(finite) || !vec3(e) || e.some((x) => x <= 0)) fail('apparatus dimensions or pose');
  const qn = Math.hypot(...p.rotation_xyzw); if (Math.abs(qn - 1) > 1e-6) fail('rotation must be unit');
  const surface = snapshot.surfaces.find((s) => s.id === apparatus.surface_id);
  if (!surface) fail('surface is not in validated snapshot');
  const corners = [-1, 1].flatMap(x => [-1, 1].flatMap(y => [-1, 1].map(z => [x * e[0], y * e[1], z * e[2]])));
  const rotated = corners.map((c) => quatRotate(p.rotation_xyzw, c));
  const support = Math.min(...rotated.map((c) => dot(surface.normal, add(p.position_m, c))));
  const shift = surface.offset - support;
  const position_m = add(p.position_m, surface.normal.map((n) => n * shift));
  const vertices = rotated.map((c) => add(position_m, c));
  const { min, max } = snapshot.bounds_m;
  if (vertices.some((v) => v.some((x, i) => x < min[i] - 1e-9 || x > max[i] + 1e-9))) fail('placed apparatus exceeds scene bounds');
  return Object.freeze({ id: apparatus.id, shape: 'box', surface_id: surface.id, pose: Object.freeze({ position_m: Object.freeze(position_m), rotation_xyzw: Object.freeze([...p.rotation_xyzw]) }), half_extents_m: Object.freeze([...e]), vertices: Object.freeze(vertices.map(Object.freeze)), synthetic: true });
}
