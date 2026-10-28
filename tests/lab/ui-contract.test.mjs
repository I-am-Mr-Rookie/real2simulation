import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { parseFitReveal, plotPoints, sampleRows } from '../../Build/web/src/lab/fit-contract.mjs';

const source = await readFile(new URL('../../Build/web/src/lab/LabClient.jsx', import.meta.url), 'utf8');
const css = await readFile(new URL('../../Build/web/src/lab/lab.css', import.meta.url), 'utf8');

test('lab UI keeps the user flow and trust labels visible in source', () => {
  for (const text of ['Run trial', 'Fit &amp; reveal', 'Mystery-g mode', 'Simulated', 'limitations', 'aria-live="polite"']) assert.match(source, new RegExp(text));
  assert.match(source, /action: 'start'/); assert.match(source, /action: 'fit'/);
  assert.match(source, /disabled=\{!session \|\| !ballistic/);
  assert.doesNotMatch(source, /gravity\s*=\s*9\.81|seed\s*=|privateSetup/);
});

test('lab layout collapses before the narrow mobile viewport', () => {
  assert.match(css, /max-width: 390px/);
  assert.match(css, /overflow-x: auto/);
  assert.match(css, /grid-template-columns: 1fr/);
  assert.match(css, /\.reveal \{[^}]*overflow-wrap: anywhere/);
});

test('both request paths retain abort and stale-result guards before state updates', () => {
  for (const [start, end, update] of [['async function run(', 'async function fitTrial(', 'setSession(body)'],
    ['async function fitTrial(', 'const rows =', 'setFit(revealed)']]) {
    const handler = source.slice(source.indexOf(start), source.indexOf(end));
    const guard = 'if (controller.signal.aborted || version !== requestVersion.current) return;';
    assert.ok(handler.includes('request.current?.abort()'));
    assert.ok(handler.indexOf(guard) > 0 && handler.indexOf(guard) < handler.indexOf(update));
    assert.match(handler, /error.name === 'AbortError'/);
  }
  assert.match(source, /const reset = .*requestVersion.current \+= 1/);
  assert.match(source, /useEffect\(\(\) => \(\) => request.current\?\.abort\(\), \[\]\)/);
});

test('fit contract accepts only the actual S11 quantity and preserves uncertainty metadata', () => {
  const body = { status: 'ok', sessionId: 's1', fit: { status: 'ok',
    gravity: { value: 9.7, unit: 'm/s^2', uncertainty: 0.2, source: { label: 'simulated', evidence: 'synthetic' } },
    uncertainty: { model: 'quadratic', assumptions: ['ideal'] },
  } };
  assert.deepEqual(parseFitReveal(body, 's1'), { value: 9.7, uncertainty: 0.2, unit: 'm/s^2', source: 'simulated', evidence: 'synthetic', model: 'quadratic', assumptions: ['ideal'] });
  assert.equal(parseFitReveal({ ...body, fit: { ...body.fit, status: 'error' } }, 's1'), null);
  assert.equal(parseFitReveal(body, 'stale'), null);
  assert.equal(parseFitReveal({ ...body, fit: { ...body.fit, gravity: { ...body.fit.gravity, uncertainty: -1 } } }, 's1'), null);
  assert.equal(parseFitReveal({ ...body, fit: { ...body.fit, gravity: { ...body.fit.gravity, unit: 'm/s²' } } }, 's1'), null);
  assert.equal(parseFitReveal({ ...body, fit: { ...body.fit, uncertainty: { model: 'x', assumptions: ['ok', 1] } } }, 's1'), null);
  assert.equal(parseFitReveal({ sessionId: 's1', actualS11response: body.fit }, 's1'), null);
  assert.equal(parseFitReveal({ ...body, status: 'error' }, 's1'), null);
  assert.equal(parseFitReveal({ ...body, status: undefined }, 's1'), null);
});

test('the chart uses all observations, not the downsampled table', () => {
  assert.match(source, /plotPoints\(session\?\.observations\)/);
  assert.doesNotMatch(source, /plotPoints\(rows\)/);
  const observations = Array.from({ length: 2000 }, (_, i) => ({
    time_s: i / 100, position_m: (1 - Math.cos(2 * Math.PI * i / 250)) / 2,
  }));
  const result = plotPoints(observations);
  assert.equal(result.points.split(' ').length, 2000);
  assert.ok(result.position[1] > 0.999);
  assert.equal(result.position[0], 0);
  const rows = sampleRows(observations);
  assert.equal(rows.length, 9);
  assert.equal(rows.at(-1), observations.at(-1));
  assert.ok(Math.max(...rows.map((row) => row.position_m)) < 0.001, 'table samples alone alias this oscillation');
});

test('labels describe the bridge ordinate and unsupported fits honestly', () => {
  assert.match(source, /one standard uncertainty \(1σ\), not a 95% interval/);
  assert.match(source, /Downward vertical displacement from start/);
  assert.match(source, /not distance along the ramp or pendulum arc/);
  assert.match(source, /Fit is unavailable for this template/);
  assert.match(source, /ballistic \? 'Trial ready/);
  assert.doesNotMatch(source, />[Pp]osition \(/);
});

test('plot helper uses actual finite time and position domains', () => {
  const result = plotPoints([{ time_s: 10, position_m: -5 }, { time_s: 20, position_m: 15 }, { time_s: NaN, position_m: 2 }]);
  assert.deepEqual(result.time, [10, 20]); assert.deepEqual(result.position, [-5, 15]);
  assert.match(result.points, /^24,190 616,30$/);
  assert.deepEqual(plotPoints([{ time_s: 1, position_m: 2 }]).points, '320,110');
});

test('plot and table ignore nonfinite and malformed observations without coercion', () => {
  const valid = { time_s: 1, position_m: 2 };
  const observations = [null, {}, { time_s: '1', position_m: 2 }, { time_s: 0, position_m: Infinity },
    { time_s: NaN, position_m: 0 }, valid];
  assert.deepEqual(sampleRows(observations), [valid]);
  assert.deepEqual(plotPoints(observations), plotPoints([valid]));
  for (const empty of [undefined, null, {}, [], observations.slice(0, -1)]) {
    assert.deepEqual(sampleRows(empty), []);
    assert.deepEqual(plotPoints(empty), { points: '', time: null, position: null });
  }
  for (const length of [1, 2, 8, 9, 16, 17, 2000]) {
    const samples = Array.from({ length }, (_, i) => ({ time_s: i, position_m: i }));
    const rows = sampleRows(samples);
    assert.ok(rows.length <= 9);
    assert.equal(rows[0], samples[0]);
    assert.equal(rows.at(-1), samples.at(-1));
  }
});
