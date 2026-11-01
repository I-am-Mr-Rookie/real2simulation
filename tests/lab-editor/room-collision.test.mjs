// N29: room collision proxy from a point cloud (MODEL-ESTIMATED boxes) in the shared Rapier world.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import R from '../../Build/web/node_modules/@dimforge/rapier3d-compat/dist/rapier.mjs';
import { validateScene, keepAdded } from '../../Build/web/src/lab-editor/scene.mjs';
import { createPhysics, roomProxy } from '../../Build/web/src/lab-editor/physics.mjs';

await R.init();
let seed = 7;
const rnd = (lo, hi) => { seed = (seed * 1103515245 + 12345) % 2147483648; return lo + (hi - lo) * (seed / 2147483648); };
const fill = (pts, n, [x0, x1], [y0, y1], [z0, z1]) => { for (let i = 0; i < n; i += 1) pts.push(rnd(x0, x1), rnd(y0, y1), rnd(z0, z1)); };
// 4 m room: floor, a table-shaped box cluster (top at 0.8 m), a wall at x = 2, and stray points.
const cloud = () => {
  const pts = [];
  fill(pts, 6000, [-2, 2], [-0.01, 0.01], [-2, 2]);
  fill(pts, 3000, [-0.5, 0.5], [0.6, 0.8], [-0.4, 0.4]);
  fill(pts, 4000, [1.95, 2.05], [0, 2.5], [-2, 2]);
  fill(pts, 20, [-3, 3], [0, 3], [-3, 3]);
  return new Float32Array(pts);
};
const room = (collision) => ({ kind: 'ply', floor_y: 0, source: 'room.ply', scale_verified: false, collision });
const run = (collision, ball, seconds) => {
  const sim = createPhysics(R, { version: 'lab-scene-v1', room: room(collision), objects: [{ id: 'b', kind: 'ball', size: [0.1, 0.1, 0.1], restitution: 0.1, ...ball }] });
  sim.step(Math.round(seconds * 120));
  const t = sim.trace('b');
  sim.free();
  return t.samples;
};

test('proxy is a capped, valid MODEL-ESTIMATED box set', () => {
  const c = roomProxy(cloud());
  assert.equal(c.label, 'MODEL-ESTIMATED');
  assert.ok(c.boxes.length > 0 && c.boxes.length <= 300, String(c.boxes.length));
  assert.deepEqual(validateScene({ version: 'lab-scene-v1', room: room(c) }).room.collision.boxes, c.boxes);
  assert.equal(roomProxy(new Float32Array(30)), null);
  const tiny = roomProxy(cloud(), [0, -9.81, 0], 0, 3);
  assert.ok(tiny === null || tiny.boxes.length <= 3);
});

test('ball dropped above the table lands on it; without collisions it reaches the floor', () => {
  const c = roomProxy(cloud());
  const on = run(c, { position: [0, 1.5, 0] }, 2).at(-1).p[1];
  assert.ok(on > 0.7 && on < 1.0, 'rests on the table top: ' + on);
  const off = run({ ...c, enabled: false }, { position: [0, 1.5, 0] }, 2).at(-1).p[1];
  assert.ok(Math.abs(off - 0.05) < 0.01, 'rests on the floor: ' + off);
});

test('the wall stops a rolling ball', () => {
  const c = roomProxy(cloud());
  const xs = run(c, { position: [1.0, 0.05, 1.5], velocity: [3, 0, 0] }, 3).map((s) => s.p[0]);
  assert.ok(Math.max(...xs) < 2.0, 'max x ' + Math.max(...xs));
  assert.ok(run({ ...c, enabled: false }, { position: [1.0, 0.05, 1.5], velocity: [3, 0, 0] }, 3).at(-1).p[0] > 2.5);
});

test('validator rejects bad proxies', () => {
  const ok = { boxes: [[0, 1, 0, 0.1, 0.1, 0.1]] };
  assert.throws(() => validateScene({ version: 'lab-scene-v1', room: { kind: 'plane', collision: ok } }), /needs room.kind ply/);
  assert.throws(() => validateScene({ version: 'lab-scene-v1', room: room({ boxes: [[0, 1, 0, 0, 0.1, 0.1]] }) }), /half size/);
  assert.throws(() => validateScene({ version: 'lab-scene-v1', room: room({ boxes: Array(401).fill(ok.boxes[0]) }) }), /at most 400/);
  assert.throws(() => validateScene({ version: 'lab-scene-v1', room: room({ ...ok, extra: 1 }) }), /unknown room.collision field/);
  assert.equal(validateScene({ version: 'lab-scene-v1', room: room(ok) }).room.collision.enabled, true);
});

test('A4 rescale keeps user-added objects, positions scaled with the room', () => {
  const server = [{ id: 'chair-1', position: [2, 0.5, 0] }];
  const cur = [{ id: 'chair-1', position: [1, 0.25, 0] }, { id: 'ball-1', position: [1, 2, -3] }];
  assert.deepEqual(keepAdded(cur, server, 0.5), [server[0], { id: 'ball-1', position: [0.5, 1, -1.5] }]);
  assert.deepEqual(keepAdded(cur, server, NaN), server); // first load of a room: server scene only
});
