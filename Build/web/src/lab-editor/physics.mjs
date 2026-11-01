// Rapier world built from a validated lab-scene-v1. RAPIER is passed in so Node tests and the browser share this code.
import { validateScene } from './scene.mjs';
import { robustBounds } from './frame.mjs';

export const DT = 1 / 120;
export const MAX_SAMPLES = 12000; // 100 s at 120 Hz per sensor
export const MAX_COLLIDERS = 300;

let rapierPromise;
// Lazy: the wasm is fetched only when the editor first plays a scene.
export const loadRapier = () => (rapierPromise ??= import('@dimforge/rapier3d-compat').then(async (m) => { const R = m.default ?? m; await R.init(); return R; }));

const qrot = ([x, y, z, w], [vx, vy, vz]) => {
  const tx = 2 * (y * vz - z * vy), ty = 2 * (z * vx - x * vz), tz = 2 * (x * vy - y * vx);
  return [vx + w * tx + (y * tz - z * ty), vy + w * ty + (z * tx - x * tz), vz + w * tz + (x * ty - y * tx)];
};
const add = (a, b) => a.map((v, i) => v + b[i]);

// Quaternion rotating +y onto -gravity, so the floor stays perpendicular to the scene's gravity vector.
export function upQuat(g) {
  const n = Math.hypot(...g);
  if (n < 1e-9) return [0, 0, 0, 1];
  const u = g.map((v) => -v / n);
  const d = u[1];
  if (d < -0.999999) return [1, 0, 0, 0];
  const q = [u[2], 0, -u[0], 1 + d]; // cross((0,1,0), u), 1 + dot
  const m = Math.hypot(...q);
  return q.map((v) => v / m);
}

// Start position of the moving part: pendulum bob or spring mass; the object position is the fixed anchor.
export function movingStart(o) {
  if (o.kind === 'pendulum') {
    const a = (o.params.angle_deg * Math.PI) / 180;
    return add(o.position, qrot(o.rotation, [o.params.length * Math.sin(a), -o.params.length * Math.cos(a), 0]));
  }
  if (o.kind === 'spring') return add(o.position, qrot(o.rotation, [0, -(o.params.rest_length + o.params.stretch), 0]));
  return o.position;
}

// N29: coarse static collision proxy of a room point cloud. Gravity-aligned voxel grid; cells with enough points are
// occupied; the floor slab is left to the floor plane; occupied cells merge greedily into boxes. The grid coarsens
// until it fits maxBoxes. Returns room.collision for lab-scene-v1 (MODEL-ESTIMATED), or null for tiny clouds.
export function roomProxy(positions, gravity = [0, -9.81, 0], floorY = 0, maxBoxes = MAX_COLLIDERS) {
  const n = Math.floor((positions?.length ?? 0) / 3);
  if (n < 50) return null;
  const q = upQuat(gravity), qi = [-q[0], -q[1], -q[2], q[3]];
  const local = new Float32Array(n * 3);
  for (let i = 0; i < n; i += 1) local.set(qrot(qi, [positions[i * 3], positions[i * 3 + 1], positions[i * 3 + 2]]), i * 3);
  const b = robustBounds(local, 0.005);
  const floorH = qrot(qi, [0, floorY, 0])[1];
  const r4 = (v) => Math.round(v * 1e4) / 1e4;
  for (let cells = 40; cells >= 6; cells = Math.floor(cells * 0.75)) {
    const s = Math.max(1e-3, ...b.max.map((m, a) => m - b.min[a])) / cells;
    const [X, Y, Z] = b.max.map((m, a) => Math.max(1, Math.ceil((m - b.min[a]) / s)));
    const at = (i, j, k) => (k * Y + j) * X + i;
    const count = new Uint32Array(X * Y * Z);
    for (let p = 0; p < n; p += 1) {
      const i = Math.floor((local[p * 3] - b.min[0]) / s), j = Math.floor((local[p * 3 + 1] - b.min[1]) / s), k = Math.floor((local[p * 3 + 2] - b.min[2]) / s);
      if (i >= 0 && i < X && j >= 0 && j < Y && k >= 0 && k < Z) count[at(i, j, k)] += 1;
    }
    const nz = [...count.filter((c) => c > 0)].sort((u, v) => u - v);
    const thr = Math.max(3, 0.25 * (nz[nz.length >> 1] ?? 0)); // sparse cells are stray reconstruction points
    const occ = new Uint8Array(X * Y * Z);
    for (let j = 0; j < Y; j += 1) {
      if (b.min[1] + (j + 1) * s <= floorH + s) continue; // floor slab: the floor plane collider covers it
      for (let k = 0; k < Z; k += 1) for (let i = 0; i < X; i += 1) if (count[at(i, j, k)] >= thr) occ[at(i, j, k)] = 1;
    }
    const full = (i0, i1, j0, j1, k0, k1) => {
      for (let j = j0; j <= j1; j += 1) for (let k = k0; k <= k1; k += 1) for (let i = i0; i <= i1; i += 1) if (!occ[at(i, j, k)]) return false;
      return true;
    };
    const boxes = [];
    for (let j = 0; j < Y && boxes.length <= maxBoxes; j += 1) for (let k = 0; k < Z; k += 1) for (let i = 0; i < X; i += 1) {
      if (!occ[at(i, j, k)]) continue;
      let i1 = i, k1 = k, j1 = j;
      while (i1 + 1 < X && full(i1 + 1, i1 + 1, j, j, k, k)) i1 += 1;
      while (k1 + 1 < Z && full(i, i1, j, j, k1 + 1, k1 + 1)) k1 += 1;
      while (j1 + 1 < Y && full(i, i1, j1 + 1, j1 + 1, k, k1)) j1 += 1;
      for (let jj = j; jj <= j1; jj += 1) for (let kk = k; kk <= k1; kk += 1) for (let ii = i; ii <= i1; ii += 1) occ[at(ii, jj, kk)] = 0;
      const lo = [i, j, k], hi = [i1 + 1, j1 + 1, k1 + 1];
      const c = qrot(q, lo.map((v, a) => b.min[a] + ((v + hi[a]) / 2) * s));
      boxes.push([...c, ...lo.map((v, a) => ((hi[a] - v) * s) / 2)].map(r4));
    }
    if (boxes.length <= maxBoxes) return { enabled: true, label: 'MODEL-ESTIMATED', rotation: q.map(r4), cell: r4(s), boxes };
  }
  return null;
}

