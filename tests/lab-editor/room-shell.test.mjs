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
