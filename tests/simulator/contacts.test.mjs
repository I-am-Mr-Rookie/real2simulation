import test from 'node:test';
import assert from 'node:assert/strict';
import { freeFallTrajectory } from '../../Build/simulator/trajectories.mjs';
import { contactAwareTrajectory } from '../../Build/simulator/contacts.mjs';

const physics = { friction: 0.4, restitution: 0, density: 1 };
const geometry = { floorY: 0, floorHalfExtents: [5, 0.1, 5], sphereRadius: 0.1 };
const falling = (dt = 0.005) => freeFallTrajectory({ initialPosition: [0, 2, 0], initialVelocity: [0, 0, 0], gravity: 9.81, dt, steps: Math.round(2 / dt), source: 'simulated', inputProvenance: 'synthetic' });

test('real Rapier contact is mapped onto the same RK4 samples', async () => {
  const out = await contactAwareTrajectory({ trajectory: falling(), geometry, physics, gravity: 9.81 });
  assert.ok(out.samples.length < 201);
  assert.equal(out.contactEngine, 'rapier3d-compat-0.21.0');
  assert.ok(out.samples.some((s) => s.contact));
  assert.deepEqual(out.samples[20].position_m, falling().samples[20].position_m);
  const firstContact = out.samples.findIndex((s) => s.contact);
  assert.ok(firstContact > 0);
  assert.ok(out.samples.some((sample) => sample.contacts.some((contact) => contact.colliderA === 'sphere')));
  assert.ok(out.samples[firstContact].position_m[1] - geometry.floorY <= geometry.sphereRadius);
  assert.equal(firstContact, out.samples.length - 1);
});

test('contact timing tracks analytic impact within one sample for supported timesteps', async () => {
  for (const dt of [0.005, 0.0025, 0.001]) {
    const out = await contactAwareTrajectory({ trajectory: falling(dt), geometry, physics, gravity: 9.81 });
    const first = out.samples.find((s) => s.contact);
    const analytic = Math.sqrt((2 - geometry.floorY - geometry.sphereRadius) * 2 / 9.81);
    assert.ok(Math.abs(first.time_s - analytic) <= dt, `${dt}: ${first.time_s} vs ${analytic}`);
    assert.ok(first.contactBracket_s[0] <= analytic && analytic <= first.contactBracket_s[1]);
  }
});

test('no-contact trajectory remains no-contact and deterministic', async () => {
  const input = { trajectory: freeFallTrajectory({ initialPosition: [0, 10, 0], initialVelocity: [0, 0, 0], gravity: 9.81, dt: 0.01, steps: 2, source: 'simulated', inputProvenance: 'synthetic' }), geometry, physics, gravity: 9.81 };
  const [a, b] = await Promise.all([contactAwareTrajectory(input), contactAwareTrajectory(input)]);
  assert.deepEqual(a, b); assert.ok(a.samples.every((s) => !s.contact));
});

test('rejects invalid explicit physics and geometry', async () => {
  await assert.rejects(() => contactAwareTrajectory({ trajectory: falling(0.1), geometry, physics, gravity: 9.81 }), /excessive displacement/);
  await assert.rejects(() => contactAwareTrajectory({ trajectory: falling(), geometry, physics: { ...physics, restitution: 2 }, gravity: 9.81 }), /restitution/);
  await assert.rejects(() => contactAwareTrajectory({ trajectory: falling(), geometry: { ...geometry, sphereRadius: 0 }, physics, gravity: 9.81 }), /sphereRadius/);
  await assert.rejects(() => contactAwareTrajectory({ trajectory: falling(), geometry, physics: { ...physics, friction: Number.NaN }, gravity: 9.81 }), /friction/);
  await assert.rejects(() => contactAwareTrajectory({ trajectory: falling(), geometry, physics }), /gravity/);
  const sparse = structuredClone(falling()); delete sparse.samples[1];
  await assert.rejects(() => contactAwareTrajectory({ trajectory: sparse, geometry, physics, gravity: 9.81 }), /dense/);
  await assert.rejects(() => contactAwareTrajectory({ trajectory: { ...falling(), source: 'measured' }, geometry, physics, gravity: 9.81 }), /source labels/);
  const badClock = structuredClone(falling()); badClock.samples[2].time_s += 0.001;
  await assert.rejects(() => contactAwareTrajectory({ trajectory: badClock, geometry, physics, gravity: 9.81 }), /step\/time/);
});

