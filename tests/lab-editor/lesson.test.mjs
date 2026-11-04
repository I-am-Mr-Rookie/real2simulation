import test from 'node:test';
import assert from 'node:assert/strict';
import { LESSONS, lessonVerdict, lessonReport } from '../../Build/web/src/lab-editor/lesson.mjs';
import { templateScene } from '../../Build/web/src/lab-editor/templates.mjs';
import { fitSimTrace } from '../../Build/web/src/workspace/measure.mjs';
import { simulate } from '../../Build/web/src/lab-editor/agent-run.mjs';

const [MASS, HEIGHT] = LESSONS;

test('mass lesson: equal fits are the same within the floor, and the prediction is scored', () => {
  const a = { value: -9.8100163, uncertainty: 2.2e-6, mass: 0.05 }, b = { value: -9.8100401, uncertainty: 2.1e-6, mass: 0.5 };
  assert.equal(lessonVerdict(MASS, a, b, 'heavier').outcome, 'same'); assert.equal(lessonVerdict(MASS, a, b, 'heavier').matched, false);
  assert.match(lessonReport(MASS, 'same', a, b, lessonVerdict(MASS, a, b, 'same')), /Prediction: Both fall the same[\s\S]*The prediction matched/);
  assert.equal(lessonVerdict(MASS, { value: -9.0, uncertainty: 0.05, mass: 0.1 }, { value: -9.8, uncertainty: 0.05, mass: 1 }).outcome, 'heavier');
  assert.equal(lessonVerdict(MASS, null, b), null);
});

test('height lesson: change doubles the drop height above the floor', () => {
  const o = { position: [0, 2, 0], size: [0.06, 0.06, 0.06] }, c = HEIGHT.change(o);
  assert.ok(Math.abs((c.position[1] - 0.03) - 2 * (2 - 0.03)) < 1e-9);
  assert.ok(HEIGHT.changed(c, HEIGHT.run({ t1: 0.63 }, o)));
});

test('height lesson end to end in the engine: twice the height takes about 1.41 times as long', async () => {
  const s = templateScene('physics-lab'), ball = s.objects.find((o) => o.id === 'ball-drop');
  const fitOf = async (scene, secs) => { // the browser keeps recording the ball at rest after landing; add that tail here too
    const d = (await simulate(scene, secs)).traces.find((t) => t.object_id === 'ball-drop').samples, end = d.at(-1);
    return fitSimTrace({ samples: [...d, ...Array.from({ length: 40 }, (_, i) => ({ t: end.t + 0.02 * (i + 1), p: [end.p[0], 0.03, end.p[2]] }))] });
  };
  const fa = await fitOf(s, 1.2), a = HEIGHT.run(fa, ball);
  const moved = HEIGHT.change(ball), s2 = { ...s, objects: s.objects.map((o) => (o.id === 'ball-drop' ? moved : o)) };
  const fb = await fitOf(s2, 1.6), b = HEIGHT.run(fb, moved);
  assert.ok(fa.n < fa.total && fb.n < fb.total, 'both runs reached the first impact');
  const v = lessonVerdict(HEIGHT, a, b, 'double');
  assert.equal(v.outcome, 'sqrt', v.text); assert.equal(v.matched, false);
  assert.ok(Math.abs(b.time / a.time - Math.SQRT2) < 0.03, v.text);
});
