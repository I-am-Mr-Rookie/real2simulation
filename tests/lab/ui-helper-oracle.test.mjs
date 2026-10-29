import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { parseFitReveal, plotPoints, sampleRows } from '../../Build/web/src/lab/fit-contract.mjs';

// Integer multiples of 2^-1074 prove input ratios without floating subtraction/division.
function dyadicUnits(value) {
  assert.ok(Number.isFinite(value));
  const view = new DataView(new ArrayBuffer(8));
  view.setFloat64(0, value);
  const bits = view.getBigUint64(0);
  const exponent = Number((bits >> 52n) & 2047n);
  const fraction = bits & ((1n << 52n) - 1n);
  const magnitude = exponent === 0 ? fraction : ((1n << 52n) | fraction) << BigInt(exponent - 1);
  return bits >> 63n ? -magnitude : magnitude;
}

const huge = 2 ** 1023;
const ulp = 2 ** 971;
const tiny = Number.MIN_VALUE;
const domains = [
  ['ordinary quarters', [-8, -4, 0, 4, 8]],
  ['opposite-sign overflowing power-of-two span', [-huge, -huge / 2, 0, huge / 2, huge]],
  ['opposite-sign maximum finite span', [-Number.MAX_VALUE, -Number.MAX_VALUE / 2, 0, Number.MAX_VALUE / 2, Number.MAX_VALUE]],
  ['positive maximum finite midpoint', [0, Number.MAX_VALUE / 2, Number.MAX_VALUE]],
  ['negative maximum finite midpoint', [-Number.MAX_VALUE, -Number.MAX_VALUE / 2, 0]],
  ['nearby huge positive quarters', [huge, huge + ulp, huge + 2 * ulp, huge + 3 * ulp, huge + 4 * ulp]],
  ['nearby huge negative quarters', [-huge - 4 * ulp, -huge - 3 * ulp, -huge - 2 * ulp, -huge - ulp, -huge]],
  ['positive subnormal quarters', [tiny, 2 * tiny, 3 * tiny, 4 * tiny, 5 * tiny]],
  ['negative subnormal quarters', [-5 * tiny, -4 * tiny, -3 * tiny, -2 * tiny, -tiny]],
  ['opposite-sign subnormal quarters', [-2 * tiny, -tiny, 0, tiny, 2 * tiny]],
  ['subnormal-to-normal boundary quarters', [2 ** -1022 - 2 * tiny, 2 ** -1022 - tiny, 2 ** -1022, 2 ** -1022 + tiny, 2 ** -1022 + 2 * tiny]],
];
const pixels = {
  3: [[24, 190], [320, 110], [616, 30]],
  5: [[24, 190], [172, 150], [320, 110], [468, 70], [616, 30]],
};

test('oracle input spacing is exactly rational, including huge and subnormal cases', () => {
  assert.equal(dyadicUnits(tiny), 1n);
  assert.equal(dyadicUnits(-tiny), -1n);
  assert.equal(dyadicUnits(1), 1n << 1074n);
  for (const [name, domain] of domains) {
    const units = domain.map(dyadicUnits);
    assert.ok(units.at(-1) > units[0], name);
    units.forEach((value, index) => assert.equal(
      BigInt(units.length - 1) * (value - units[0]),
      BigInt(index) * (units.at(-1) - units[0]), name));
  }
});

function coordinates(result) {
  return result.points.split(' ').map((pair) => {
    const values = pair.split(',').map(Number);
    assert.equal(values.length, 2);
    assert.ok(values.every(Number.isFinite), `nonfinite pixel: ${pair}`);
    return values;
  });
}

for (const [name, domain] of domains) {
  test(`exact plot coordinates: ${name}`, () => {
    const observations = domain.map((value) => Object.freeze({ time_s: value, position_m: value }));
    Object.freeze(observations);
    const before = structuredClone(observations);
    const result = plotPoints(observations);
    assert.deepEqual(coordinates(result), pixels[domain.length]);
    assert.deepEqual(result.time, [domain[0], domain.at(-1)]);
    assert.deepEqual(result.position, [domain[0], domain.at(-1)]);
    assert.deepEqual(observations, before);
  });
}

test('axes are independent; shuffled and duplicate observations keep exact order and count', () => {
  const domain = domains[5][1];
  const order = [4, 0, 2, 2, 1, 3, 0];
  const observations = Object.freeze(order.map((i) => Object.freeze({ time_s: domain[i], position_m: (4 - i) * tiny })));
  const before = structuredClone(observations);
  const result = plotPoints(observations);
  assert.deepEqual(coordinates(result), [[616, 190], [24, 30], [320, 110], [320, 110], [172, 70], [468, 150], [24, 30]]);
  assert.deepEqual(result.time, [domain[0], domain.at(-1)]);
  assert.deepEqual(result.position, [0, 4 * tiny]);
  assert.deepEqual(observations, before);
});

test('degenerate axes center independently without moving the other axis', () => {
  const cases = [
    [[{ time_s: huge, position_m: -tiny }, { time_s: huge, position_m: tiny }], [[320, 190], [320, 30]]],
    [[{ time_s: -huge, position_m: tiny }, { time_s: huge, position_m: tiny }], [[24, 110], [616, 110]]],
    [[{ time_s: -huge, position_m: tiny }, { time_s: -huge, position_m: tiny }], [[320, 110], [320, 110]]],
  ];
  for (const [rows, expected] of cases) assert.deepEqual(coordinates(plotPoints(rows)), expected);
});

