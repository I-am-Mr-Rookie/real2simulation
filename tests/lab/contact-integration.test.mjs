import test from 'node:test';
import assert from 'node:assert/strict';
import { runContactAwareTrajectory } from '../../Build/simulator/contact-runs.mjs';
import { createReplayRecord } from '../../Build/simulator/replay.mjs';

test('both ballistic templates reach real contact through the common run adapter', async () => {
  for (const template of ['free_fall', 'projectile']) {
    const output = await runContactAwareTrajectory({ template, initialPosition: [0, 2, 0],
      initialVelocity: template === 'projectile' ? [1, 0, 0] : [0, 0, 0],
      gravity: 9.81, dt: 0.01, steps: 150, source: 'simulated', inputProvenance: 'synthetic',
      geometry: { floorY: 0, floorHalfExtents: [5, 0.1, 5], sphereRadius: 0.1 },
      physics: { friction: 0.4, restitution: 0, density: 1 } });
    assert.equal(output.samples.at(-1).contact, true);
    assert.ok(output.samples.length < 151);
    assert.equal(output.source, 'simulated');
    assert.equal(output.kind, template === 'free_fall' ? 'free-fall' : 'projectile');
  }
});

test('unsupported replay versions cannot produce unreplayable records', async () => {
  await assert.rejects(createReplayRecord({ seed: 0, version: 'unknown', parameters: {}, trace: [1] }), /metadata/);
});
