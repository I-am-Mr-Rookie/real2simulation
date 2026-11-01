// lab-scene-v1: the editable lab scene JSON. The editor and the agent read and write this same shape.
export const SCENE_VERSION = 'lab-scene-v1';
export const MAX_OBJECTS = 50;
export const KINDS = ['ball', 'block', 'ramp', 'pendulum', 'spring'];
const ROOMS = ['none', 'plane', 'ply'];
const DEFAULTS = {
  ball: { size: [0.1, 0.1, 0.1], params: {} },
  block: { size: [0.2, 0.2, 0.2], params: {} },
  ramp: { size: [1.2, 0.05, 0.4], fixed: true, rotation: [0, 0, 0.2588190451, 0.9659258263], params: {} },
  pendulum: { size: [0.1, 0.1, 0.1], fixed: true, params: { length: 0.8, angle_deg: 30 } },
  spring: { size: [0.15, 0.15, 0.15], fixed: true, params: { rest_length: 0.4, stiffness: 40, damping: 0.2, stretch: 0.15 } },
};
const PARAM_KEYS = { ball: [], block: [], ramp: [], pendulum: ['length', 'angle_deg'], spring: ['rest_length', 'stiffness', 'damping', 'stretch'] };
const OBJECT_KEYS = new Set(['id', 'kind', 'position', 'rotation', 'size', 'velocity', 'mass', 'friction', 'restitution', 'fixed', 'sensor', 'params']);
const SCENE_KEYS = new Set(['version', 'label', 'units', 'gravity', 'room', 'objects']);

export class SceneError extends Error {}
const bad = (m) => { throw new SceneError(m); };
const num = (v, name, lo = -1e4, hi = 1e4) => (typeof v === 'number' && Number.isFinite(v) && v >= lo && v <= hi ? v : bad(name + ' must be a finite number in [' + lo + ', ' + hi + ']'));
const vec = (v, n, name, lo, hi) => (Array.isArray(v) && v.length === n ? v.map((x, i) => num(x, name + '[' + i + ']', lo, hi)) : bad(name + ' must be an array of ' + n + ' numbers'));

export function defaultScene() {
  return { version: SCENE_VERSION, label: 'SIMULATED', units: 'm', gravity: [0, -9.81, 0], room: { kind: 'plane', floor_y: 0 }, objects: [] };
}

export function makeObject(kind, scene, at = [0, 1, 0]) {
  if (!KINDS.includes(kind)) bad('unknown kind ' + kind);
  if (scene.objects.length >= MAX_OBJECTS) bad('at most ' + MAX_OBJECTS + ' objects');
  const used = new Set(scene.objects.map((o) => o.id));
  let n = 1; while (used.has(kind + '-' + n)) n += 1;
  const d = DEFAULTS[kind];
  return { id: kind + '-' + n, kind, position: [...at], rotation: [...(d.rotation ?? [0, 0, 0, 1])], size: [...d.size], velocity: [0, 0, 0],
    mass: 1, friction: 0.5, restitution: 0.3, fixed: d.fixed ?? false, sensor: kind !== 'ramp', params: { ...d.params } };
}

