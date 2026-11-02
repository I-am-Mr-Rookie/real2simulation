// Verify the actual public RM02 shell and its unchanged table-top colliders, not a hand-built lookalike.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import R from '../../Build/web/node_modules/@dimforge/rapier3d-compat/dist/rapier.mjs';
import { validateScene } from '../../Build/web/src/lab-editor/scene.mjs';
import { createPhysics } from '../../Build/web/src/lab-editor/physics.mjs';

await R.init();
const dir = process.argv[2] || 'evidence/N52/rm02';
const scene = validateScene(JSON.parse(fs.readFileSync(dir + '/scene.json')));
const shell = JSON.parse(fs.readFileSync(dir + '/shell.json'));
const chairs = scene.objects.filter(o => o.look?.category === 'chair');
const tables = scene.objects.filter(o => ['table', 'desk'].includes(o.look?.category));
assert.ok(chairs.length && tables.length);
for (const chair of chairs) {
  const [r, g, b] = chair.look.color.slice(1).match(/../g).map(v => parseInt(v, 16));
  assert.ok(g > r + 10 && g > b, 'source-green chair ' + chair.id);
  assert.ok(chair.size[0] <= 0.85 && chair.size[2] <= 0.85, 'chair size prior ' + chair.id);
  const table = tables.toSorted((a, b) => Math.hypot(a.position[0] - chair.position[0], a.position[2] - chair.position[2])
    - Math.hypot(b.position[0] - chair.position[0], b.position[2] - chair.position[2]))[0];
  const yaw = 2 * Math.atan2(chair.rotation[1], chair.rotation[3]);
  assert.ok(Math.sin(yaw) * (table.position[0] - chair.position[0]) + Math.cos(yaw) * (table.position[2] - chair.position[2]) > 0);
}
assert.ok(shell.openings.some(h => shell.walls[h.wall].status === 'EXTENT'));
const roomYaw = shell.yaw_deg * Math.PI / 180;
for (const item of scene.objects.filter(o => o.id.startsWith('room-object-'))) {
  const yaw = 2 * Math.atan2(item.rotation[1], item.rotation[3]);
  for (const x of [-0.5, 0.5]) for (const z of [-0.5, 0.5]) {
    const px = item.position[0] + x * item.size[0] * Math.cos(yaw) + z * item.size[2] * Math.sin(yaw);
    const pz = item.position[2] - x * item.size[0] * Math.sin(yaw) + z * item.size[2] * Math.cos(yaw);
    const uv = [px * Math.cos(roomYaw) - pz * Math.sin(roomYaw), px * Math.sin(roomYaw) + pz * Math.cos(roomYaw)];
    for (const wall of shell.walls) assert.ok(uv[wall.axis] * wall.side <= wall.plane * wall.side + 0.01, 'furniture inside wall ' + item.id);
  }
}
const drops = tables.map(table => {
  assert.ok(table.size[0] <= 1.89 && table.size[2] <= 1.155, 'desk size prior ' + table.id);
  const top = table.position[1] + table.size[1] / 2;
  const ball = { id: 'n52-drop', kind: 'ball', position: [table.position[0], top + 0.4, table.position[2]], size: [0.05, 0.05, 0.05], restitution: 0.1 };
  const sim = createPhysics(R, validateScene({ ...scene, objects: [...scene.objects, ball] }));
  sim.step(3 * 120);
  const y = sim.trace(ball.id).samples.at(-1).p[1];
  sim.free();
  assert.ok(Math.abs(y - top - 0.025) < 0.01, 'ball rests on actual table ' + table.id + ': ' + y);
  return { table: table.id, top_m: top, expected_rest_y_m: top + 0.025, simulated_rest_y_m: y };
});
const result = { label: 'SIMULATED, room scale unverified', chairs: chairs.length, tables: tables.length, openings: shell.openings.length, drops };
fs.writeFileSync(dir + '/ball-rest.json', JSON.stringify(result, null, 1) + '\n');
console.log(JSON.stringify(result));
