// N22: Mode B result logic checked against the real N07 ST03 result (evidence/N07/live-st03.json, fitter output).
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { polyFit, chartGeom, fmtPm, knownSizeText, naturalPoint, experimentBody, jobView, jobsFromToolCalls, shareable, trajectoryScene } from '../../Build/web/src/workspace/measure.mjs';
import { validateScene } from '../../Build/web/src/lab-editor/scene.mjs';

const res = JSON.parse(readFileSync(new URL('../../evidence/N07/live-st03.json', import.meta.url))).result;

test('browser refit matches the fitter acceleration and 1 sigma', () => {
  const f = polyFit(res.trajectory.t_s, res.trajectory.y, 2);
  const a = 2 * f.b[2], s = 2 * Math.sqrt(f.cov[2][2]);
  assert.ok(Math.abs(a - res.fit.y.accel_px_s2) < 1e-6 * Math.abs(a), a);
  assert.ok(Math.abs(s / res.fit.y.accel_sigma_px_s2 - 1) < 0.02, s);
  assert.equal(polyFit([0, 1], [0, 1], 2), null);
});

test('chart has every point, a curve and a closed band', () => {
  const g = chartGeom(res);
  assert.equal(g.points.length, res.trajectory.t_s.length);
  assert.match(g.curve, /^M/); assert.match(g.band, /Z$/);
  for (const p of g.points) assert.ok(p.cx >= 0 && p.cx <= g.W && p.cy >= 0 && p.cy <= g.H);
  assert.equal(chartGeom({}), null);
});

test('formatting and form helpers', () => {
  assert.equal(fmtPm(2329.5401, 105.54), '2330 +/- 110');
  assert.equal(fmtPm(9.7812, 0.234), '9.78 +/- 0.23');
  assert.equal(knownSizeText('6.5', 'cm', 'ball diameter'), 'ball diameter 6.5 cm');
  assert.equal(knownSizeText('', 'cm', 'x'), null); assert.equal(knownSizeText('-1', 'cm', 'x'), null); assert.equal(knownSizeText('2', 'ft', 'x'), null);
  assert.deepEqual(naturalPoint(50, 100, 100, 200, 720, 1366), { x: 360, y: 683 });
  assert.deepEqual(naturalPoint(100, 200, 100, 200, 720, 1366), { x: 719, y: 1365 });
  assert.equal(naturalPoint(1, 1, 0, 0, 1, 1), null);
  assert.deepEqual(experimentBody('f', { point: { x: 1, y: 2 }, name: 'apple', size: '7', unit: 'cm', what: 'apple width' }, 'p'),
    { file_id: 'f', point: { x: 1, y: 2 }, known_size: 'apple width 7 cm', project_id: 'p' });
  assert.deepEqual(experimentBody('f', { name: ' apple ' }), { file_id: 'f', target_text: 'apple' });
  assert.equal(experimentBody('f', {}), null);
});

test('job cards, agent tool calls, share gate', () => {
  assert.deepEqual(jobView('experiment', { experiment: { status: 'failed', error: { code: 'CAP_EXCEEDED', message: 'cap' } } }).error, 'cap');
  const r = jobView('room', { job: { state: 'reconstructing', gpu: { state: 'yellow' } } });
  assert.equal(r.terminal, false); assert.equal(r.gpu.state, 'yellow');
  assert.equal(jobView('room', { job: { state: 'done' } }).terminal, true);
  assert.deepEqual(jobsFromToolCalls([{ name: 'start_room_build', output: { room_job_id: 'r1' } }, { name: 'start_experiment_track', output: { trajectory_id: 'e1' } }, { name: 'fit', output: {} }]),
    [{ kind: 'room', id: 'r1' }, { kind: 'experiment', id: 'e1' }]);
  assert.equal(shareable(res), false); assert.equal(shareable({ quantity: { unit: 'm/s^2' } }), true);
});

test('redo scene validates and starts at the first track point', () => {
  const t = trajectoryScene(res);
  const s = validateScene(t.scene);
  assert.equal(s.objects.length, 1); assert.deepEqual(s.objects[0].position, t.track[0]);
  assert.ok(Math.min(...t.track.map((p) => p[1])) > 0); assert.equal(t.metric, false); assert.match(t.note, /Scale unverified/);
  assert.ok(t.scene.objects[0].velocity[1] < 0);
});
