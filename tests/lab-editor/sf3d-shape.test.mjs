// N31: Stable Fast 3D shape on a block: validated like the server writes it, and it is the Rapier collider (not the box).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import R from '../../Build/web/node_modules/@dimforge/rapier3d-compat/dist/rapier.mjs';
import { validateScene, parseScene, sceneJson } from '../../Build/web/src/lab-editor/scene.mjs';
import { createPhysics } from '../../Build/web/src/lab-editor/physics.mjs';

await R.init();
// Unit-box pyramid (object_lift.fit_mesh output form): base y = -0.5, apex (0, 0.5, 0).
const pyramid = (extra = {}) => ({ type: 'mesh', label: 'MODEL-GENERATED shape', credit: 'Powered by Stability AI', category: 'desk',
  glb: '/api/workspace/rooms/abc123/objects/room-object-1.glb', quarter_turns: 2,
  vertices: [-0.5, -0.5, -0.5, 0.5, -0.5, -0.5, 0.5, -0.5, 0.5, -0.5, -0.5, 0.5, 0, 0.5, 0],
  indices: [0, 2, 1, 0, 3, 2, 0, 1, 4, 1, 2, 4, 2, 3, 4, 3, 0, 4], ...extra });
const scene = (shape, fixed = true) => ({ version: 'lab-scene-v1', room: { kind: 'plane', floor_y: 0 }, objects: [
  { id: 'room-object-1', kind: 'block', position: [0, 0.5, 0], size: [1, 1, 1], fixed, sensor: false, ...(shape && { shape }) },
  { id: 'ball', kind: 'ball', position: [0.4, 1.5, 0.4], size: [0.1, 0.1, 0.1], restitution: 0.5 }] });
const drop = (s, seconds = 1.5) => {
  const sim = createPhysics(R, s);
  sim.step(Math.round(seconds * 120));
  const p = sim.trace('ball').samples.map((x) => x.p);
  sim.free();
  return p;
};

test('mesh and box shapes validate; bad ones are rejected', () => {
  const s = validateScene(scene(pyramid()));
  assert.equal(s.objects[0].shape.type, 'mesh');
  assert.deepEqual(validateScene(JSON.parse(sceneJson(s))).objects[0].shape, s.objects[0].shape);
  assert.equal(validateScene(scene({ type: 'box', fallback_reason: 'SF3D failed: no GPU' })).objects[0].shape.fallback_reason, 'SF3D failed: no GPU');
  for (const bad of [pyramid({ credit: 'Stability' }), pyramid({ glb: 'https://evil.example/x.glb' }), pyramid({ indices: [0, 1, 9] }),
    pyramid({ vertices: [0.9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] }), pyramid({ collider: 'x' }), { type: 'sphere' }]) {
    assert.throws(() => validateScene(scene(bad)));
  }
  assert.throws(() => validateScene({ ...scene(), objects: [{ id: 'b', kind: 'ball', shape: pyramid() }] }));
  assert.ok(parseScene(JSON.stringify(scene(pyramid()))));
});

test('ball dropped near a corner bounces off the mesh, not the box', () => {
  // Box top is y = 1; the pyramid surface under (0.4, 0.4) is at y = 0.2 (+ ball radius 0.05).
  // Contact = first sample pushed sideways (the ball falls straight until it touches a slope).
  const box = drop(scene(null)), mesh = drop(scene(pyramid()));
  const hit = mesh.find((p) => Math.hypot(p[0] - 0.4, p[2] - 0.4) > 0.01);
  assert.ok(Math.min(...box.map((p) => p[1])) > 0.99, 'box fallback stops the ball on the box top');
  assert.ok(hit[1] > 0.15 && hit[1] < 0.45, 'the mesh slope deflects the ball at y ' + hit[1]);
  assert.ok(Math.hypot(mesh.at(-1)[0], mesh.at(-1)[2]) > Math.hypot(0.4, 0.4) + 0.05, 'the slope sends the ball outward');
});

test('movable mesh object gets a convex hull collider and falls to the floor', () => {
  const s = scene(pyramid({ category: 'box' }), false);
  s.objects[0].position = [0, 2, 0];
  const sim = createPhysics(R, { ...s, objects: [{ ...s.objects[0], sensor: true }] });
  sim.step(240);
  const y = sim.trace('room-object-1').samples.at(-1).p[1];
  sim.free();
  assert.ok(Math.abs(y - 0.5) < 0.05, 'pyramid hull rests with its centre 0.5 m up: ' + y);
});

