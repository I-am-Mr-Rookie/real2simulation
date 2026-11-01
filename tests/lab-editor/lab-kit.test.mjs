import { test } from 'node:test';
import assert from 'node:assert/strict';
import R from '../../Build/web/node_modules/@dimforge/rapier3d-compat/dist/rapier.mjs';
import { defaultScene, makeObject, validateScene, KINDS, PROBES, MASS_SET } from '../../Build/web/src/lab-editor/scene.mjs';
import { createPhysics } from '../../Build/web/src/lab-editor/physics.mjs';
import { emptyHistory, record, undo, redo, removeObject, typing } from '../../Build/web/src/lab-editor/history.mjs';

test('N33 kit kinds validate, play in Rapier and probes write lab-trace-v1', async () => {
  await R.init();
  const s = defaultScene();
  KINDS.forEach((k, i) => s.objects.push(makeObject(k, s, [i * 1.5, k === 'atwood' ? 1.6 : 1.2, 0])));
  const v = validateScene(JSON.parse(JSON.stringify(s)));
  assert.equal(v.objects.length, KINDS.length);
  const sim = createPhysics(R, v);
  sim.step(120);
  const poses = sim.poses();
  for (const k of ['flywheel', 'atwood', 'cart', 'cradle']) assert.ok(Array.isArray(poses[k + '-1'].parts), k + ' has parts');
  for (const k of PROBES) {
    const t = sim.trace(k + '-1');
    assert.equal(t.version, 'lab-trace-v1'); assert.equal(t.label, 'SIMULATED'); assert.ok(t.target, k + ' has a target');
  }
  assert.ok(sim.trace('ruler-1').samples.every((x) => Number.isFinite(x.value)));
  sim.free();
});

test('mass set derives mass and size from grams; bad kit params are rejected', () => {
  const s = defaultScene();
  const m = makeObject('mass', s); m.params.grams = MASS_SET[4];
  const v = validateScene({ ...s, objects: [m] }).objects[0];
  assert.equal(v.mass, 0.2); assert.ok(v.size[0] > 0.01 && v.size[0] < 0.05);
  const c = makeObject('cradle', s); c.params.count = 40;
  assert.throws(() => validateScene({ ...s, objects: [c] }), /count/);
  const a = makeObject('atwood', s); a.params.m3 = 1;
  assert.throws(() => validateScene({ ...s, objects: [a] }), /unknown field m3/);
});

test('undo/redo covers add, move and delete; delete removes one object', () => {
  const s0 = defaultScene();
  const s1 = { ...s0, objects: [makeObject('ball', s0), { ...makeObject('block', s0), id: 'room-chair' }] };
  const s2 = { ...s1, objects: s1.objects.map((o) => (o.id === 'ball-1' ? { ...o, position: [1, 1, 1] } : o)) };
  const s3 = removeObject(s2, 'room-chair');
  assert.deepEqual(s3.objects.map((o) => o.id), ['ball-1']);
  let h = record(record(record(emptyHistory(), s0), s1), s2);
  let u = undo(h, s3); assert.equal(u.scene, s2);
  u = undo(u.history, u.scene); assert.equal(u.scene, s1);
  const r = redo(u.history, u.scene); assert.equal(r.scene, s2);
  assert.equal(record(r.history, r.scene).future.length, 0, 'a new edit clears redo');
  assert.equal(undo(emptyHistory(), s0), null);
  assert.ok(typing({ tagName: 'TEXTAREA' }) && !typing({ tagName: 'CANVAS' }));
});
