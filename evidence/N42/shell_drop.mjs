// N42: drop balls on a grid over the top of each support item (table/shelf) of a room shell scene, with the lab's own
// Rapier world (walls + kept furniture, dense room collision off). SF3D mesh vs measured box. Numbers only.
// node evidence/N42/shell_drop.mjs <private scene.json> [out.json]
import fs from 'fs';
import R from '../../Build/web/node_modules/@dimforge/rapier3d-compat/dist/rapier.mjs';
import { validateScene } from '../../Build/web/src/lab-editor/scene.mjs';
import { createPhysics } from '../../Build/web/src/lab-editor/physics.mjs';
await R.init();
const scene = validateScene(JSON.parse(fs.readFileSync(process.argv[2], 'utf8')));
const r = 0.02, G = 3; // 3 x 3 drop points over the middle 60% of the top
const drop = (objects, t, k) => {
  const top = t.position[1] + t.size[1] / 2, q = t.rotation ?? [0, 0, 0, 1], yaw = 2 * Math.atan2(q[1], q[3]);
  const u = ((k % G) / (G - 1) - 0.5) * 0.6 * t.size[0], w = (Math.floor(k / G) / (G - 1) - 0.5) * 0.6 * t.size[2];
  const x = t.position[0] + u * Math.cos(yaw) + w * Math.sin(yaw), z = t.position[2] - u * Math.sin(yaw) + w * Math.cos(yaw);
  const ball = { id: 'ball', kind: 'ball', position: [x, top + 0.3, z], size: [2 * r, 2 * r, 2 * r], restitution: 0.3 };
  const sim = createPhysics(R, { ...scene, room: { kind: 'plane', floor_y: 0 }, objects: [...objects, ball] });
  sim.step(3 * 120);
  const end = sim.trace('ball').samples.at(-1).p;
  sim.free();
  return { end_y: Number(end[1].toFixed(4)), rests_on_top: end[1] > r + 0.01 && Math.abs(end[1] - top - r) < 0.03 };
};
const items = scene.objects.filter((o) => o.shape?.type === 'mesh' && ['table', 'desk', 'shelf', 'cabinet'].includes(o.shape.category));
const out = { label: 'SIMULATED (Rapier); geometry MODEL-ESTIMATED, scale unverified', ball_radius: r, grid: G * G, seconds: 3, items: items.map((t) => {
  const { shape, ...box } = t;
  const run = (objs) => { const d = Array.from({ length: G * G }, (_, k) => drop(objs, t, k)); return { held: d.filter((x) => x.rests_on_top).length, end_y: d.map((x) => x.end_y) }; };
  return { id: t.id, category: shape.category, top_y: Number((t.position[1] + t.size[1] / 2).toFixed(4)), size: t.size,
    sf3d_mesh: run(scene.objects), measured_box: run(scene.objects.map((o) => (o.id === t.id ? box : o))) };
}) };
if (process.argv[3]) fs.writeFileSync(process.argv[3], JSON.stringify(out, null, 1) + '\n');
console.log(JSON.stringify(out));

