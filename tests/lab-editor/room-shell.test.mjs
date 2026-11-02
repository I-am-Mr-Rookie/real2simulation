// N39: room shell scene (fixed wall pieces around an opening + a floor-reaching table box) in the shared Rapier world.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import R from '../../Build/web/node_modules/@dimforge/rapier3d-compat/dist/rapier.mjs';
import { validateScene } from '../../Build/web/src/lab-editor/scene.mjs';
import { createPhysics } from '../../Build/web/src/lab-editor/physics.mjs';

await R.init();
const wall = (id, position, size) => ({ id, kind: 'block', position, size, rotation: [0, 0, 0, 1], fixed: true, sensor: false, mass: 100, friction: 0.5 });
// wall at x = 2 with a door opening z in [-0.5, 0.5] up to y 2.0 (pieces as room_shell.wall_objects makes them)
const shell = validateScene({ version: 'lab-scene-v1', room: { kind: 'ply', floor_y: 0, source: 'room.ply', scale_verified: false, collision: { enabled: false, boxes: [] } }, objects: [
  wall('wall-1-1', [2.04, 1.25, -1.25], [0.08, 2.5, 1.5]), wall('wall-1-2', [2.04, 2.25, 0], [0.08, 0.5, 1.0]), wall('wall-1-3', [2.04, 1.25, 1.25], [0.08, 2.5, 1.5]),
  { ...wall('room-object-1', [0, 0.36, 0], [0.8, 0.72, 0.5]), mass: 25 }] });
const roll = (extra) => {
  const sim = createPhysics(R, { ...shell, room: { kind: 'plane', floor_y: 0 }, objects: [...shell.objects, { id: 'b', kind: 'ball', size: [0.1, 0.1, 0.1], restitution: 0.1, ...extra }] });
  sim.step(2 * 120);
  const p = sim.trace('b').samples.map((s) => s.p);
  sim.free();
  return p;
};
test('ball dropped on the floor-reaching table rests on its top', () => {
  const p = roll({ position: [0, 1.2, 0] });
  assert.ok(Math.abs(p.at(-1)[1] - 0.77) < 0.02, 'rest y ' + p.at(-1)[1]);
});
test('wall stops a rolling ball; the door opening lets it through', () => {
  const blocked = roll({ position: [1, 0.05, -1.2], velocity: [3, 0, 0] }), through = roll({ position: [1, 0.05, 0], velocity: [3, 0, 0] });
  assert.ok(Math.max(...blocked.map((s) => s[0])) < 2.0, 'blocked max x ' + Math.max(...blocked.map((s) => s[0])));
  assert.ok(Math.max(...through.map((s) => s[0])) > 2.2, 'opening max x ' + Math.max(...through.map((s) => s[0])));
});

// N42: SF3D table whose own top covers only one corner (N39 coffee table: the ball fell off); support.outline = the
// last 4 vertices (plan outline at the top) -> solid slab while fixed.
test('ball rests on an SF3D mesh table top through the support slab; without it, it falls', () => {
  const vertices = [-0.5, 0.5, -0.5, -0.3, 0.5, -0.5, -0.5, 0.5, -0.3, -0.5, -0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, 0.5, -0.5, 0.5, 0.5, 0.5, -0.5, 0.5, 0.5];
  const mesh = { type: 'mesh', label: 'MODEL-GENERATED shape', credit: 'Powered by Stability AI', category: 'table', glb: '/api/workspace/rooms/' + 'c'.repeat(32) + '/objects/room-object-1.glb',
    quarter_turns: 0, vertices, indices: [0, 1, 2, 0, 3, 4], support: { plane: 0.3, outline: 4 } };
  const table = { ...wall('room-object-1', [0, 0.36, 0], [0.8, 0.72, 0.5]), mass: 25, shape: mesh };
  const drop = (t) => {
    const s = validateScene({ ...shell, objects: [t] });
    const sim = createPhysics(R, { ...s, room: { kind: 'plane', floor_y: 0 }, objects: [...s.objects, { id: 'b', kind: 'ball', position: [0.2, 1.0, 0.1], size: [0.04, 0.04, 0.04], restitution: 0.3 }] });
    sim.step(3 * 120);
    const y = sim.trace('b').samples.at(-1).p[1];
    sim.free();
    return y;
  };
  assert.ok(Math.abs(drop(table) - 0.74) < 0.01, 'rest y ' + drop(table));
  const { support, ...bare } = mesh;
  assert.ok(drop({ ...table, shape: bare }) < 0.05, 'no slab: falls to the floor');
  assert.throws(() => validateScene({ ...shell, objects: [{ ...table, shape: { ...mesh, support: { plane: 0.3, outline: 99 } } }] }), /support/);
});

// N44 (N43 F1): the committed DEV RM02 scene; the ball dropped over the first SF3D table hit slanted trimesh triangles at
// the flattened top edge, slid and rolled to the floor. With those left to the slab it rests on the top.
test('N43 RM02 centre drop rests on the SF3D table top', async () => {
  const fs = await import('node:fs');
  const s = validateScene(JSON.parse(fs.readFileSync(new URL('../../evidence/N43/drop-scene.json', import.meta.url))));
  const sim = createPhysics(R, { ...s, room: { kind: 'plane', floor_y: 0 } });
  sim.step(4 * 120);
  const p = sim.trace('ball-1').samples.at(-1).p;
  sim.free();
  assert.ok(Math.abs(p[1] - (0.41735 + 0.025)) < 0.005 && Math.hypot(p[0] - 0.0839, p[2] + 1.7662) < 0.01, 'rest ' + p);
});
