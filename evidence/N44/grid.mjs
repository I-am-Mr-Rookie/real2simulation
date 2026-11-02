
import R from '../../Build/web/node_modules/@dimforge/rapier3d-compat/dist/rapier.mjs';
import fs from 'node:fs';
import { validateScene } from '../../Build/web/src/lab-editor/scene.mjs';
import { createPhysics } from '../../Build/web/src/lab-editor/physics.mjs';
await R.init();
// usage: node grid.mjs <scene.json> <table ids comma> ; 3x3 grid at +-30% of the table's local x/z, ball r 0.025 from top+0.8
const [file, ids] = process.argv.slice(2);
const raw = JSON.parse(fs.readFileSync(file)); const s0 = validateScene(raw.scene ?? raw);
const base = s0.objects.filter(o => o.kind !== 'ball');
const out = {};
for (const id of ids.split(',')) {
  const t = base.find(o => o.id === id); const yaw = 2 * Math.atan2(t.rotation[1], t.rotation[3]);
  const top = t.position[1] + t.size[1] / 2; let held = 0; const runs = [];
  for (const i of [-1, 0, 1]) for (const j of [-1, 0, 1]) {
    const u = i * 0.3 * t.size[0], w = j * 0.3 * t.size[2];
    const p = [t.position[0] + u * Math.cos(yaw) + w * Math.sin(yaw), top + 0.8, t.position[2] - u * Math.sin(yaw) + w * Math.cos(yaw)];
    const ball = { id: 'b', kind: 'ball', position: p, size: [0.05, 0.05, 0.05], restitution: 0 };
    const sim = createPhysics(R, { ...validateScene({ ...s0, objects: [...base, ball] }), room: { kind: 'plane', floor_y: 0 } });
    sim.step(4 * 120); const e = sim.trace('b').samples.at(-1).p; sim.free();
    const ok = Math.abs(e[1] - (top + 0.025)) < 0.01; held += ok; runs.push({ grid: [i, j], end: e.map(x => +x.toFixed(4)), held: ok });
  }
  out[id] = { shape: t.shape?.type, top: +top.toFixed(4), held, of: 9, runs };
}
console.log(JSON.stringify(out));

