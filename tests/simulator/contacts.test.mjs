import test from 'node:test';
import assert from 'node:assert/strict';
import { freeFallTrajectory } from '../../Build/simulator/trajectories.mjs';
import { contactAwareTrajectory } from '../../Build/simulator/contacts.mjs';

const physics = { friction: 0.4, restitution: 0, density: 1 };
const geometry = { floorY: 0, floorHalfExtents: [5, 0.1, 5], sphereRadius: 0.1 };
const falling = () => freeFallTrajectory({ initialPosition: [0, 2, 0], initialVelocity: [0, 0, 0], gravity: 9.81, dt: 0.01, steps: 200, source: 'simulated', inputProvenance: 'synthetic' });

test('real Rapier contact is mapped onto the same RK4 samples', async () => {
  const out = await contactAwareTrajectory({ trajectory: falling(), geometry, physics, gravity: 9.81 });
  assert.equal(out.samples.length, 201);
  assert.equal(out.contactEngine, 'rapier3d-compat-0.21.0');
  assert.ok(out.samples.some((s) => s.contact));
  assert.deepEqual(out.samples[20].position_m, falling().samples[20].position_m);
  assert.equal(out.samples.at(-1).contacts[0].colliderA, 'sphere');
});

test('no-contact trajectory remains no-contact and deterministic', async () => {
  const input = { trajectory: freeFallTrajectory({ initialPosition: [0, 10, 0], initialVelocity: [0, 0, 0], gravity: 9.81, dt: 0.01, steps: 2, source: 'simulated', inputProvenance: 'synthetic' }), geometry, physics, gravity: 9.81 };
  const [a, b] = await Promise.all([contactAwareTrajectory(input), contactAwareTrajectory(input)]);
  assert.deepEqual(a, b); assert.ok(a.samples.every((s) => !s.contact));
});

test('rejects invalid explicit physics and geometry', async () => {
  await assert.rejects(() => contactAwareTrajectory({ trajectory: falling(), geometry, physics: { ...physics, restitution: 2 }, gravity: 9.81 }), /restitution/);
  await assert.rejects(() => contactAwareTrajectory({ trajectory: falling(), geometry: { ...geometry, sphereRadius: 0 }, physics, gravity: 9.81 }), /sphereRadius/);
  await assert.rejects(() => contactAwareTrajectory({ trajectory: falling(), geometry, physics: { ...physics, friction: Number.NaN }, gravity: 9.81 }), /friction/);
});
