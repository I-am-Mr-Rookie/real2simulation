import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { reduce, initialState } from '../../Build/web/src/workspace/workflow.mjs';
import { deps, jobReady, validSpec, runParameters, fixtureRunner } from '../../Build/web/src/workspace/fixtures.mjs';
import { initialInstruments, reduceInstruments, measure, instrumentView, parseReading } from '../../Build/web/src/workspace/instruments.mjs';
import { renderInstruments } from '../../Build/web/src/workspace/instrument-view.mjs';

// Readings recorded from the REAL Build/instruments models (evidence/S15/instrument_fixtures.py); SYNTHETIC settings/inputs.
const FIX = JSON.parse(readFileSync(new URL('./fixtures/instrument-readings.json', import.meta.url), 'utf8'));
const service = async (id, n) => { const r = FIX.readings[id]?.[n]; if (!r) throw new Error('no recorded reading'); return r; };
const html = (tag, props, ...kids) => '<' + tag + Object.entries(props ?? {}).map(([k, v]) => ' ' + k + '="' + v + '"').join('') + '>' + kids.flat().join('') + '</' + tag + '>';
const done = () => [{ type: 'UPLOAD_STARTED', jobId: 'synthetic-job-v1' }, { type: 'JOB_UPDATE', job: jobReady(1) }, { type: 'INTERVIEW_SPEC', spec: validSpec },
  { type: 'RUN_START', seed: 7 }, { type: 'RUN_COMPLETE', seed: 7, observations: fixtureRunner(runParameters, 7) }].reduce((s, e) => reduce(s, e, deps), initialState());
const take = async (m, s, id, n) => { // host loop: select, request, answer from the service
  m = reduceInstruments(m, { type: 'I_SELECT', instrument: id }, s); m = reduceInstruments(m, { type: 'I_MEASURE' }, s);
  return reduceInstruments(m, await measure(service, m), s);
};
const num = (x) => String(Number(x.toPrecision(10)));

test('fixture is current real instrument output', () => {
  const r = spawnSync('python', ['evidence/S15/instrument_fixtures.py', '--check'], { encoding: 'utf8' });
  if (r.error) return; // python unavailable here; the generator --check is the authority
  assert.equal(r.status, 0, r.stderr);
});

test('every trial row renders value, plus-minus uncertainty, unit, simulated label and source evidence; error is never shown', async () => {
  const s = done(); let m = initialInstruments();
  for (const id of ['stopwatch', 'light_gate', 'ruler', 'camera']) m = await take(m, s, id, 0);
  assert.equal(m.trials.length, 4);
  const out = renderInstruments(html, instrumentView(s, m), () => {});
  const rows = [FIX.readings.stopwatch[0], FIX.readings.light_gate[0], FIX.readings.ruler[0], FIX.readings.camera[0].time, FIX.readings.camera[0].x, FIX.readings.camera[0].y];
  for (const q of rows) {
    assert.ok(out.includes(num(q.value) + ' \u00b1 ' + num(q.uncertainty) + ' ' + q.unit), 'value, uncertainty, unit: ' + JSON.stringify(q));
    assert.ok(out.includes('source: ' + q.source.evidence));
  }
  assert.equal(out.split('data-label="simulated"').length - 1, rows.length);
  assert.match(out, /Trial 4: Camera, frame 0/);
  assert.doesNotMatch(out, /error/i); // signed instrument error would leak the hidden true value
  assert.ok(rows.some((q) => q.error !== 0), 'fixture has a non-zero error that must stay hidden');
});

test('repeat readings for one instrument advance through the service; exhaustion is a visible failure', async () => {
  const s = done(); let m = initialInstruments();
  for (let i = 0; i < 3; i += 1) m = await take(m, s, 'stopwatch', i);
  assert.deepEqual(m.trials.map((x) => x.rows[0].value), FIX.readings.stopwatch.map((q) => q.value));
  m = await take(m, s, 'stopwatch', 3);
  assert.equal(m.trials.length, 3); assert.equal(m.pending, null); assert.match(instrumentView(s, m).error, /no recorded reading/);
});

