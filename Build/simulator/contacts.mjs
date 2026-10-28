import RAPIER from '@dimforge/rapier3d-compat';

const fail = (message) => { throw new TypeError(`INVALID_CONTACTS: ${message}`); };
const finite = (v) => typeof v === 'number' && Number.isFinite(v);
const vec3 = (v) => Array.isArray(v) && v.length === 3 && v.every(finite);
const positive = (v, name) => { if (!finite(v) || v <= 0) fail(`${name} must be finite and positive`); return v; };
const nonnegative = (v, name) => { if (!finite(v) || v < 0) fail(`${name} must be finite and non-negative`); return v; };
let ready;
const init = () => (ready ??= RAPIER.init());

function checked(input) {
  if (!input || typeof input !== 'object' || !input.trajectory) fail('trajectory is required');
  const t = input.trajectory;
  if (!['free-fall', 'projectile'].includes(t.kind) || t.integrator !== 'rk4-fixed-step' || !Array.isArray(t.samples)) fail('trajectory must be an RK4 trajectory output');
  if (!finite(t.dt_s) || t.dt_s <= 0 || !Number.isSafeInteger(t.requestedSteps) || t.requestedSteps < 0) fail('trajectory timestep/steps are invalid');
  const g = input.geometry ?? {};
  if (!finite(g.floorY) || !vec3(g.floorHalfExtents) || g.floorHalfExtents.some((v) => v <= 0)) fail('floorY and floorHalfExtents are required');
  const radius = positive(g.sphereRadius, 'sphereRadius');
  const physics = input.physics ?? {};
  const friction = nonnegative(physics.friction, 'friction');
  const restitution = physics.restitution;
  if (!finite(restitution) || restitution < 0 || restitution > 1) fail('restitution must be finite in [0,1]');
  const density = positive(physics.density, 'density');
  return { t, g, radius, friction, restitution, density };
}

function readContacts(world, sphere, floor, ids) {
  const contacts = [];
  world.narrowPhase.contactPairsWith(sphere.handle, (other) => {
    if (other !== floor.handle) return;
    world.narrowPhase.contactPair(sphere.handle, floor.handle, world.bodies, (manifold, flipped) => {
      if (!manifold.numContacts()) return;
      const normal = manifold.normal();
      contacts.push({ colliderA: ids.get(sphere.handle), colliderB: ids.get(floor.handle), pointCount: manifold.numContacts(), normal_m: [flipped ? -normal.x : normal.x, flipped ? -normal.y : normal.y, flipped ? -normal.z : normal.z] });
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
  const { t, g, radius, friction, restitution, density } = checked(input);
  await init();
  const world = new RAPIER.World({ x: 0, y: -positive(input.gravity ?? 9.81, 'gravity'), z: 0 });
  const ids = new Map();
  try {
    const floorDesc = RAPIER.ColliderDesc.cuboid(...g.floorHalfExtents).setTranslation(0, g.floorY, 0).setFriction(friction).setRestitution(restitution);
    const floor = world.createCollider(floorDesc); ids.set(floor.handle, 'floor');
    const first = t.samples[0];
    if (!first || !vec3(first.position_m) || !vec3(first.velocity_m_s)) fail('trajectory samples contain invalid state');
    const body = world.createRigidBody(RAPIER.RigidBodyDesc.dynamic().setTranslation(...first.position_m).setLinvel(...first.velocity_m_s).setCcdEnabled(true));
    const sphere = world.createCollider(RAPIER.ColliderDesc.ball(radius).setDensity(density).setFriction(friction).setRestitution(restitution), body);
    ids.set(sphere.handle, 'sphere');
    const samples = t.samples.map((sample, index) => {
      if (!sample || !vec3(sample.position_m) || !vec3(sample.velocity_m_s) || !finite(sample.time_s)) fail('trajectory samples contain non-finite state');
      if (index > 0) world.step();
      const contacts = readContacts(world, sphere, floor, ids);
      return Object.freeze({ ...sample, contacts: Object.freeze(contacts.map((c) => Object.freeze(c))), contact: contacts.length > 0 });
    });
    return Object.freeze({ kind: t.kind, source: t.source, inputProvenance: t.inputProvenance, integrator: t.integrator, contactEngine: 'rapier3d-compat-0.21.0', contactSemantics: 'Rapier detector sampled beside RK4; RK4 state is authoritative', geometry: Object.freeze({ floorY: g.floorY, floorHalfExtents: [...g.floorHalfExtents], sphereRadius: radius }), samples: Object.freeze(samples) });
  } finally { world.free(); }
}
