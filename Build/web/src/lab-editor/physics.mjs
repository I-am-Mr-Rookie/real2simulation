// Rapier world built from a validated lab-scene-v1. RAPIER is passed in so Node tests and the browser share this code.
import { validateScene } from './scene.mjs';

export const DT = 1 / 120;
export const MAX_SAMPLES = 12000; // 100 s at 120 Hz per sensor

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

