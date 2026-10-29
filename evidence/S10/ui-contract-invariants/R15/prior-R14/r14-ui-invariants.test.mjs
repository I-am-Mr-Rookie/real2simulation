// Frozen R14 audit oracle: do not change expectations to accommodate implementation.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { parseFitReveal, plotPoints, sampleRows } from '../../Build/web/src/lab/fit-contract.mjs';
import { runBrowserSimulation } from '../../Build/web/src/lab/browser-simulator.mjs';

const root = new URL('../../', import.meta.url);
const read = (path) => readFileSync(new URL(path, root), 'utf8');
const client = read('Build/web/src/lab/LabClient.jsx');
const browser = read('Build/web/src/lab/BrowserSimulation.jsx');
const dto = () => ({ status: 'ok', sessionId: 'r14-session', fit: { status: 'ok',
  gravity: { value: 9.7, uncertainty: 0.2, unit: 'm/s^2', source: { label: 'simulated', evidence: 'synthetic' } },
  uncertainty: { model: 'independent_position_time_first_order', assumptions: ['independent standard uncertainties'],
    quantity_uncertainty: 'standard uncertainty (one sigma), not a 95% interval' },
} });
const payload = () => ({ mode: 'normal', validatedSetup: JSON.parse(read('evidence/S10/browser-simulation/free_fall.artifact.json')) });

test('R14 valid accepted DTO preserves value, source, unit and uncertainty metadata', () => {
  const body = dto();
  assert.deepEqual(parseFitReveal(body, body.sessionId), { value: 9.7, uncertainty: 0.2, unit: 'm/s^2',
    source: 'simulated', evidence: 'synthetic', model: body.fit.uncertainty.model, assumptions: body.fit.uncertainty.assumptions });
});

test('R14 finite quantities, correct units/sources/status/session are strict without coercion', () => {
  for (const value of [NaN, Infinity, -Infinity, '9.7', null, {}, []]) {
    for (const key of ['value', 'uncertainty']) {
      const body = dto(); body.fit.gravity[key] = value;
      assert.equal(parseFitReveal(body, body.sessionId), null);
    }
  }
  for (const change of [
    (b) => { b.fit.gravity.uncertainty = -0.2; },
    (b) => { b.fit.gravity.unit = 'cm/s^2'; },
    (b) => { b.fit.gravity.source.label = 'measured'; },
    (b) => { b.fit.status = 'error'; },
    (b) => { b.status = 'error'; },
    (b) => { b.sessionId = 'stale'; },
    (b) => { b.fit.uncertainty.model = ' '; },
    (b) => { b.fit.uncertainty.assumptions = ['valid', null]; },
  ]) { const body = dto(); change(body); assert.equal(parseFitReveal(body, 'r14-session'), null); }
});

test('R14 explicit 95% interval metadata must not be accepted as the hardcoded one-sigma reveal', () => {
  const body = dto();
  body.fit.uncertainty.quantity_uncertainty = '95% confidence interval';
  assert.equal(parseFitReveal(body, body.sessionId), null);
});

test('R14 sparse assumptions are not a dense array of assumption strings (in-memory boundary)', () => {
  const body = dto(); body.fit.uncertainty.assumptions = Array(1);
  assert.equal(parseFitReveal(body, body.sessionId), null);
});

test('R14 malformed/nonfinite/sparse observation arrays are filtered without coercion or mutation', () => {
  const valid = Object.freeze({ time_s: 2, position_m: -3 });
  const rows = Object.freeze([, null, { time_s: '1', position_m: 2 }, { time_s: 0, position_m: Infinity }, valid]);
  assert.deepEqual(sampleRows(rows), [valid]);
  assert.deepEqual(plotPoints(rows), { points: '320,110', time: [2, 2], position: [-3, -3] });
  for (const value of [null, undefined, {}, 'samples', 3, Array(3)]) {
    assert.deepEqual(sampleRows(value), []);
    assert.deepEqual(plotPoints(value), { points: '', time: null, position: null });
  }
});

test('R14 two finite extreme observations must not yield NaN/Infinity SVG coordinates', () => {
  const plot = plotPoints([{ time_s: -1e308, position_m: -1e308 }, { time_s: 1e308, position_m: 1e308 }]);
  assert.doesNotMatch(plot.points, /NaN|Infinity/);
  assert.equal(plot.points, '24,190 616,30');
});