test('rejects readings that lack provenance or uncertainty, or break the contract', () => {
  const good = FIX.readings.stopwatch[0], bad = (patch) => ({ ...good, ...patch });
  const cases = [bad({ unit: 'm' }), bad({ uncertainty: -1 }), bad({ uncertainty: undefined }), bad({ value: NaN }), bad({ source: { label: 'measured', evidence: 'x' } }),
    bad({ source: { label: 'simulated', evidence: ' ' } }), bad({ source: undefined }), bad({ extra: 1 }), bad({ gravity: 9 }), bad({ source: { label: 'simulated', evidence: 'x', hidden_g: 1 } })];
  for (const c of cases) assert.throws(() => parseReading('stopwatch', c), undefined, JSON.stringify(c));
  assert.throws(() => parseReading('camera', { time: good, x: good, y: good }), /frame_index/);
  assert.throws(() => parseReading('camera', { ...FIX.readings.camera[0], x: FIX.readings.stopwatch[0] }), /unit must be px/);
  const s = done(); let m = reduceInstruments(initialInstruments(), { type: 'I_MEASURE' }, s);
  m = reduceInstruments(m, { type: 'I_READING', instrument: 'stopwatch', reading: bad({ uncertainty: -1 }) }, s);
  assert.equal(m.trials.length, 0); assert.equal(m.pending, null); assert.match(m.error, /^Reading rejected/);
});

test('guards: phase, pending, stale readings, same-reference no-ops, run changes clear trials', async () => {
  const s = done(), m0 = initialInstruments();
  assert.equal(reduceInstruments(m0, { type: 'I_MEASURE' }, initialState()), m0); // no trial run yet
  assert.equal(reduceInstruments(m0, { type: 'I_SELECT', instrument: 'stopwatch' }, s), m0);
  assert.equal(reduceInstruments(m0, { type: 'I_READING', instrument: 'stopwatch', reading: FIX.readings.stopwatch[0] }, s), m0); // unrequested
  const pend = reduceInstruments(m0, { type: 'I_MEASURE' }, s);
  assert.equal(reduceInstruments(pend, { type: 'I_MEASURE' }, s), pend);
  assert.equal(reduceInstruments(pend, { type: 'I_SELECT', instrument: 'ruler' }, s), pend);
  assert.equal(reduceInstruments(pend, { type: 'I_READING', instrument: 'ruler', reading: FIX.readings.ruler[0] }, s), pend); // stale instrument
  assert.equal(instrumentView(s, pend).canMeasure, false);
  const m = await take(m0, s, 'ruler', 0);
  for (const type of ['RUN_START', 'RUN_CANCEL', 'EDIT_SPEC', 'RESET']) assert.equal(reduceInstruments(m, { type }, s).trials.length, 0);
  assert.equal(instrumentView(initialState(), m0).show, false);
  assert.equal(renderInstruments(html, instrumentView(initialState(), m0)), null);
});

test('controls: disabled without onAction and while pending; buttons report their events', async () => {
  const s = done(), m = initialInstruments();
  assert.match(renderInstruments(html, instrumentView(s, m)), /disabled="true"/);
  const sent = []; const h = (tag, p, ...k) => ({ tag, p, k: k.flat() });
  const tree = renderInstruments(h, instrumentView(s, m), (a) => sent.push(a));
  const buttons = []; (function walk(n) { if (n && typeof n === 'object') { if (n.tag === 'button') buttons.push(n); n.k?.forEach(walk); } })(tree);
  buttons.forEach((b) => b.p.onClick());
  assert.deepEqual(sent.map((a) => a.type), ['I_SELECT', 'I_SELECT', 'I_SELECT', 'I_SELECT', 'I_MEASURE']);
});