// Strict validation at the trust boundary (imported files and agent edits). Returns a normalized copy.
export function validateScene(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) bad('scene must be an object');
  for (const k of Object.keys(input)) if (!SCENE_KEYS.has(k)) bad('unknown scene field ' + k);
  if (input.version !== SCENE_VERSION) bad('version must be ' + SCENE_VERSION);
  if (input.label !== undefined && input.label !== 'SIMULATED') bad('label must be SIMULATED');
  if (input.units !== undefined && input.units !== 'm') bad('units must be m');
  const gravity = vec(input.gravity ?? [0, -9.81, 0], 3, 'gravity', -100, 100);
  const room = input.room ?? { kind: 'none' };
  if (!room || typeof room !== 'object' || !ROOMS.includes(room.kind)) bad('room.kind must be one of ' + ROOMS.join(', '));
  for (const k of Object.keys(room)) if (!['kind', 'floor_y', 'source', 'scale_verified'].includes(k)) bad('unknown room field ' + k);
  const outRoom = { kind: room.kind };
  if (room.kind !== 'none') outRoom.floor_y = num(room.floor_y ?? 0, 'room.floor_y');
  if (room.kind === 'ply') {
    outRoom.source = typeof room.source === 'string' && room.source.length <= 200 ? room.source : bad('room.source must be a string');
    outRoom.scale_verified = room.scale_verified === true;
  }
  const objects = input.objects ?? [];
  if (!Array.isArray(objects)) bad('objects must be an array');
  if (objects.length > MAX_OBJECTS) bad('at most ' + MAX_OBJECTS + ' objects');
  const ids = new Set();
  const out = objects.map((o, i) => {
    const at = 'objects[' + i + ']';
    if (!o || typeof o !== 'object' || Array.isArray(o)) bad(at + ' must be an object');
    for (const k of Object.keys(o)) if (!OBJECT_KEYS.has(k)) bad(at + ': unknown field ' + k);
    if (!KINDS.includes(o.kind)) bad(at + '.kind must be one of ' + KINDS.join(', '));
    if (typeof o.id !== 'string' || !/^[A-Za-z0-9_-]{1,40}$/.test(o.id)) bad(at + '.id must match [A-Za-z0-9_-]{1,40}');
    if (ids.has(o.id)) bad('duplicate id ' + o.id);
    ids.add(o.id);
    const d = DEFAULTS[o.kind];
    const q = vec(o.rotation ?? [0, 0, 0, 1], 4, at + '.rotation', -1.0001, 1.0001);
    const qn = Math.hypot(...q);
    if (qn < 1e-6) bad(at + '.rotation must be a unit quaternion');
    const given = o.params ?? {};
    if (typeof given !== 'object' || Array.isArray(given)) bad(at + '.params must be an object');
    for (const k of Object.keys(given)) if (!PARAM_KEYS[o.kind].includes(k)) bad(at + '.params: unknown field ' + k);
    const params = {};
    for (const k of PARAM_KEYS[o.kind]) {
      const [lo, hi] = k === 'angle_deg' ? [-179, 179] : k === 'stiffness' ? [0.01, 1e5] : k === 'damping' ? [0, 1e4] : k === 'stretch' ? [-50, 50] : [0.01, 50];
      params[k] = num(given[k] ?? d.params[k], at + '.params.' + k, lo, hi);
    }
    const bool = (k, dflt) => (o[k] === undefined ? dflt : typeof o[k] === 'boolean' ? o[k] : bad(at + '.' + k + ' must be boolean'));
    return {
      id: o.id, kind: o.kind,
      position: vec(o.position ?? [0, 1, 0], 3, at + '.position', -1000, 1000),
      rotation: q.map((x) => x / qn),
      size: vec(o.size ?? d.size, 3, at + '.size', 0.005, 50),
      velocity: vec(o.velocity ?? [0, 0, 0], 3, at + '.velocity', -100, 100),
      mass: num(o.mass ?? 1, at + '.mass', 1e-4, 1e4),
      friction: num(o.friction ?? 0.5, at + '.friction', 0, 10),
      restitution: num(o.restitution ?? 0.3, at + '.restitution', 0, 1),
      fixed: bool('fixed', d.fixed ?? false),
      sensor: bool('sensor', o.kind !== 'ramp'),
      params,
    };
  });
  return { version: SCENE_VERSION, label: 'SIMULATED', units: 'm', gravity, room: outRoom, objects: out };
}

export function parseScene(text) {
  if (typeof text !== 'string' || text.length > 512 * 1024) bad('scene JSON must be a string under 512 KiB');
  let raw;
  try { raw = JSON.parse(text); } catch { bad('scene is not valid JSON'); }
  return validateScene(raw);
}
export const sceneJson = (scene) => JSON.stringify(validateScene(scene), null, 2);

// Sensor trace -> Build/fitter fit_observations request (one axis, simulated quantities, zero declared sigma).
export function fitterRequest(trace, axis = 1, degree = 2) {
  if (!trace?.samples?.length) bad('trace has no samples');
  const source = { label: 'simulated', evidence: 'lab-editor ' + trace.object_id + ' axis ' + 'xyz'[axis] };
  return {
    times: trace.samples.map((s) => ({ value: s.t, unit: 's', uncertainty: 0, source })),
    positions: trace.samples.map((s) => ({ value: s.p[axis], unit: 'm', uncertainty: 0, source })),
    degree,
  };
}
