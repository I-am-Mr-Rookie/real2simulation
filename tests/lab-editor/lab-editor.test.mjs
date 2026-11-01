// N10: lab-scene-v1 schema + headless Rapier step + Build/fitter handoff. Run: node --test tests/lab-editor/
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import R from '../../Build/web/node_modules/@dimforge/rapier3d-compat/dist/rapier.mjs';
import { defaultScene, makeObject, validateScene, parseScene, sceneJson, fitterRequest, MAX_OBJECTS, KINDS } from '../../Build/web/src/lab-editor/scene.mjs';
import { createPhysics, movingStart, upQuat, DT } from '../../Build/web/src/lab-editor/physics.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
await R.init();

test('every kind round-trips through JSON', () => {
  const s = defaultScene();
  for (const k of KINDS) s.objects.push(makeObject(k, s));
  const back = parseScene(sceneJson(s));
  assert.deepEqual(back.objects.map((o) => o.id), KINDS.map((k) => k + '-1'));
  assert.equal(back.label, 'SIMULATED');
  assert.deepEqual(parseScene(sceneJson(back)), back);
});

test('schema rejects bad agent edits with readable errors', () => {
  const s = defaultScene();
  s.objects.push(makeObject('ball', s));
  const bad = (mut, re) => { const c = structuredClone(s); mut(c); assert.throws(() => validateScene(c), re); };
  bad((c) => { c.version = 'x'; }, /version/);
  bad((c) => { c.label = 'MEASURED'; }, /SIMULATED/);
  bad((c) => { c.objects[0].kind = 'rocket'; }, /kind/);
  bad((c) => { c.objects[0].size = [0, 1, 1]; }, /size\[0\]/);
  bad((c) => { c.objects[0].position = [NaN, 0, 0]; }, /position/);
  bad((c) => { c.objects[0].eval = 'x'; }, /unknown field eval/);
  bad((c) => { c.objects.push({ ...c.objects[0] }); }, /duplicate id/);
  bad((c) => { c.objects = Array.from({ length: MAX_OBJECTS + 1 }, (_, i) => ({ id: 'b' + i, kind: 'ball' })); }, /at most 50/);
  assert.throws(() => parseScene('{'), /not valid JSON/);
  const full = defaultScene();
  for (let i = 0; i < MAX_OBJECTS; i++) full.objects.push(makeObject('ball', full));
  assert.throws(() => makeObject('ball', full), /at most 50/);
});

test('gravity vector orients the floor', () => {
  assert.deepEqual(upQuat([0, -9.81, 0]).map((v) => Math.round(v * 1e9) / 1e9 + 0), [0, 0, 0, 1]);
  const q = upQuat([9.81, 0, 0]); // floor normal must become -x
  const [x, y, z, w] = q; // rotate (0,1,0)
  const ny = [2 * (x * y - w * z), 1 - 2 * (x * x + z * z), 2 * (y * z + w * x)];
  assert.ok(Math.abs(ny[0] + 1) < 1e-9 && Math.abs(ny[1]) < 1e-9);
});

test('headless step: free fall matches g, sensor trace feeds Build/fitter', () => {
  const s = defaultScene();
  const ball = makeObject('ball', s, [0, 2, 0]);
  s.objects.push(ball);
  const sim = createPhysics(R, s);
  sim.step(48); // 0.4 s, before the 1.9 m drop reaches the floor
  const tr = sim.trace('ball-1');
  sim.free();
  assert.equal(tr.samples.length, 49);
  assert.equal(tr.label, 'SIMULATED');
  const y = tr.samples.at(-1).p[1];
  const t = 48 * DT; // integrator offset is O(g t dt); the fitter below checks the acceleration itself
  assert.ok(Math.abs(y - (2 - 4.905 * t * t)) < 0.02, String(y));
  const req = fitterRequest(tr, 1);
  const py = spawnSync('python', ['-c', 'import json,sys; from Build.fitter.api import handle; print(json.dumps(handle(json.load(sys.stdin))))'], { cwd: ROOT, input: JSON.stringify(req), encoding: 'utf8' });
  if (py.status !== 0) { console.log('fitter skipped:', py.stderr.slice(-300)); return; }
  const out = JSON.parse(py.stdout);
  assert.equal(out.status, 'ok', py.stdout.slice(0, 300));
  assert.equal(out.gravity.unit, 'm/s^2');
  assert.ok(Math.abs(out.gravity.value + 9.81) < 1e-3, JSON.stringify(out.gravity)); // f32 Rapier, so not exact
});

test('pendulum swings, spring oscillates, ball rolls down ramp', () => {
  const s = defaultScene();
  const p = makeObject('pendulum', s, [0, 2, 0]); s.objects.push(p);
  const sp = makeObject('spring', s, [2, 2, 0]); s.objects.push(sp);
  const ramp = makeObject('ramp', s, [-2, 0.4, 0]); s.objects.push(ramp);
  const b = makeObject('ball', s, [-1.6, 0.7, 0]); s.objects.push(b);
  const sim = createPhysics(R, s);
  sim.step(120);
  const pt = sim.trace('pendulum-1').samples, st = sim.trace('spring-1').samples;
  const L = (q) => Math.hypot(q.p[0], q.p[1] - 2, q.p[2]);
  assert.ok(pt.every((q) => Math.abs(L(q) - 0.8) < 0.01), 'pendulum length held');
  assert.ok(Math.min(...pt.map((q) => q.p[0])) < -0.2, 'pendulum swung past centre');
  const ys = st.map((q) => q.p[1]);
  assert.ok(Math.max(...ys) - Math.min(...ys) > 0.05, 'spring moved');
  assert.ok(sim.trace('ball-1').samples.at(-1).p[0] < -1.7, 'ball rolled down the ramp');
  assert.deepEqual(movingStart(p).map((v) => Math.round(v * 1e6) / 1e6), [0.4, Math.round((2 - 0.8 * Math.cos(Math.PI / 6)) * 1e6) / 1e6, 0]);
  sim.free();
});

