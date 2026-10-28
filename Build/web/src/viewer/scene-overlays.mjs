// S09d: renderer-independent overlay maths for scene-v1 colliders, camera_path and labels.
// Pure functions (no THREE, no DOM) so alignment and path sampling are deterministic and testable.
// Report output is a geometric consistency check of the manifest, never measured/simulated or gate evidence.

const finite3 = (v) => Array.isArray(v) && v.length === 3 && v.every(Number.isFinite);
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const QUAT_NORM_TOL = 1e-3;

/** Normalise an xyzw quaternion; throws if non-finite or not near unit length. */
export function unitQuat(q) {
  if (!Array.isArray(q) || q.length !== 4 || !q.every(Number.isFinite)) throw new Error('quaternion invalid');
  const n = Math.hypot(...q);
  if (Math.abs(n - 1) > QUAT_NORM_TOL) throw new Error('quaternion not unit');
  return q.map((c) => c / n);
}

/** Rotate v by unit quaternion q (xyzw). */
export function rotate([x, y, z, w], v) {
  const tx = 2 * (y * v[2] - z * v[1]), ty = 2 * (z * v[0] - x * v[2]), tz = 2 * (x * v[1] - y * v[0]);
  return [v[0] + w * tx + (y * tz - z * ty), v[1] + w * ty + (z * tx - x * tz), v[2] + w * tz + (x * ty - y * tx)];
}

function boxFrame(c) {
  const p = c?.pose?.position_m, h = c?.half_extents_m;
  if (c?.shape !== 'box' || !finite3(p) || !finite3(h) || !h.every((v) => v > 0)) throw new Error('collider invalid');
  const q = unitQuat(c.pose.rotation_xyzw);
  return { p, h, axes: [[1, 0, 0], [0, 1, 0], [0, 0, 1]].map((a) => rotate(q, a)) };
}

/** 8 world-space corners; corner i has sign bits x=bit0, y=bit1, z=bit2. */
export function boxCorners(collider) {
  const { p, h, axes } = boxFrame(collider);
  return Array.from({ length: 8 }, (_, i) => {
    const s = [i & 1 ? 1 : -1, i & 2 ? 1 : -1, i & 4 ? 1 : -1];
    return [0, 1, 2].map((k) => p[k] + s[0] * h[0] * axes[0][k] + s[1] * h[1] * axes[1][k] + s[2] * h[2] * axes[2][k]);
  });
}

/** LineSegments positions for all box colliders: 12 edges x 2 vertices x 3 floats each. */
export function colliderEdgePositions(colliders) {
  const list = Array.isArray(colliders) ? colliders : [];
  const out = new Float32Array(list.length * 72);
  let o = 0;
  for (const c of list) {
    const k = boxCorners(c);
    for (let i = 0; i < 8; i++) for (const bit of [1, 2, 4]) if (!(i & bit)) { out.set(k[i], o); out.set(k[i | bit], o + 3); o += 6; }
  }
  return out;
}

/**
 * Geometric consistency of a scene model: each collider with surface_id must touch its surface plane
 * (support along the surface normal = 0) and contain the surface origin in its footprint; colliders and labels
 * must lie inside bounds_m. pointsOnFace counts render points lying on the collider's surface face.
 */
