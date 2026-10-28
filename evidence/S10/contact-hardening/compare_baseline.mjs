import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { freeFallTrajectory, projectileTrajectory } from '../../../Build/simulator/trajectories.mjs';
import { contactAwareTrajectory } from '../../../Build/simulator/contacts.mjs';
import { createReplayRecord, stableHash } from '../../../Build/simulator/replay.mjs';

const root = new URL('../../../', import.meta.url);
const source = execFileSync('git', ['show', '0db90ba:Build/simulator/contacts.mjs'], { cwd: root, encoding: 'utf8' });
const rapier = new URL('../../../Build/simulator/node_modules/@dimforge/rapier3d-compat/dist/rapier.mjs', import.meta.url);
const baseline = await import(`data:text/javascript;base64,${Buffer.from(source.replace(
  "import RAPIER from '@dimforge/rapier3d-compat';", `import RAPIER from '${rapier.href}';`)).toString('base64')}`);
const geometry = { floorY: 0, floorHalfExtents: [5, 0.1, 5], sphereRadius: 0.1 };
const physics = { friction: 0.4, restitution: 0, density: 1 };
const rows = [];
for (const template of ['free_fall', 'projectile']) {
  for (const [name, y, dt, steps] of [
    ['contact-5ms', 2, 0.005, 400], ['contact-2.5ms', 2, 0.0025, 800],
    ['contact-1ms', 2, 0.001, 2000], ['initial-touch', 0.1, 0.005, 0],
    ['no-contact', 10, 0.01, 2],
  ]) {
    const trajectory = (template === 'free_fall' ? freeFallTrajectory : projectileTrajectory)({
      initialPosition: [0, y, 0], initialVelocity: template === 'projectile' ? [1, 0, 0] : [0, 0, 0],
      gravity: 9.81, dt, steps, source: 'simulated', inputProvenance: 'synthetic' });
    const parameters = { trajectory, geometry, physics, gravity: 9.81 };
    const before = await baseline.contactAwareTrajectory(parameters);
    const after = await contactAwareTrajectory(parameters);
    assert.deepEqual(after, before);
    const oldRecord = await createReplayRecord({ seed: 7, parameters, trace: before.samples });
    const newRecord = await createReplayRecord({ seed: 7, parameters, trace: after.samples });
    assert.deepEqual(newRecord, oldRecord);
    const otherSeed = await createReplayRecord({ seed: 8, parameters, trace: after.samples });
    assert.notEqual(otherSeed.replayHash, newRecord.replayHash);
    rows.push({ template, case: name, fullOutputIdentical: true, replayRecordIdentical: true,
      seedBound: true, outputHash: await stableHash(after), replayHash: newRecord.replayHash });
  }
}
console.log(JSON.stringify({ baseline: '0db90bae35d9dd1c9c23a032644e0311fb843975', rows }, null, 2));