test('custom finite drawing extents retain the same exact midpoint geometry', () => {
  const rows = [-huge, 0, huge].map((value) => ({ time_s: value, position_m: value }));
  assert.deepEqual(coordinates(plotPoints(rows, 512, 128)), [[24, 190], [280, 126], [536, 62]]);
});

test('finite-only filtering and table sampling preserve caller-owned inputs', () => {
  const valid = Array.from({ length: 17 }, (_, i) => Object.freeze({ time_s: i, position_m: i }));
  const rows = Object.freeze([null, Object.freeze({ time_s: '0', position_m: 1 }), ...valid,
    Object.freeze({ time_s: Infinity, position_m: 0 }), Object.freeze({ time_s: 0, position_m: NaN })]);
  const before = structuredClone(rows);
  assert.equal(coordinates(plotPoints(rows)).length, 17);
  const sampled = sampleRows(rows);
  assert.deepEqual(sampled, [valid[0], valid[3], valid[6], valid[9], valid[12], valid[15], valid[16]]);
  sampled.forEach((row) => assert.ok(valid.includes(row)));
  assert.deepEqual(rows, before);
});

test('a bounded large point list has no implicit argument-count limit or silent truncation', () => {
  const row = Object.freeze({ time_s: huge, position_m: tiny });
  const rows = Object.freeze(Array(131073).fill(row));
  const result = plotPoints(rows);
  const pairs = result.points.split(' ');
  assert.equal(pairs.length, rows.length);
  assert.ok(pairs.every((pair) => pair === '320,110'));
  assert.equal(rows.length, 131073);
  assert.ok(rows.every((item) => item === row));
});

let producerBody;
function actualProducerBody() {
  if (producerBody) return structuredClone(producerBody);
  const code = `import json,runpy\nm=runpy.run_path('Build/lab/session-bridge.py')\ns=m['handle']({'action':'start','template':'free_fall','mystery':False})\nassert s['status']=='ok',s\nf=m['handle']({'action':'fit','observations':s['observations']})\nprint(json.dumps(f,allow_nan=False))`;
  const result = spawnSync(process.env.PYTHON || 'python', ['-B', '-c', code], {
    cwd: fileURLToPath(new URL('../../', import.meta.url)), encoding: 'utf8', timeout: 30000,
    env: { PATH: process.env.PATH || '', SystemRoot: process.env.SystemRoot || '', PYTHONIOENCODING: 'utf-8', PYTHONDONTWRITEBYTECODE: '1' },
  });
  assert.ifError(result.error);
  assert.equal(result.status, 0, result.stderr);
  const fit = JSON.parse(result.stdout);
  assert.equal(fit.status, 'ok');
  // Only the service envelope/session ID is authored; the complete fit is the real producer's.
  producerBody = { status: 'ok', sessionId: 'r16-oracle', fit };
  return structuredClone(producerBody);
}

test('actual producer explicitly supplies one-standard-uncertainty metadata and is accepted unchanged', () => {
  const body = actualProducerBody();
  const before = structuredClone(body);
  assert.equal(body.fit.uncertainty.quantity_uncertainty, 'standard uncertainty (one sigma), not a 95% interval');
  assert.equal(body.fit.covariance.interval, null);
  const reveal = parseFitReveal(body, body.sessionId);
  assert.ok(reveal);
  assert.equal(reveal.value, body.fit.gravity.value);
  assert.equal(reveal.uncertainty, body.fit.gravity.uncertainty);
  assert.deepEqual(reveal.assumptions, body.fit.uncertainty.assumptions);
  assert.deepEqual(body, before);
});

for (const meaning of ['95% confidence interval', 'expanded uncertainty (two sigma)', 'not a standard uncertainty']) {
  test(`explicit contradictory uncertainty meaning is not silently relabelled 1-sigma: ${meaning}`, () => {
    const body = actualProducerBody();
    body.fit.uncertainty.quantity_uncertainty = meaning;
    const before = structuredClone(body);
    assert.equal(parseFitReveal(body, body.sessionId), null);
    assert.deepEqual(body, before);
  });
}

test('legitimate minimal DTO does not acquire a newly required metadata key', () => {
  const body = { status: 'ok', sessionId: 'legacy', fit: { status: 'ok',
    gravity: { value: 9.7, uncertainty: 0.2, unit: 'm/s^2', source: { label: 'simulated', evidence: 'synthetic' } },
    uncertainty: { model: 'quadratic', assumptions: ['ideal'] } } };
  const before = structuredClone(body);
  assert.deepEqual(parseFitReveal(body, 'legacy'), { value: 9.7, uncertainty: 0.2, unit: 'm/s^2',
    source: 'simulated', evidence: 'synthetic', model: 'quadratic', assumptions: ['ideal'] });
  assert.deepEqual(body, before);
});

test('explicit assumptions must contain actual strings, not sparse array holes', () => {
  const body = actualProducerBody();
  body.fit.uncertainty.assumptions = Array(1);
  const before = structuredClone(body);
  assert.equal(parseFitReveal(body, body.sessionId), null);
  assert.deepEqual(body, before);
});
