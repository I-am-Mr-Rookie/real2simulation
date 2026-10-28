import test from 'node:test';
import assert from 'node:assert/strict';
import { freeFallTrajectory } from '../../Build/simulator/trajectories.mjs';
import { contactAwareTrajectory } from '../../Build/simulator/contacts.mjs';

const physics = { friction: 0.4, restitution: 0, density: 1 };
const geometry = { floorY: 0, floorHalfExtents: [5, 0.1, 5], sphereRadius: 0.1 };
const falling = (dt = 0.01) => freeFallTrajectory({ initialPosition: [0, 2, 0], initialVelocity: [0, 0, 0], gravity: 9.81, dt, steps: Math.round(2 / dt), source: 'simulated', inputProvenance: 'synthetic' });

test('real Rapier contact is mapped onto the same RK4 samples', async () => {
  const out = await contactAwareTrajectory({ trajectory: falling(), geometry, physics, gravity: 9.81 });
  assert.ok(out.samples.length < 201);
  assert.equal(out.contactEngine, 'rapier3d-compat-0.21.0');
  assert.ok(out.samples.some((s) => s.contact));
  assert.deepEqual(out.samples[20].position_m, falling().samples[20].position_m);
  const firstContact = out.samples.findIndex((s) => s.contact);
  assert.ok(firstContact > 0);
  assert.equal(out.samples[firstContact].contacts[0].colliderA, 'sphere');
  assert.ok(out.samples[firstContact].position_m[1] - geometry.floorY >= geometry.sphereRadius - 1e-12);
  assert.equal(firstContact, out.samples.length - 1);
});

test('contact timing tracks analytic impact within one sample for supported timesteps', async () => {
  for (const dt of [0.005, 0.01, 0.02]) {
    const out = await contactAwareTrajectory({ trajectory: falling(dt), geometry, physics, gravity: 9.81 });
    const first = out.samples.find((s) => s.contact);
    const analytic = Math.sqrt((2 - geometry.floorY - geometry.sphereRadius) * 2 / 9.81);
    assert.ok(Math.abs(first.time_s - analytic) <= dt, `${dt}: ${first.time_s} vs ${analytic}`);
  }
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
  await assert.rejects(() => contactAwareTrajectory({ trajectory: falling(), geometry, physics }), /gravity/);
  const sparse = structuredClone(falling()); delete sparse.samples[1];
  await assert.rejects(() => contactAwareTrajectory({ trajectory: sparse, geometry, physics, gravity: 9.81 }), /dense/);
});

test('returned contact output is deeply immutable', async () => {
  const out = await contactAwareTrajectory({ trajectory: falling(0.02), geometry, physics, gravity: 9.81 });
  assert.ok(Object.isFrozen(out));
  assert.ok(Object.isFrozen(out.geometry));
  assert.ok(Object.isFrozen(out.samples));
  assert.ok(Object.isFrozen(out.samples.at(-1).contacts));
  assert.throws(() => { out.geometry.floorHalfExtents[0] = 99; }, /read only|Cannot assign/i);
  assert.throws(() => { out.samples[0].contacts.push({}); }, /read only|Cannot add property|is not extensible/i);
});
