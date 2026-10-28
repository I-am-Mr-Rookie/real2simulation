import RAPIER from '@dimforge/rapier3d-compat';

const fail = (message) => { throw new TypeError(`INVALID_CONTACTS: ${message}`); };
const finite = (v) => typeof v === 'number' && Number.isFinite(v);
const vec3 = (v) => Array.isArray(v) && v.length === 3 && [0, 1, 2].every((i) => Object.prototype.hasOwnProperty.call(v, i) && finite(v[i]));
const positive = (v, name) => { if (!finite(v) || v <= 0) fail(`${name} must be finite and positive`); return v; };
const nonnegative = (v, name) => { if (!finite(v) || v < 0) fail(`${name} must be finite and non-negative`); return v; };
let ready;
const init = () => (ready ??= RAPIER.init());

function checked(input) {
  if (!input || typeof input !== 'object' || !input.trajectory) fail('trajectory is required');
  const t = input.trajectory;
  if (!['free-fall', 'projectile'].includes(t.kind) || t.integrator !== 'rk4-fixed-step' || !Array.isArray(t.samples)) fail('trajectory must be an RK4 trajectory output');
  if (t.source !== 'simulated' || t.inputProvenance !== 'synthetic') fail('source labels must be explicit simulated/synthetic');
  if (!finite(t.dt_s) || t.dt_s <= 0 || !Number.isSafeInteger(t.requestedSteps) || t.requestedSteps < 0) fail('trajectory timestep/steps are invalid');
  if (t.samples.length === 0 || t.samples.length > t.requestedSteps + 1 || !Array.from({ length: t.samples.length }, (_, i) => Object.prototype.hasOwnProperty.call(t.samples, i)).every(Boolean)) fail('trajectory samples must be non-empty, dense, and bounded');
  const g = input.geometry ?? {};
  if (!finite(g.floorY) || !vec3(g.floorHalfExtents) || g.floorHalfExtents.some((v) => v <= 0)) fail('floorY and floorHalfExtents are required');
  const radius = positive(g.sphereRadius, 'sphereRadius');
  const physics = input.physics ?? {};
  const friction = nonnegative(physics.friction, 'friction');
  const restitution = physics.restitution;
  if (!finite(restitution) || restitution < 0 || restitution > 1) fail('restitution must be finite in [0,1]');
  const density = positive(physics.density, 'density');
  const gravity = input.gravity;
  if (!finite(gravity) || gravity <= 0) fail('gravity must be finite and positive');
  return { t, g, radius, friction, restitution, density, gravity };
}

function readContacts(world, sphere, floor, ids) {
  const contacts = [];
  world.narrowPhase.contactPairsWith(sphere.handle, (other) => {
    if (other !== floor.handle) return;
    world.narrowPhase.contactPair(sphere.handle, floor.handle, world.bodies, (manifold, flipped) => {
      if (!manifold.numContacts()) return;
      const normal = manifold.normal();
      contacts.push({ colliderA: ids.get(sphere.handle), colliderB: ids.get(floor.handle), pointCount: manifold.numContacts(), normal_m: Object.freeze([flipped ? -normal.x : normal.x, flipped ? -normal.y : normal.y, flipped ? -normal.z : normal.z]) });
    });
  });
  return contacts;
}

/**
 * Runs Rapier only as a contact detector. Positions/velocities stay the supplied
 * RK4 samples, preserving the accepted analytic trajectory; contact metadata is
 * sampled at the same step/time and is not a physical Gate-P result.
 */
export async function contactAwareTrajectory(input) {
  const { t, g, radius, friction, restitution, density, gravity } = checked(input);
  await init();
  const world = new RAPIER.World({ x: 0, y: -gravity, z: 0 });
  world.timestep = t.dt_s;
  const ids = new Map();
  try {
    const floorDesc = RAPIER.ColliderDesc.cuboid(...g.floorHalfExtents).setTranslation(0, g.floorY - g.floorHalfExtents[1], 0).setFriction(friction).setRestitution(restitution);
    const floor = world.createCollider(floorDesc); ids.set(floor.handle, 'floor');
    const first = t.samples[0];
    if (!first || !vec3(first.position_m) || !vec3(first.velocity_m_s)) fail('trajectory samples contain invalid state');
    // Disable solver evolution: each dynamic body pose is replaced by the exact
    // RK4 sample before Rapier's actual narrow phase runs.
    const body = world.createRigidBody(RAPIER.RigidBodyDesc.dynamic().setGravityScale(0, true).setTranslation(...first.position_m));
    const sphere = world.createCollider(RAPIER.ColliderDesc.ball(radius).setDensity(density).setFriction(friction).setRestitution(restitution), body);
    ids.set(sphere.handle, 'sphere');
    const samples = [];
    for (let index = 0; index < t.samples.length; index += 1) {
      const sample = t.samples[index];
      if (!sample || sample.step !== index || sample.time_s !== index * t.dt_s || !vec3(sample.position_m) || !vec3(sample.velocity_m_s) || !finite(sample.time_s)) fail('trajectory samples must have exact step/time and finite dense state');
      if (Math.abs(sample.position_m[0]) + radius > g.floorHalfExtents[0] || Math.abs(sample.position_m[2]) + radius > g.floorHalfExtents[2]) fail('sphere must remain within supported floor footprint');
      const previous = t.samples[index - 1];
      if (previous && Math.hypot(...previous.velocity_m_s) * t.dt_s + 0.5 * gravity * t.dt_s ** 2 > radius / 2) fail('time_step permits excessive displacement; reduce it');
      body.setTranslation({ x: sample.position_m[0], y: sample.position_m[1], z: sample.position_m[2] }, true);
      body.setLinvel({ x: 0, y: 0, z: 0 }, true);
      world.timestep = t.dt_s;
      world.step();
      const contacts = readContacts(world, sphere, floor, ids);
      const touch = sample.position_m[1] - radius <= g.floorY;
      const bracket = touch ? Object.freeze([previous?.time_s ?? sample.time_s, sample.time_s]) : null;
      samples.push(Object.freeze({ step: index, time_s: sample.time_s, position_m: Object.freeze([...sample.position_m]), velocity_m_s: Object.freeze([...sample.velocity_m_s]), contacts: Object.freeze(contacts.map((c) => Object.freeze(c))), contact: touch, contactBracket_s: bracket }));
      if (touch) break;
    }
    return Object.freeze({ kind: t.kind, source: t.source, inputProvenance: t.inputProvenance, integrator: t.integrator, contactEngine: 'rapier3d-compat-0.21.0', contactSemantics: 'Sphere-floor touch uses RK4 sample geometry and a time bracket; contacts contains Rapier candidate manifolds, not touch truth. Unsupported coarse steps reject.', geometry: Object.freeze({ floorY: g.floorY, floorHalfExtents: Object.freeze([...g.floorHalfExtents]), sphereRadius: radius }), samples: Object.freeze(samples) });
  } finally { world.free(); }
}
