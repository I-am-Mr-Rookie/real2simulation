// Rapier world built from a validated lab-scene-v1. RAPIER is passed in so Node tests and the browser share this code.
import { validateScene, PROBES } from './scene.mjs';
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

// N33 kit layout in scene coordinates (shared with the editor meshes). Strings and axles use scene y as vertical and
// the object's yaw only. shortcut: tilted gravity bends nothing here; upgrade if kit objects must follow a room tilt.
export function kitParts(o) {
  const P = o.params, at = (v) => add(o.position, qrot(o.rotation, v));
  if (o.kind === 'flywheel') return [{ p: o.position, r: P.radius, role: 'disc' }, { p: at([P.radius, -P.hang_length, 0]), r: 0.025, role: 'hang' }];
  if (o.kind === 'atwood') return [{ p: at([-P.radius, -P.hang_length, 0]), r: 0.03, role: 'm1' }, { p: at([P.radius, -P.hang_length, 0]), r: 0.03, role: 'm2' }];
  if (o.kind === 'cart') {
    const a = (P.angle_deg * Math.PI) / 180, tilt = [0, 0, Math.sin(a / 2), Math.cos(a / 2)];
    const q = qmul(o.rotation, tilt), h = o.size[1] / 2 + 0.02;
    return [{ p: o.position, q, role: 'track', size: [P.length, 0.04, 0.2] }, { p: add(o.position, qrot(q, [P.length / 2 - o.size[0], h, 0])), q, role: 'cart', size: o.size }];
  }
  if (o.kind === 'cradle') {
    const d = Math.max(...o.size) + 0.005, n = P.count, a = (P.angle_deg * Math.PI) / 180;
    return Array.from({ length: n }, (_, i) => {
      const anchor = at([(i - (n - 1) / 2) * d, 0, 0]);
      return { anchor, p: i === 0 ? add(anchor, qrot(o.rotation, [-P.length * Math.sin(a), -P.length * Math.cos(a), 0])) : add(anchor, [0, -P.length, 0]), role: 'bob' };
    });
  }
  return [];
}
const qmul = ([ax, ay, az, aw], [bx, by, bz, bw]) => [aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx, aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz];
const sub = (a, b) => a.map((v, i) => v - b[i]);
const dot = (a, b) => a.reduce((s, v, i) => s + v * b[i], 0);

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

// N31: SF3D mesh shape (unit box, scaled by size): fixed -> trimesh, movable -> convex hull. null = use the box.
// N44: with a support slab, triangles touching the flattened top are left out: their slanted normals at the top edge
// pushed a dropped ball sideways on contact and it rolled off (N43 RM02 table); the slab alone forms the top.
export function meshCollider(R, o) {
  if (o.shape?.type !== 'mesh') return null;
  const v = new Float32Array(o.shape.vertices.map((x, i) => x * o.size[i % 3]));
  if (!o.fixed) return R.ColliderDesc.convexHull(v);
  let idx = o.shape.indices;
  if (o.shape.support) {
    const y = o.shape.vertices, low = (i) => y[3 * i + 1] < 0.499;
    idx = idx.filter((_, k) => { const t = k - (k % 3); return low(idx[t]) && low(idx[t + 1]) && low(idx[t + 2]); });
    if (!idx.length) return null;
  }
  return R.ColliderDesc.trimesh(v, new Uint32Array(idx));
}

