// S15k fixture-first walk: upload -> interview -> template/spec -> run -> instruments -> fit -> report through the REAL
// workspace models + React 19 SSR binding. Every step is labelled FIXTURE (synthetic/recorded real-Python outputs); none is live S14,
// a deployed workspace, gate, real-scene or physical evidence. Writes evidence/S15/walk-steps.json (+ walk-preview.html per stage).
// Usage: node evidence/S15/walk-check.mjs <path-to-Build/web/node_modules>
import { createRequire } from 'node:module';
import assert from 'node:assert/strict';
import { readFileSync, writeFileSync } from 'node:fs';
import { createWorkspace } from '../../Build/web/src/workspace/react.mjs';
import { initialLogged, reduceLogged } from '../../Build/web/src/workspace/status.mjs';
import { reduce } from '../../Build/web/src/workspace/workflow.mjs';
import { job, jobReady, runParameters, fixtureRunner, fitBody } from '../../Build/web/src/workspace/fixtures.mjs';
import { parseFitReveal } from '../../Build/web/src/lab/fit-contract.mjs';
import { initialInterview, reduceInterview, interviewAnswers } from '../../Build/web/src/workspace/interview.mjs';
import { initialTemplate, reduceTemplate, acceptedSpec } from '../../Build/web/src/workspace/template.mjs';
import { initialRun, reduceRun, prepareRun, completionEvent } from '../../Build/web/src/workspace/runcontrol.mjs';
import { initialInstruments, reduceInstruments } from '../../Build/web/src/workspace/instruments.mjs';
import { createReplayRecord, replayRecord } from '../../Build/simulator/replay.mjs';

const req = createRequire(process.argv[2].replace(/[\\/]?$/, '/') + 'x.js');
const React = req('react'), { renderToString } = req('react-dom/server');
const Workspace = createWorkspace(React);
const fx = (n) => JSON.parse(readFileSync('tests/workspace/fixtures/' + n, 'utf8'));
const IV = fx('interview-responses.json'), TP = fx('template-cases.json'), FIT = fx('fit-output.json'), RPT = fx('report-output.json').report;
const steps = [], previews = [];
const css = readFileSync('Build/web/src/app/styles.css', 'utf8') + readFileSync('Build/web/src/workspace/workspace.css', 'utf8');

let m = initialLogged(), im = initialInterview(), tm = initialTemplate(), rm = initialRun(), ins = initialInstruments();
let spec = null;
const verdict = TP.verdicts.find((v) => v.template === 'free_fall' && v.ok);
const deps = { validateSpec: (s) => (s && s === spec ? { ok: true } : { ok: false, errors: ['spec is not the accepted template spec'] }) };
const send = (e) => { m = reduceLogged(m, e, deps); rm = reduceRun(rm, e, m.state); };
const render = (extra = {}) => renderToString(React.createElement(Workspace, { state: m.state, log: m.log, adapter: {}, loadScene: () => {}, navigate: true, interview: im, template: tm, run: rm, onAction: () => {}, ...extra }));
const step = async (name, mode, fn, expectPhase) => {
  const t0 = performance.now(); let err = null, html = '';
  try { html = await fn(); assert.equal(m.state.phase, expectPhase, name + ': phase'); } catch (e) { err = String(e.message ?? e); }
  steps.push({ step: name, mode, ok: !err, phase: m.state.phase, ms: +(performance.now() - t0).toFixed(1), error: err, htmlBytes: html.length });
  if (html) previews.push('<h2>' + name + ' [' + mode + ']</h2>' + html);
  if (err) console.error('STEP FAIL', name, err);
};