export function createPhysics(R, sceneInput) {
  const scene = validateScene(sceneInput);
  const v3 = ([x, y, z]) => ({ x, y, z });
  const q4 = ([x, y, z, w]) => ({ x, y, z, w });
  const world = new R.World(v3(scene.gravity));
  world.timestep = DT;
  if (scene.room.kind !== 'none') {
    const q = upQuat(scene.gravity);
    const centre = add([0, scene.room.floor_y, 0], qrot(q, [0, -0.5, 0]));
    const floor = world.createRigidBody(R.RigidBodyDesc.fixed().setTranslation(...centre).setRotation(q4(q)));
    world.createCollider(R.ColliderDesc.cuboid(500, 0.5, 500).setFriction(0.6).setRestitution(0.3), floor);
  }
  const proxy = scene.room.collision;
  if (proxy?.enabled && proxy.boxes.length) {
    const body = world.createRigidBody(R.RigidBodyDesc.fixed());
    for (const [x, y, z, hx, hy, hz] of proxy.boxes) {
      world.createCollider(R.ColliderDesc.cuboid(hx, hy, hz).setTranslation(x, y, z).setRotation(q4(proxy.rotation)).setFriction(0.6).setRestitution(0.3), body);
    }
  }
  const moving = new Map();
  for (const o of scene.objects) {
    const half = o.size.map((s) => s / 2);
    const shape = o.kind === 'ball' || o.kind === 'pendulum' ? R.ColliderDesc.ball(Math.max(...half)) : R.ColliderDesc.cuboid(...half);
    shape.setMass(o.mass).setFriction(o.friction).setRestitution(o.restitution);
    const jointed = o.kind === 'pendulum' || o.kind === 'spring';
    const start = movingStart(o);
    // Jointed moving parts start unrotated so the joint anchor below is in world-aligned local axes.
    const desc = (!jointed && o.fixed ? R.RigidBodyDesc.fixed() : R.RigidBodyDesc.dynamic())
      .setTranslation(...start).setRotation(q4(jointed ? [0, 0, 0, 1] : o.rotation)).setLinvel(...o.velocity).setCcdEnabled(true);
    const body = world.createRigidBody(desc);
    world.createCollider(shape, body);
    if (jointed) {
      const anchor = world.createRigidBody(R.RigidBodyDesc.fixed().setTranslation(...o.position));
      const rel = start.map((v, i) => v - o.position[i]);
      const len = Math.hypot(...rel);
      const joint = o.kind === 'pendulum'
        ? R.JointData.spherical(v3([0, 0, 0]), v3(rel.map((v) => -v)))
        : R.JointData.spring(o.params.rest_length, o.params.stiffness, o.params.damping, v3([0, 0, 0]), v3([0, 0, 0]));
      world.createImpulseJoint(joint, anchor, body, true);
      if (o.kind === 'spring' && len === 0) throw new Error(o.id + ': spring mass coincides with anchor');
    }
    moving.set(o.id, { o, body });
  }
  let t = 0;
  const traces = new Map(scene.objects.filter((o) => o.sensor).map((o) => [o.id, []]));
  const pose = (b) => { const p = b.translation(), q = b.rotation(); return { p: [p.x, p.y, p.z], q: [q.x, q.y, q.z, q.w] }; };
  const record = () => {
    for (const [id, s] of traces) if (s.length < MAX_SAMPLES) s.push({ t: Number(t.toFixed(9)), p: pose(moving.get(id).body).p });
  };
  record();
  return {
    scene,
    get time() { return t; },
    step(n = 1) { for (let i = 0; i < n; i++) { world.step(); t += DT; record(); } },
    poses() { return Object.fromEntries([...moving].map(([id, { body }]) => [id, pose(body)])); },
    trace(id) {
      const samples = traces.get(id);
      if (!samples) return null;
      return { version: 'lab-trace-v1', label: 'SIMULATED', object_id: id, kind: moving.get(id).o.kind, frame: 'scene', units: { t: 's', p: 'm' },
        dt: DT, gravity: scene.gravity, truncated: samples.length >= MAX_SAMPLES, samples: samples.slice() };
    },
    traces() { return [...traces.keys()].map((id) => this.trace(id)); },
    free() { world.free(); },
  };
}