// N42: fixed support furniture (table, shelf): solid convex slab under the SF3D top outline, at the measured top. A thin
// trimesh top let a falling ball tunnel or roll off (N39); the slab is at most 3 cm (or the object height) thick.
export function topCollider(R, o) {
  const sp = o.shape?.type === 'mesh' && o.fixed && o.shape.support;
  if (!sp) return null;
  const v = o.shape.vertices.slice(-3 * sp.outline), y0 = o.size[1] / 2, y1 = y0 - Math.min(0.03, o.size[1]), p = [];
  for (let k = 0; k < v.length; k += 3) p.push(v[k] * o.size[0], y0, v[k + 2] * o.size[2], v[k] * o.size[0], y1, v[k + 2] * o.size[2]);
  return R.ColliderDesc.convexHull(new Float32Array(p));
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
  const pre = []; // N33 string constraints: velocity projections before each world.step (inextensible, can go slack)
  const gy = scene.gravity[1];
  const v3a = (b) => { const v = b.linvel(); return [v.x, v.y, v.z]; };
  const hanger = (p, r, mass) => {
    const b = world.createRigidBody(R.RigidBodyDesc.dynamic().setTranslation(...p).lockRotations().setCcdEnabled(true));
    world.createCollider(R.ColliderDesc.ball(r).setMass(mass).setFriction(0.5).setRestitution(0.1), b);
    return b;
  };
  for (const o of scene.objects) {
    if (PROBES.includes(o.kind)) { moving.set(o.id, { o, body: null }); continue; }
    if (['flywheel', 'atwood', 'cart', 'cradle'].includes(o.kind)) {
      const parts = kitParts(o), P = o.params, bodies = [];
      if (o.kind === 'flywheel') {
        const I = P.inertia || 0.5 * o.mass * P.radius ** 2;
        const disc = world.createRigidBody(R.RigidBodyDesc.dynamic().setTranslation(...o.position).setRotation(q4(o.rotation)).lockTranslations()
          .setAdditionalMassProperties(o.mass, v3([0, 0, 0]), v3([I / 2, I / 2, I]), q4([0, 0, 0, 1])).enabledRotations(false, false, true));
        const m = hanger(parts[1].p, 0.025, P.hang_mass), r = P.radius;
        bodies.push(disc, m);
        pre.push(() => { // rim speed w r must equal the mass's downward string speed while the string is taut
          const w = disc.angvel().z, v = v3a(m), vy = v[1] + gy * DT;
          if (vy >= w * r) return;
          const u = (P.hang_mass * vy + (I / r) * w) / (P.hang_mass + I / (r * r));
          m.setLinvel(v3([0, u - gy * DT, 0]), true); disc.setAngvel(v3([0, 0, u / r]), true);
        });
      } else if (o.kind === 'atwood') {
        const [b1, b2] = [hanger(parts[0].p, 0.03, P.m1), hanger(parts[1].p, 0.03, P.m2)];
        bodies.push(b1, b2);
        pre.push(() => {
          const y1 = v3a(b1)[1] + gy * DT, y2 = v3a(b2)[1] + gy * DT;
          if (y1 + y2 >= 0) return; // string would shorten: slack
          const u = (P.m1 * y1 - P.m2 * y2) / (P.m1 + P.m2);
          b1.setLinvel(v3([0, u - gy * DT, 0]), true); b2.setLinvel(v3([0, -u - gy * DT, 0]), true);
        });
      } else if (o.kind === 'cart') {
        const [tr, ct] = parts;
        const track = world.createRigidBody(R.RigidBodyDesc.fixed().setTranslation(...tr.p).setRotation(q4(tr.q)));
        world.createCollider(R.ColliderDesc.cuboid(...tr.size.map((s) => s / 2)).setFriction(o.friction).setRestitution(0), track);
        const cart = world.createRigidBody(R.RigidBodyDesc.dynamic().setTranslation(...ct.p).setRotation(q4(ct.q)).setLinvel(...o.velocity).setCcdEnabled(true));
        world.createCollider(R.ColliderDesc.cuboid(...o.size.map((s) => s / 2)).setMass(o.mass).setFriction(o.friction).setRestitution(0), cart);
        bodies.push(track, cart);
      } else {
        for (const pt of parts) {
          const anchor = world.createRigidBody(R.RigidBodyDesc.fixed().setTranslation(...pt.anchor));
          const bob = world.createRigidBody(R.RigidBodyDesc.dynamic().setTranslation(...pt.p).setCcdEnabled(true));
          world.createCollider(R.ColliderDesc.ball(Math.max(...o.size) / 2).setMass(o.mass).setFriction(o.friction).setRestitution(o.restitution), bob);
          world.createImpulseJoint(R.JointData.spherical(v3([0, 0, 0]), v3(sub(pt.anchor, pt.p))), anchor, bob, true);
          bodies.push(bob);
        }
      }
      // Traced part: the hanging mass, mass 1, the cart, the last cradle ball.
      moving.set(o.id, { o, body: bodies[o.kind === 'flywheel' || o.kind === 'cart' ? 1 : o.kind === 'atwood' ? 0 : bodies.length - 1], parts: bodies });
      continue;
    }
    const half = o.size.map((s) => s / 2);
    const shape = meshCollider(R, o) ?? (o.kind === 'ball' || o.kind === 'pendulum' || o.kind === 'launcher' ? R.ColliderDesc.ball(Math.max(...half))
      : o.kind === 'mass' ? R.ColliderDesc.cylinder(half[1], half[0]) : R.ColliderDesc.cuboid(...half));
    shape.setMass(o.mass).setFriction(o.friction).setRestitution(o.restitution);
    const jointed = o.kind === 'pendulum' || o.kind === 'spring';
    const start = movingStart(o);
    const a = (o.params.angle_deg * Math.PI) / 180; // launcher: fires along its local +x, tilted up by angle_deg
    const vel = o.kind === 'launcher' ? qrot(o.rotation, [o.params.speed * Math.cos(a), o.params.speed * Math.sin(a), 0]) : o.velocity;
    // Jointed moving parts start unrotated so the joint anchor below is in world-aligned local axes.
    const desc = (!jointed && o.kind !== 'launcher' && o.fixed ? R.RigidBodyDesc.fixed() : R.RigidBodyDesc.dynamic())
      .setTranslation(...start).setRotation(q4(jointed ? [0, 0, 0, 1] : o.rotation)).setLinvel(...vel).setCcdEnabled(true);
    const body = world.createRigidBody(desc);
    world.createCollider(shape, body);
    const top = topCollider(R, o);
    if (top) world.createCollider(top.setFriction(o.friction).setRestitution(o.restitution), body);
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
  // Probes read the nearest non-probe moving part at the start: ruler = distance along its axis, protractor = angle
  // from straight down about its centre, photogate = interpolated times the part crosses its horizontal beam plane.
  const bodiesOf = [...moving.values()].filter((m) => m.body && !(m.o.fixed && ['ball', 'block', 'mass', 'ramp'].includes(m.o.kind)));
  const probes = [...moving.values()].filter((m) => !m.body).map((m) => {
    const near = bodiesOf.map((b) => [Math.hypot(...sub(pose(b.body).p, m.o.position)), b]).sort((x, y) => x[0] - y[0])[0]?.[1];
    return { ...m, target: near ?? null, last: null };
  });
  const reading = (pr, p) => {
    const o = pr.o, d = sub(p, o.position);
    if (o.kind === 'ruler') return dot(d, qrot(o.rotation, [1, 0, 0])) + o.params.length / 2;
    if (o.kind === 'protractor') { const x = dot(d, qrot(o.rotation, [1, 0, 0])), y = dot(d, qrot(o.rotation, [0, 1, 0])); return (Math.atan2(x, -y) * 180) / Math.PI; }
    return dot(d, qrot(o.rotation, [0, 1, 0])); // photogate: signed distance to the beam plane
  };
  const record = () => {
    for (const pr of probes) {
      const s = traces.get(pr.o.id);
      if (!s || !pr.target || s.length >= MAX_SAMPLES) continue;
      const p = pose(pr.target.body).p, v = reading(pr, p);
      if (pr.o.kind !== 'photogate') s.push({ t: Number(t.toFixed(9)), p, value: v });
      else if (pr.last && pr.last.v * v < 0) { const f = pr.last.v / (pr.last.v - v), te = pr.last.t + f * DT; s.push({ t: Number(te.toFixed(9)), p: p.map((x, i) => pr.last.p[i] + f * (x - pr.last.p[i])), value: te }); }
      pr.last = { t, p, v };
    }
    for (const [id, s] of traces) if (moving.get(id).body && s.length < MAX_SAMPLES) s.push({ t: Number(t.toFixed(9)), p: pose(moving.get(id).body).p });
  };
  record();
  return {
    scene,
    get time() { return t; },
    step(n = 1) { for (let i = 0; i < n; i++) { for (const f of pre) f(); world.step(); t += DT; record(); } },
    poses() { return Object.fromEntries([...moving].filter(([, m]) => m.body).map(([id, { body, parts }]) => [id, parts ? { ...pose(body), parts: parts.map(pose) } : pose(body)])); },
    trace(id) {
      const samples = traces.get(id);
      if (!samples) return null;
      const { o } = moving.get(id), pr = probes.find((x) => x.o.id === id);
      const units = { t: 's', p: 'm', ...(pr ? { value: o.kind === 'protractor' ? 'deg' : o.kind === 'photogate' ? 's' : 'm' } : {}) };
      return { version: 'lab-trace-v1', label: 'SIMULATED', object_id: id, kind: o.kind, frame: 'scene', units, ...(pr ? { target: pr.target?.o.id ?? null } : {}),
        dt: DT, gravity: scene.gravity, truncated: samples.length >= MAX_SAMPLES, samples: samples.slice() };
    },
    traces() { return [...traces.keys()].map((id) => this.trace(id)); },
    free() { world.free(); },
  };
}

