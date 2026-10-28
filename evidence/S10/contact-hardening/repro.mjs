import { createRequire } from 'node:module';
import { freeFallTrajectory } from '../../../Build/simulator/trajectories.mjs';
import { contactAwareTrajectory } from '../../../Build/simulator/contacts.mjs';

const require = createRequire(new URL('../../../Build/simulator/package.json', import.meta.url));
const RAPIER = require('@dimforge/rapier3d-compat');

const physics = { friction: 0.4, restitution: 0, density: 1 };
const geometry = { floorY: 0, floorHalfExtents: [5, 0.1, 5], sphereRadius: 0.1 };
const trajectory = (y) => freeFallTrajectory({ initialPosition: [0, y, 0],
  initialVelocity: [0, 0, 0], gravity: 9.81, dt: 0.005, steps: 0,
  source: 'simulated', inputProvenance: 'synthetic' });
const rows = [];
for (const [name, y, floor] of [
  ['finite operands overflow derived floor center', 2, { ...geometry, floorY: -1e308, floorHalfExtents: [5, 1e308, 5] }],
  ['initial penetration', 0.05, geometry],
  ['finite JS floor center overflows float32', 2, { ...geometry, floorY: -1e40 }],
  ['finite JS body position overflows float32', 1e40, geometry],
  ['true initial touch', 0.1, geometry],
]) {
  try {
    const result = await contactAwareTrajectory({ trajectory: trajectory(y), geometry: floor, physics, gravity: 9.81 });
    const first = result.samples[0];
    rows.push({ name, status: 'accepted', contact: first.contact,
      contactBracket_s: first.contactBracket_s, manifoldCount: first.contacts.length });
  } catch (error) { rows.push({ name, status: 'rejected', reason: String(error) }); }
}

// Direct installed-engine proof: JSON strings preserve the non-finite value.
await RAPIER.init();
const world = new RAPIER.World({ x: 0, y: 0, z: 0 });
try {
  const collider = world.createCollider(RAPIER.ColliderDesc.cuboid(5, 0.1, 5).setTranslation(0, -1e40, 0));
  const body = world.createRigidBody(RAPIER.RigidBodyDesc.dynamic().setTranslation(0, 1e40, 0));
  rows.push({ name: 'raw Rapier float32 boundary', finiteJSInput: Number.isFinite(1e40),
    fround: String(Math.fround(1e40)), colliderY: String(collider.translation().y), bodyY: String(body.translation().y) });
} finally { world.free(); }
console.log(JSON.stringify(rows, null, 2));
