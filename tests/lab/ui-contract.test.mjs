import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { parseFitReveal, plotPoints } from '../../Build/web/src/lab/fit-contract.mjs';

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
});

test('fit contract accepts only the actual S11 quantity and preserves uncertainty metadata', () => {
  const body = { status: 'ok', actualS11response: { sessionId: 's1', fit: {
    gravity: { value: 9.7, unit: 'm/s²', uncertainty: 0.2, source: { label: 'simulated', evidence: 'synthetic' } },
    uncertainty: { model: 'quadratic', assumptions: ['ideal'] },
  } } };
  assert.deepEqual(parseFitReveal(body, 's1'), { value: 9.7, uncertainty: 0.2, unit: 'm/s²', source: 'simulated', evidence: 'synthetic', model: 'quadratic', assumptions: ['ideal'] });
  assert.equal(parseFitReveal({ ...body, status: 'error' }, 's1'), null);
  assert.equal(parseFitReveal(body, 'stale'), null);
  assert.equal(parseFitReveal({ status: 'ok', actualS11response: { sessionId: 's1', fit: { gravity: { value: 9.7, unit: 'm/s²', uncertainty: -1, source: { label: 'simulated', evidence: 'synthetic' } }, uncertainty: { model: 'x', assumptions: [] } } } }, 's1'), null);
  assert.equal(parseFitReveal({ status: 'ok', actualS11response: { sessionId: 's1', fit: { gravity: { value: 9.7, unit: 'm/s²', uncertainty: 0.2, source: { label: 'truth', evidence: {} } }, uncertainty: { model: 'x', assumptions: [] } } } }, 's1'), null);
});

test('plot helper uses actual finite time and position domains', () => {
  const result = plotPoints([{ time_s: 10, position_m: -5 }, { time_s: 20, position_m: 15 }, { time_s: NaN, position_m: 2 }]);
  assert.deepEqual(result.time, [10, 20]); assert.deepEqual(result.position, [-5, 15]);
  assert.match(result.points, /^24,190 616,30$/);
  assert.deepEqual(plotPoints([{ time_s: 1, position_m: 2 }]).points, '320,110');
});
