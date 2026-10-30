import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { initialLogged, reduceLogged } from '../../Build/web/src/workspace/status.mjs';
import { job, jobReady, runParameters, fixtureRunner, fitBody } from '../../Build/web/src/workspace/fixtures.mjs';
import { initialTemplate, reduceTemplate, acceptedSpec } from '../../Build/web/src/workspace/template.mjs';
import { initialRun, reduceRun, prepareRun, completionEvent } from '../../Build/web/src/workspace/runcontrol.mjs';
import { parseFitReveal } from '../../Build/web/src/lab/fit-contract.mjs';
import { createReplayRecord } from '../../Build/simulator/replay.mjs';

// S15k: model-level full walk (FIXTURE data) with a host loop; evidence/S15/walk-check.mjs does the same through React SSR.
const fx = (n) => JSON.parse(readFileSync(new URL('./fixtures/' + n, import.meta.url), 'utf8'));

test('fixture walk: upload -> spec -> run -> fit -> report, each stage legal; real fitter output is NOT an S11 reveal (known gap)', async () => {
  const verdict = fx('template-cases.json').verdicts.find((v) => v.template === 'free_fall' && v.ok);
  let m = initialLogged(), rm = initialRun(), tm = initialTemplate(), spec = null;
  const deps = { validateSpec: (s) => (s && s === spec ? { ok: true } : { ok: false, errors: ['not the accepted spec'] }) };
  const send = (e) => { m = reduceLogged(m, e, deps); rm = reduceRun(rm, e, m.state); };
  const phases = [];
  send({ type: 'UPLOAD_STARTED', jobId: 'synthetic-job-v1' }); send({ type: 'JOB_UPDATE', job: job(1, 'running') }); send({ type: 'JOB_UPDATE', job: jobReady(2) });
  phases.push(m.state.phase);
  tm = reduceTemplate(tm, { type: 'T_LOAD', template: 'free_fall' });
  for (const [param, a] of Object.entries(verdict.answers)) tm = reduceTemplate(tm, { type: 'T_EDIT', param, text: a.text });
  tm = reduceTemplate(tm, { type: 'T_SUBMIT' });
  tm = reduceTemplate(tm, { type: 'T_VERDICT', answers: verdict.answers, result: { ok: true, spec: verdict.spec } });
  spec = acceptedSpec(tm); send({ type: 'INTERVIEW_SPEC', spec }); phases.push(m.state.phase);
  send({ type: 'RUN_START', seed: 7 });
  send({ type: 'R_LOAD', record: await prepareRun({ createReplayRecord, runner: fixtureRunner, parameters: runParameters, seed: 7 }) });
  for (let i = 0; i < 200 && !completionEvent(m.state, rm); i += 1) send({ type: 'R_TICK' });
  send(completionEvent(m.state, rm)); phases.push(m.state.phase);
  send({ type: 'FIT_START', sessionId: 's15k' }); send({ type: 'FIT_RESULT', body: fitBody('s15k') }); phases.push(m.state.phase);
  send({ type: 'REPORT_OPEN' }); phases.push(m.state.phase);
  assert.deepEqual(phases, ['interview.active', 'run.ready', 'run.done', 'fit.done', 'report.open']);
  assert.equal(m.state.run.label, 'simulated');
  // Gap pin: Build/fitter output (what the fit panel renders) has no adapter to the S11 reveal the reducer requires.
  assert.equal(parseFitReveal({ ...fx('fit-output.json').output, sessionId: 's15k' }, 's15k'), null);
});
