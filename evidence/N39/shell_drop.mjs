// N39: drop a ball onto the detected table of the live room shell (owner room, private scene stays local) with the
// lab's own Rapier world: walls + kept furniture, dense room collision boxes off (the lab default). Numbers only.
// node evidence/N39/shell_drop.mjs <private scene.json> <table object id> -> evidence/N39/live/drop.json
import fs from 'fs';
import R from '../../Build/web/node_modules/@dimforge/rapier3d-compat/dist/rapier.mjs';
import { validateScene } from '../../Build/web/src/lab-editor/scene.mjs';
import { createPhysics } from '../../Build/web/src/lab-editor/physics.mjs';
await R.init();
const scene = validateScene(JSON.parse(fs.readFileSync(process.argv[2], 'utf8')));
const table = scene.objects.find((o) => o.id === process.argv[3]);
const top = table.position[1] + table.size[1] / 2, r = 0.02;
const ball = { id: 'ball', kind: 'ball', position: [table.position[0], top + 0.3, table.position[2]], size: [2 * r, 2 * r, 2 * r], restitution: 0.3 };
const drop = (objects) => {
  const sim = createPhysics(R, { ...scene, room: { kind: 'plane', floor_y: 0 }, objects: [...objects, ball] });
  sim.step(3 * 120);
  const p = sim.trace('ball').samples.map((s) => s.p);
  sim.free();
  const i = p.findIndex((s, k) => k > 0 && (Math.hypot(s[0] - ball.position[0], s[2] - ball.position[2]) > 0.002 || s[1] >= p[k - 1][1]));
  const end = p[p.length - 1], shift = Math.hypot(end[0] - ball.position[0], end[2] - ball.position[2]);
  return { first_contact_y: i < 0 ? null : Number(p[i][1].toFixed(4)), end: end.map((x) => Number(x.toFixed(4))),
    horizontal_shift: Number(shift.toFixed(4)), landed_on_table: i >= 0 && p[i][1] > r + 0.01, rests_on_table: end[1] > r + 0.01 && shift < Math.max(table.size[0], table.size[2]) / 2 };
};
const { shape, ...box } = table;
const out = { label: 'SIMULATED (Rapier); table geometry MODEL-ESTIMATED, scale unverified', table: table.id,
  table_top_y: Number(top.toFixed(4)), table_size: table.size, objects_in_scene: scene.objects.length,
  walls: scene.objects.filter((o) => o.id.startsWith('wall-')).length, ball_radius: r, drop_from_y: ball.position[1], seconds: 3,
  sf3d_mesh: table.shape?.type === 'mesh' ? drop(scene.objects) : null,
  measured_box: drop(scene.objects.map((o) => (o.id === table.id ? box : o))) };
fs.mkdirSync(new URL('./live/', import.meta.url), { recursive: true });
fs.writeFileSync(new URL('./live/drop.json', import.meta.url), JSON.stringify(out, null, 1) + '\n');
console.log(JSON.stringify(out));
