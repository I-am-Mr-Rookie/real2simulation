import test from 'node:test';
import assert from 'node:assert/strict';
import { lessonVerdict, lessonReport } from '../../Build/web/src/lab-editor/lesson.mjs';

test('equal fits are the same within the floor, and the prediction is scored', () => {
  const a = { value: -9.8100163, uncertainty: 2.2e-6, mass: 0.1 }, b = { value: -9.8100401, uncertainty: 2.1e-6, mass: 1 };
  const v = lessonVerdict(a, b, 'heavier');
  assert.equal(v.outcome, 'same'); assert.equal(v.matched, false);
  assert.equal(lessonVerdict(a, b, 'same').matched, true);
  assert.match(lessonReport('same', a, b, lessonVerdict(a, b, 'same')), /Prediction: Both fall the same[\s\S]*The prediction matched/);
});

test('a real difference beyond 2 sigma names the faster run', () => {
  const v = lessonVerdict({ value: -9.0, uncertainty: 0.05, mass: 0.1 }, { value: -9.8, uncertainty: 0.05, mass: 1 }, null);
  assert.equal(v.outcome, 'heavier'); assert.equal(v.matched, null);
  assert.equal(lessonVerdict({ value: -9.8, uncertainty: 0.05, mass: 0.1 }, { value: -9.0, uncertainty: 0.05, mass: 1 }).outcome, 'lighter');
  assert.equal(lessonVerdict(null, { value: 1 }), null);
});
