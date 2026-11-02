// Actual generated tables, full-scene versus isolated support, SIMULATED only.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import R from '../../Build/web/node_modules/@dimforge/rapier3d-compat/dist/rapier.mjs';
import { validateScene } from '../../Build/web/src/lab-editor/scene.mjs';
import { createPhysics } from '../../Build/web/src/lab-editor/physics.mjs';

await R.init();
const scene = validateScene(JSON.parse(fs.readFileSync(process.argv[2])));
const tables = scene.objects.filter(o => ['table', 'desk'].includes(o.look?.category));
const drops = tables.map(table => {
  const top = table.position[1] + table.size[1] / 2;
  const ball = { id: 'n53-drop', kind: 'ball', position: [table.position[0], top + 0.4, table.position[2]],
    size: [0.05, 0.05, 0.05], restitution: 0.1 };
  const run = objects => {
    const sim = createPhysics(R, validateScene({ ...scene, objects: [...objects, ball] }));
    sim.step(3 * 120);
    const last = sim.trace(ball.id).samples.at(-1).p;
    sim.free();
    return { position: last, rests_on_table: Math.abs(last[1] - top - 0.025) < 0.01 };
  };
  return { table: table.id, expected_y: top + 0.025, full_scene: run(scene.objects), isolated_table: run([table]) };
});
assert.ok(tables.length);
assert.ok(drops.every(d => d.isolated_table.rests_on_table), 'actual table colliders must support the isolated ball');
const result = { label: 'SIMULATED, scale unverified; full-scene failures remain findings',
  tables: tables.length, isolated_passed: drops.filter(d => d.isolated_table.rests_on_table).length,
  full_scene_passed: drops.filter(d => d.full_scene.rests_on_table).length, drops };
fs.writeFileSync(process.argv[3], JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify(result));