test('returned contact output is deeply immutable', async () => {
  const out = await contactAwareTrajectory({ trajectory: falling(), geometry, physics, gravity: 9.81 });
  assert.ok(Object.isFrozen(out));
  assert.ok(Object.isFrozen(out.geometry));
  assert.ok(Object.isFrozen(out.samples));
  assert.ok(Object.isFrozen(out.samples.at(-1).contacts));
  assert.ok(Object.isFrozen(out.samples[0].position_m));
  assert.ok(Object.isFrozen(out.samples[0].velocity_m_s));
  assert.ok(Object.isFrozen(out.samples.at(-1).contactBracket_s));
  assert.notStrictEqual(out.samples[0].position_m, falling().samples[0].position_m);
  assert.throws(() => { out.geometry.floorHalfExtents[0] = 99; }, /read only|Cannot assign/i);
  assert.throws(() => { out.samples[0].contacts.push({}); }, /read only|Cannot add property|is not extensible/i);
});

const initialOnly = (y = 2, dt = 0.005) => freeFallTrajectory({ initialPosition: [0, y, 0],
  initialVelocity: [0, 0, 0], gravity: 9.81, dt, steps: 0,
  source: 'simulated', inputProvenance: 'synthetic' });

test('rejects overflow of the derived floor center from finite operands', async () => {
  await assert.rejects(() => contactAwareTrajectory({ trajectory: initialOnly(), physics, gravity: 9.81,
    geometry: { ...geometry, floorY: -1e308, floorHalfExtents: [5, 1e308, 5] } }), /floor center.*finite/);
});

test('rejects initial penetration instead of fabricating a zero-time contact bracket', async () => {
  for (const y of [0.05, 0.1 - Number.EPSILON, -1]) {
    await assert.rejects(() => contactAwareTrajectory({ trajectory: initialOnly(y), geometry, physics, gravity: 9.81 }), /initial.*penetrat/);
  }
});

test('true initial touch is supported without treating a just-above start as contact', async () => {
  for (const floor of [geometry, { ...geometry, floorY: 0.25, sphereRadius: 0.125 }]) {
    const y = floor.floorY + floor.sphereRadius;
    const out = await contactAwareTrajectory({ trajectory: initialOnly(y), geometry: floor, physics, gravity: 9.81 });
    assert.equal(out.samples.length, 1);
    assert.equal(out.samples[0].contact, true);
    assert.deepEqual(out.samples[0].contactBracket_s, [0, 0]);
    assert.deepEqual(out.samples[0].position_m, [0, y, 0]);
    const above = await contactAwareTrajectory({ trajectory: initialOnly(y + Number.EPSILON), geometry: floor, physics, gravity: 9.81 });
    assert.equal(above.samples[0].contact, false);
    assert.equal(above.samples[0].contactBracket_s, null);
  }
});

test('finite JavaScript inputs cannot overflow or collapse positive Rapier float32 inputs', async () => {
  const input = { trajectory: initialOnly(), geometry, physics, gravity: 9.81 };
  const cases = [
    ['floor center', { geometry: { ...geometry, floorY: -1e40 } }],
    ['floor extents', { geometry: { ...geometry, floorHalfExtents: [1e40, 0.1, 5] } }],
    ['floor thickness', { geometry: { ...geometry, floorHalfExtents: [5, 1e-50, 5] } }],
    ['radius overflow', { geometry: { ...geometry, sphereRadius: 1e40 } }],
    ['radius underflow', { geometry: { ...geometry, sphereRadius: 1e-50 } }],
    ['friction', { physics: { ...physics, friction: 1e40 } }],
    ['density overflow', { physics: { ...physics, density: 1e40 } }],
    ['density underflow', { physics: { ...physics, density: 1e-50 } }],
    ['gravity overflow', { gravity: 1e40 }],
    ['gravity underflow', { gravity: 1e-50 }],
    ['timestep overflow', { trajectory: initialOnly(2, 1e40) }],
    ['timestep underflow', { trajectory: initialOnly(2, 1e-50) }],
    ['initial position', { trajectory: initialOnly(1e40) }],
  ];
  for (const [name, overrides] of cases) {
    await assert.rejects(() => contactAwareTrajectory({ ...input, ...overrides }), /float32/, name);
  }
  const laterOverflow = structuredClone(falling());
  laterOverflow.samples[1].position_m[1] = 1e40;
  await assert.rejects(() => contactAwareTrajectory({ ...input, trajectory: laterOverflow }), /float32/);
});