export function overlayAlignment(model, { tolM = 1e-3, positions = model?.render?.positions } = {}) {
  const issues = [];
  const { min, max } = model?.boundsM ?? {};
  const inBounds = (v) => finite3(min) && finite3(max) && v.every((x, i) => x >= min[i] - tolM && x <= max[i] + tolM);
  const surfaces = new Map((model?.surfaces ?? []).map((s) => [s.id, s]));
  const colliders = [];
  for (const c of model?.colliders ?? []) {
    let f;
    try { f = boxFrame(c); } catch (e) { issues.push(c?.id + ': ' + e.message); continue; }
    const rec = { id: c.id, surfaceId: c.surface_id ?? null, faceGapM: null, pointsOnFace: 0 };
    if (!boxCorners(c).every(inBounds)) issues.push(c.id + ': outside bounds_m');
    if (c.surface_id != null) {
      const s = surfaces.get(c.surface_id);
      if (!s || !finite3(s.normal) || !finite3(s.origin_m)) { issues.push(c.id + ': surface ' + c.surface_id + ' missing'); colliders.push(rec); continue; }
      const nl = Math.hypot(...s.normal); const n = s.normal.map((v) => v / nl);
      const support = dot(f.p.map((v, i) => v - s.origin_m[i]), n) + f.axes.reduce((a, ax, k) => a + Math.abs(dot(ax, n)) * f.h[k], 0);
      rec.faceGapM = support;
      if (Math.abs(support) > tolM) issues.push(c.id + ': face is ' + support.toFixed(4) + ' m from surface ' + s.id);
      const local = f.axes.map((ax) => dot(s.origin_m.map((v, i) => v - f.p[i]), ax));
      if (local.some((v, k) => Math.abs(v) > f.h[k] + tolM)) issues.push(c.id + ': surface origin outside collider');
      if (positions) {
        for (let i = 0; i + 2 < positions.length; i += 3) {
          const pt = [positions[i], positions[i + 1], positions[i + 2]];
          const d = pt.map((v, k) => v - f.p[k]);
          if (Math.abs(dot(pt.map((v, k) => v - s.origin_m[k]), n)) <= tolM && f.axes.every((ax, k) => Math.abs(dot(d, ax)) <= f.h[k] + tolM)) rec.pointsOnFace++;
        }
      }
    }
    colliders.push(rec);
  }
  const labels = (model?.labels ?? []).map((l) => {
    const ok = finite3(l?.position_m) && inBounds(l.position_m);
    if (!ok) issues.push('label ' + l?.id + ': position invalid or outside bounds_m');
    return { id: l?.id, ok };
  });
  return { ok: issues.length === 0, issues, colliders, labels };
}

function slerp(a, b, t) {
  let d = a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3];
  const bb = d < 0 ? b.map((v) => -v) : b; d = Math.abs(d);
  if (d > 0.9995) { const r = a.map((v, i) => v + (bb[i] - v) * t); const n = Math.hypot(...r); return r.map((v) => v / n); }
  const th = Math.acos(Math.min(1, d)), s = Math.sin(th);
  const wa = Math.sin((1 - t) * th) / s, wb = Math.sin(t * th) / s;
  return a.map((v, i) => wa * v + wb * bb[i]);
}

/** Validate camera_path once: strictly increasing finite times, finite poses, unit quats, 0<fov<180. */
export function prepareCameraPath(path) {
  if (!Array.isArray(path) || path.length < 1) throw new Error('camera_path empty');
  let prev = -Infinity;
  return Object.freeze(path.map((k) => {
    if (!Number.isFinite(k?.time_s) || k.time_s < 0 || k.time_s <= prev) throw new Error('camera_path times must be finite and strictly increasing');
    prev = k.time_s;
    if (!finite3(k.pose?.position_m)) throw new Error('camera_path position invalid');
    if (!(k.vertical_fov_deg > 0 && k.vertical_fov_deg < 180)) throw new Error('camera_path fov invalid');
    return Object.freeze({ t: k.time_s, position: [...k.pose.position_m], quaternion: unitQuat(k.pose.rotation_xyzw), fov: k.vertical_fov_deg });
  }));
}

/** Pose at time t (seconds, clamped to the path): lerp position/fov, slerp rotation. */
export function sampleCameraPath(keys, t) {
  const time = Number.isFinite(t) ? t : keys[0].t;
  if (time <= keys[0].t) return { ...keys[0], t: keys[0].t };
  const last = keys[keys.length - 1];
  if (time >= last.t) return { ...last, t: last.t };
  let i = 1; while (keys[i].t < time) i++;
  const a = keys[i - 1], b = keys[i], u = (time - a.t) / (b.t - a.t);
  return { t: time, position: a.position.map((v, k) => v + (b.position[k] - v) * u), quaternion: slerp(a.quaternion, b.quaternion, u), fov: a.fov + (b.fov - a.fov) * u };
}

/** NDC (x,y,z in [-1,1]) -> CSS pixel position in a w x h viewport; null when clipped/behind camera. */
export function ndcToScreen([x, y, z], w, h) {
  if (![x, y, z].every(Number.isFinite) || z < -1 || z > 1 || Math.abs(x) > 1 || Math.abs(y) > 1) return null;
  return [((x + 1) / 2) * w, ((1 - y) / 2) * h];
}