test('R14 oversized observations must not escape rendering as an unmanaged argument-stack RangeError', () => {
  const rows = Array.from({ length: 200_000 }, (_, i) => ({ time_s: i, position_m: i }));
  // Keep the existing all-points contract; no silent truncation or changed tolerance.
  let plot;
  assert.doesNotThrow(() => { plot = plotPoints(rows); });
  assert.equal(plot.points.split(' ').length, rows.length);
  assert.ok(sampleRows(rows).length <= 9);
});

test('R14 adapter rejects invalid/sparse/oversized input arrays, leaving caller input untouched', () => {
  for (const origin of [null, [], Array(3), [0, null, 0], [0, '0', 0], [0, Infinity, 0], Array(2001).fill(0)]) {
    const input = payload(); input.validatedSetup.spec.placement.origin.value = origin;
    const before = structuredClone(input);
    assert.throws(() => runBrowserSimulation(input));
    assert.deepEqual(input, before);
  }
});

// Execute exact source handler bodies with stubbed effects, not a duplicate UI implementation.
function handler(source, start, end, name, context) {
  const first = source.indexOf(start), last = source.indexOf(end, first);
  assert.ok(first >= 0 && last > first, 'source extraction anchors must exist');
  return Function(...Object.keys(context), `${source.slice(first, last)}; return ${name};`)(...Object.values(context));
}

test('R14 actual browser run handler replaces old success with sanitized error and error with success', () => {
  let state;
  const invoke = (input) => handler(browser, '  function run() {', '  return <section', 'run', {
    payload: input, runBrowserSimulation, setResult: (next) => { state = next; },
  })();
  const valid = payload(); invoke(valid);
  assert.ok(state.trajectory.samples.length > 0);
  const invalid = { mode: 'invalid-private-marker' }; invoke(invalid);
  assert.equal(state.payload, invalid);
  assert.equal(state.trajectory, undefined);
  assert.equal(state.error, 'Browser simulation unavailable. Supply a validated NORMAL synthetic setup with at most 2000 samples.');
  assert.doesNotMatch(state.error, /invalid-private-marker|INVALID_BROWSER_SIMULATION|TypeError/);
  invoke(valid); assert.ok(state.trajectory); assert.equal(state.error, undefined);
  // This is a source check, not a React rerender assertion.
  assert.match(browser, /const current = result\?\.payload === payload \? result : null;/);
});

test('R14 actual run/fit handlers suppress late successes and failures after abort/version invalidation', async () => {
  for (const name of ['run', 'fitTrial']) for (const invalidation of ['abort', 'version']) for (const failure of [false, true]) {
    const events = [];
    let resolve, reject;
    const pending = new Promise((yes, no) => { resolve = yes; reject = no; });
    const request = { current: null }, requestVersion = { current: 0 };
    const context = { request, requestVersion, AbortController, fetch: () => pending,
      setSession: (v) => events.push(['session', v]), setFit: (v) => events.push(['fit', v]),
      setStatus: (v) => events.push(['status', v]), setMessage: (v) => events.push(['message', v]),
      template: 'free_fall', mystery: false, ballistic: true, session: { sessionId: 'r14-session' },
      BALLISTIC: new Set(['free_fall', 'projectile']), parseFitReveal,
      errorMessage: () => { throw new Error('stale response reached error interpretation'); },
    };
    const start = name === 'run' ? '  async function run(event) {' : '  async function fitTrial() {';
    const end = name === 'run' ? '  async function fitTrial() {' : '  const rows =';
    const work = handler(client, start, end, name, context)({ preventDefault() {} });
    const before = [...events];
    if (invalidation === 'abort') request.current.abort(); else requestVersion.current += 1;
    if (failure) reject(new Error('late failure')); else resolve({ ok: true, json: async () => dto() });
    await work;
    assert.deepEqual(events, before, `${name}/${invalidation}/${failure ? 'failure' : 'success'}`);
  }
  assert.match(client, /const reset = .*request\.current\?\.abort\(\); requestVersion\.current \+= 1; setSession\(null\); setFit\(null\)/);
  assert.match(client, /useEffect\(\(\) => \(\) => request\.current\?\.abort\(\), \[\]\)/);
});
