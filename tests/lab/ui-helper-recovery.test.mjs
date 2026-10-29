import test from 'node:test';
import assert from 'node:assert/strict';
import { parseFitReveal, plotPoints, sampleRows } from '../../Build/web/src/lab/fit-contract.mjs';

const standard = 'standard uncertainty (one sigma), not a 95% interval';
const dto = () => ({ status: 'ok', sessionId: 'recovery-session', fit: { status: 'ok',
  gravity: { value: 9.7, uncertainty: 0.2, unit: 'm/s^2', source: { label: 'simulated', evidence: 'synthetic' } },
  uncertainty: { model: 'independent_position_time_first_order', assumptions: ['scale fixed'], quantity_uncertainty: standard },
} });
const row = (time_s, position_m = time_s) => ({ time_s, position_m });
const coordinates = (plot) => plot.points.split(' ').map((point) => point.split(',').map(Number));

test('R16 supplied uncertainty interpretation cannot contradict the one-sigma UI label', () => {
  for (const label of ['95% confidence interval', 'standard error of the mean', 'two sigma', '', undefined, null, 1, {}, []]) {
    const body = dto(); body.fit.uncertainty.quantity_uncertainty = label;
    const before = structuredClone(body);
    assert.equal(parseFitReveal(body, body.sessionId), null);
    assert.deepEqual(body, before);
  }
});

test('R16 canonical and legacy omitted interpretation preserve the exact reveal shape', () => {
  for (const omit of [false, true]) {
    const body = dto();
    if (omit) delete body.fit.uncertainty.quantity_uncertainty;
    const before = structuredClone(body);
    assert.deepEqual(parseFitReveal(body, body.sessionId), { value: 9.7, uncertainty: 0.2, unit: 'm/s^2',
      source: 'simulated', evidence: 'synthetic', model: body.fit.uncertainty.model, assumptions: ['scale fixed'] });
    assert.deepEqual(body, before);
  }
});

test('R16 assumptions must contain actual strings at every array index', () => {
  for (const assumptions of [Array(3), [, 'valid'], ['valid', , 'valid'], ['valid', undefined], ['valid', null]]) {
    const body = dto(); body.fit.uncertainty.assumptions = assumptions;
    const before = structuredClone(assumptions);
    assert.equal(parseFitReveal(body, body.sessionId), null);
    assert.deepEqual(assumptions, before);
  }
  for (const assumptions of [[], [''], ['independent errors', 'scale fixed']]) {
    const body = dto(); body.fit.uncertainty.assumptions = Object.freeze(assumptions);
    assert.equal(parseFitReveal(body, body.sessionId).assumptions, assumptions);
  }
});

test('R16 opposite-sign maximal domains retain every point, endpoint and midpoint', () => {
  const max = Number.MAX_VALUE;
  const observations = Object.freeze([-max, -max / 2, 0, max / 2, max].map((value) => Object.freeze(row(value, -value))));
  const plot = plotPoints(observations);
  assert.deepEqual(plot.time, [-max, max]);
  assert.deepEqual(plot.position, [-max, max]);
  assert.deepEqual(coordinates(plot), [[24, 30], [172, 70], [320, 110], [468, 150], [616, 190]]);
});

test('R16 asymmetric overflowing domains scale both axes independently without reordering', () => {
  const max = Number.MAX_VALUE;
  const plot = plotPoints([row(max / 2, -max), row(0, max / 2), row(-max, 0)], 600, 150);
  const points = coordinates(plot);
  assert.deepEqual(plot.time, [-max, max / 2]);
  assert.deepEqual(plot.position, [-max, max / 2]);
  for (const [i, expected] of [[0, [624, 190]], [1, [424, 40]], [2, [24, 90]]]) {
    for (let axis = 0; axis < 2; axis += 1) assert.ok(Math.abs(points[i][axis] - expected[axis]) < 1e-10);
  }
});

test('R16 ordinary, subnormal, adjacent-large and degenerate domains keep existing affine semantics', () => {
  const min = Number.MIN_VALUE;
  const nearMax = Number.MAX_VALUE * (1 - Number.EPSILON);
  for (const values of [[-5, 0, 15], [0, min, 2 * min], [-min, 0, min],
    [nearMax, Number.MAX_VALUE], [1, 1], [-0, 0]]) {
    const observations = values.map((value) => row(value));
    const time = [Math.min(...values), Math.max(...values)];
    const scale = (value, size) => time[0] === time[1] ? size / 2 : (value - time[0]) / (time[1] - time[0]) * size;
    assert.deepEqual(plotPoints(observations, 120, 80), { time, position: time,
      points: values.map((value) => `${24 + scale(value, 120)},${190 - scale(value, 80)}`).join(' ') });
  }
});

test('R16 large observation arrays retain finite rows beyond the argument-stack and producer limits', () => {
  const observations = Array.from({ length: 250_003 }, (_, i) => row(i, -i));
  observations[1] = null;
  observations[2] = row(NaN);
  delete observations[3];
  const plot = plotPoints(observations);
  const points = plot.points.split(' ');
  assert.equal(points.length, observations.length - 3);
  assert.equal(points[0], '24,30');
  assert.equal(points.at(-1), '616,190');
  assert.deepEqual(plot.time, [0, 250_002]);
  assert.deepEqual(plot.position, [-250_002, -0]);
  assert.doesNotMatch(plot.points, /NaN|Infinity/);
  assert.ok(sampleRows(observations).length <= 9);
  assert.equal(observations[1], null);
  assert.equal(3 in observations, false);
});