await step('1 upload', 'FIXTURE synthetic job (no real upload service)', () => {
  send({ type: 'UPLOAD_STARTED', jobId: 'synthetic-job-v1' }); send({ type: 'JOB_UPDATE', job: job(1, 'running') }); send({ type: 'JOB_UPDATE', job: jobReady(2) });
  const h = render(); assert.match(h, /SYNTHETIC scene/); return h;
}, 'interview.active');
await step('2 interview', 'FIXTURE recorded agent response (S14 live pending)', () => {
  im = reduceInterview(im, { type: 'Q_LOADED', response: IV.responses['authored-three-kinds'], sceneId: IV.scene_id, toolOutputs: IV.tool_outputs });
  im = reduceInterview(im, { type: 'Q_CHIP', chipId: 'ball' }); im = reduceInterview(im, { type: 'Q_SUBMIT' });
  im = reduceInterview(im, { type: 'Q_TEXT', text: 'Released from rest by hand.' }); im = reduceInterview(im, { type: 'Q_SUBMIT' });
  im = reduceInterview(im, { type: 'Q_CHIP', chipId: 'table' }); im = reduceInterview(im, { type: 'Q_TEXT', text: 'about 2 m' }); im = reduceInterview(im, { type: 'Q_SUBMIT' });
  assert.equal(im.status, 'complete'); assert.equal(interviewAnswers(im).length, 3);
  return render();
}, 'interview.active');
await step('3 template/spec', 'FIXTURE recorded real Python validate_setup verdict', () => {
  tm = reduceTemplate(tm, { type: 'T_LOAD', template: 'free_fall' });
  for (const [param, a] of Object.entries(verdict.answers)) tm = reduceTemplate(tm, { type: 'T_EDIT', param, text: a.text });
  tm = reduceTemplate(tm, { type: 'T_SUBMIT' });
  tm = reduceTemplate(tm, { type: 'T_VERDICT', answers: verdict.answers, result: { ok: true, spec: verdict.spec } });
  assert.equal(tm.status, 'accepted'); spec = acceptedSpec(tm);
  send({ type: 'INTERVIEW_SPEC', spec }); return render();
}, 'run.ready');
await step('4 run', 'FIXTURE deterministic runner + REAL Build/simulator replay record', async () => {
  send({ type: 'RUN_START', seed: 7 });
  send({ type: 'R_LOAD', record: await prepareRun({ createReplayRecord, runner: fixtureRunner, parameters: runParameters, seed: 7 }) });
  for (let i = 0; i < 200 && !completionEvent(m.state, rm); i += 1) send({ type: 'R_TICK' });
  const c = completionEvent(m.state, rm); assert.ok(c, 'run completes'); send(c);
  return render();
}, 'run.done');
await step('5 instruments', 'FIXTURE recorded readings (real Build/instruments)', () => {
  ins = reduceInstruments(ins, { type: 'I_SELECT', id: 'stopwatch' }, m.state);
  return render({ instruments: ins });
}, 'run.done');
await step('6 fit', 'FIXTURE synthetic S11 reveal (reducer) + recorded REAL fitter output (panel)', () => {
  // FINDING: the reducer accepts a fit only via the S11 reveal body (parseFitReveal); the panel renders Build/fitter output,
  // which parseFitReveal rejects. No adapter exists yet (S14/S12/S13 integration); both are exercised separately here.
  assert.equal(parseFitReveal({ ...FIT.output, sessionId: 's15k' }, 's15k'), null);
  send({ type: 'FIT_START', sessionId: 's15k' }); send({ type: 'FIT_RESULT', body: fitBody('s15k') });
  const h = render({ fit: { times: FIT.request.times, output: FIT.output } }); assert.match(h, /class="ws-fit"/); return h;
}, 'fit.done');
await step('7 report', 'FIXTURE recorded Build.reports output', () => {
  send({ type: 'REPORT_OPEN' });
  const h = render({ report: RPT }); assert.match(h, /class="ws-report"/); return h;
}, 'report.open');

writeFileSync('evidence/S15/walk-steps.json', JSON.stringify({ label: 'FIXTURE walk, models + SSR, not browser/live', react: React.version, steps }, null, 2));
writeFileSync('evidence/S15/walk-preview.html', '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>S15k fixture walk (SYNTHETIC)</title><style>' + css + '</style><main><p><b>FIXTURE walk</b>: not live S14, not deployed, not gate/physical evidence.</p>' + previews.join('<hr>') + '</main>');
console.log(JSON.stringify(steps, null, 1)); process.exit(steps.every((s) => s.ok) ? 0 : 1);
