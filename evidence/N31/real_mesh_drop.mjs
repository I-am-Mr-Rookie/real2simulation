// N31: the live SF3D table (owner room, private) as the Rapier collider vs its measured box: a ball dropped over a grid
// of points; first contact height (ball centre when first pushed sideways or stopped) for mesh and box. Numbers only.
// node evidence/N31/real_mesh_drop.mjs <private scene.json> <object id>  -> evidence/N31/live/drop.json
import fs from 'fs';
import R from '../../Build/web/node_modules/@dimforge/rapier3d-compat/dist/rapier.mjs';
import { createPhysics } from '../../Build/web/src/lab-editor/physics.mjs';
await R.init();
const scene = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const obj = scene.objects.find((o) => o.id === process.argv[3]);
const top = obj.position[1] + obj.size[1] / 2 + 0.3;
const rows = [];
for (const fx of [-0.4, -0.2, 0, 0.2, 0.4]) for (const fz of [-0.4, 0, 0.4]) {
  const q = obj.rotation, yaw = 2 * Math.atan2(q[1], q[3]);
  const lx = fx * obj.size[0], lz = fz * obj.size[2];
  const at = [obj.position[0] + lx * Math.cos(yaw) + lz * Math.sin(yaw), top, obj.position[2] - lx * Math.sin(yaw) + lz * Math.cos(yaw)];
  const contact = (o) => {
    const sim = createPhysics(R, { version: 'lab-scene-v1', room: { kind: 'plane', floor_y: Math.min(0, obj.position[1] - obj.size[1]) },
      objects: [o, { id: 'ball', kind: 'ball', position: at, size: [0.04, 0.04, 0.04], restitution: 0.5 }] });
    sim.step(120);
    const p = sim.trace('ball').samples.map((s) => s.p);
    sim.free();
    const i = p.findIndex((s, k) => k > 0 && (Math.hypot(s[0] - at[0], s[2] - at[2]) > 0.002 || s[1] >= p[k - 1][1]));
    return i < 0 ? null : Number(p[i][1].toFixed(4));
  };
  const { shape, ...box } = obj;
  rows.push({ local: [fx, fz], mesh_contact_y: contact(obj), box_contact_y: contact(box) });
}
const out = { label: 'SIMULATED (Rapier), shape MODEL-GENERATED, scale unverified', object: obj.id, size: obj.size,
  triangles: obj.shape.indices.length / 3, vertices: obj.shape.vertices.length / 3, box_top_y: obj.position[1] + obj.size[1] / 2,
  ball_radius: 0.02, rows, differing: rows.filter((r) => r.mesh_contact_y !== r.box_contact_y).length };
fs.mkdirSync(new URL('./live/', import.meta.url), { recursive: true });
fs.writeFileSync(new URL('./live/drop.json', import.meta.url), JSON.stringify(out, null, 1) + '\n');
console.log(JSON.stringify(out));

