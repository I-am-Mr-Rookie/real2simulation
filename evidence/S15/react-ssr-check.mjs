// S15b evidence: render the React binding with real React 19 (SSR) and assert slot markup. React is resolved from
// the canonical Build/web/node_modules (read-only, no install). Usage: node evidence/S15/react-ssr-check.mjs <path-to-Build/web/node_modules>
import { createRequire } from 'node:module';
import assert from 'node:assert/strict';
import { readFileSync, writeFileSync } from 'node:fs';
import { createWorkspace } from '../../Build/web/src/workspace/react.mjs';
import { initialState, reduce } from '../../Build/web/src/workspace/workflow.mjs';
import { jobReady } from '../../Build/web/src/workspace/fixtures.mjs';

const req = createRequire(process.argv[2].replace(/[\\/]?$/, '/') + 'x.js');
const React = req('react'), { renderToString } = req('react-dom/server');
const Workspace = createWorkspace(React);
const adapter = { mount: () => assert.fail('SSR must not mount') };
const render = (state) => renderToString(React.createElement(Workspace, { state, adapter, loadScene: () => {} }));

const idle = render(initialState());
for (const slot of ['stage-nav', 'viewport', 'panel', 'job-status']) assert.match(idle, new RegExp('data-slot="' + slot + '"'));
assert.match(idle, /data-viewer-status="empty"/); assert.match(idle, /aria-current="step"/); assert.doesNotMatch(idle, /SYNTHETIC/);
const withScene = reduce(reduce(initialState(), { type: 'UPLOAD_STARTED', jobId: 'synthetic-job-v1' }), { type: 'JOB_UPDATE', job: jobReady(1) });
const html = render(withScene);
assert.match(html, /SYNTHETIC scene/); assert.match(html, /<div class="ws-host"[^>]*><\/div>/); assert.match(html, /Job synthetic-job-v1/);
// Static preview for a manual responsive check (viewer canvas absent: the host is an empty dark box).
const css = readFileSync('Build/web/src/app/styles.css', 'utf8') + readFileSync('Build/web/src/workspace/workspace.css', 'utf8');
writeFileSync('evidence/S15/layout-preview.html', '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>S15b layout preview (SYNTHETIC)</title><style>' + css + '</style><main>' + html + '</main>');
console.log('react', React.version, 'SSR ok; idle', idle.length, 'bytes, scene', html.length, 'bytes');

// S15c: failure surface through the real React binding (SSR).
import { initialLogged as IL, reduceLogged as RL } from '../../Build/web/src/workspace/status.mjs';
import { job as jobF } from '../../Build/web/src/workspace/fixtures.mjs';
{
  let m = IL();
  for (const e of [{ type: 'UPLOAD_STARTED', jobId: 'synthetic-job-v1' }, { type: 'JOB_UPDATE', job: jobF(1, 'running') },
    { type: 'JOB_UPDATE', job: jobF(2, 'failed', { error: { code: 'DEPENDENCY_UNAVAILABLE', message: 'SYNTHETIC failure fixture' } }) }]) m = RL(m, e);
  const out = renderToString(React.createElement(Workspace, { state: m.state, log: m.log, onAction: () => {}, adapter, loadScene: () => {} }));
  for (const re of [/class="ws-timeline"/, /data-status="failed"/, /Job update r2: failed/, /Upload failed/, /Retrying later may work/, /Not available: Scene: none was created/, /data-event="UPLOAD_STARTED"/, /Start a new upload/])
    assert.match(out, re);
  assert.doesNotMatch(out, /disabled=""/);
  const noRetry = renderToString(React.createElement(Workspace, { state: RL(RL(IL(), { type: 'UPLOAD_STARTED', jobId: 'synthetic-job-v1' }), { type: 'JOB_UPDATE', job: jobF(1, 'failed', { error: { code: 'SPEND_PAUSED', message: 'SYNTHETIC' } }) }).state, adapter, loadScene: () => {} }));
  assert.doesNotMatch(noRetry, /ws-retry/); assert.match(noRetry, /Retry is not available/);
  writeFileSync('evidence/S15/failure-preview.html', '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>S15c failure preview (SYNTHETIC)</title><style>' + css + '</style><main>' + out + '</main>');
  console.log('S15c SSR ok: failure surface, retry button, blocked-retry copy');
}

// S15d: interview panel through the real React binding (SSR), plus a static preview for the in-app browser check.
import { initialInterview as II, reduceInterview as RI } from '../../Build/web/src/workspace/interview.mjs';
{
  const fx = JSON.parse(readFileSync('tests/workspace/fixtures/interview-responses.json', 'utf8'));
  const ev = (m, ...es) => es.reduce(RI, m);
  const iv = ev(II(), { type: 'Q_LOADED', response: fx.responses['authored-three-kinds'], sceneId: fx.scene_id, toolOutputs: fx.tool_outputs },
    { type: 'Q_CHIP', chipId: 'ball' }, { type: 'Q_SUBMIT' }, { type: 'Q_TEXT', text: 'Dropped from the <b>edge</b>' }, { type: 'Q_SUBMIT' });
  const out = renderToString(React.createElement(Workspace, { state: withScene, interview: iv, onAction: () => {}, adapter, loadScene: () => {} }));
  for (const re of [/class="ws-interview"/, /Question 3 of 3/, /Release surface\?/, /aria-pressed="false"/, /Compare with 9\.8 ± 0\.1 m\/s\^2 \(simulated\)/,
    /Dropped from the &lt;b&gt;edge&lt;\/b&gt;/, /maxLength="500"|maxlength="500"/i, /Finish/]) assert.match(out, re);
  assert.doesNotMatch(out, /<b>edge/);
  assert.doesNotMatch(renderToString(React.createElement(Workspace, { state: withScene, adapter, loadScene: () => {} })), /ws-interview/);
  assert.match(renderToString(React.createElement(Workspace, { state: withScene, interview: iv, adapter, loadScene: () => {} })), /disabled/);
  writeFileSync('evidence/S15/interview-preview.html', '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>S15d interview preview (SYNTHETIC)</title><style>' + css + '</style><main>' + out + '</main>');
  console.log('S15d SSR ok: interview panel, escaped free text, disabled without onAction');
}

// S15e: template controls through the real React binding (SSR) with verdicts recorded from the Python validator; static preview for the in-app browser.
import { initialTemplate as IT, reduceTemplate as RT, FIELDS as TF } from '../../Build/web/src/workspace/template.mjs';
{
  const cases = JSON.parse(readFileSync('tests/workspace/fixtures/template-cases.json', 'utf8')).verdicts;
  const pend = cases.find((v) => v.template === 'pendulum' && v.ok && v.answers.release_angle.text === '3 deg');
  const bad = cases.find((v) => v.template === 'free_fall' && !v.ok && /must be > 0/.test(v.errors[0]));
  const noUnit = cases.find((v) => v.template === 'ramp' && !v.ok);
  const enter = (v) => TF[v.template].reduce((s, fd) => RT(s, { type: 'T_EDIT', param: fd.param, text: v.answers[fd.param].text }), RT(IT(), { type: 'T_LOAD', template: v.template }));
  const verdict = (v, s) => RT(RT(s, { type: 'T_SUBMIT' }), { type: 'T_VERDICT', answers: v.answers, result: v.ok ? { ok: true, spec: v.spec } : { ok: false, errors: v.errors } });
  const R = (state, template, onAction = () => {}) => renderToString(React.createElement(Workspace, { state, template, onAction, adapter, loadScene: () => {} }));
  const rejected = R(withScene, verdict(bad, enter(bad)));
  for (const re of [/class="ws-template"/, /data-status="rejected"/, /Drop height \(m\)/, /Initial upward speed \(m\/s\)/, /m \(blank = m\)/, /role="alert"/, /must be &gt; 0/]) assert.match(rejected, re);
  const local = R(withScene, RT(enter(noUnit), { type: 'T_SUBMIT' })); // typed "30" for an angle: refused locally, never sent to the validator
  for (const re of [/Incline angle \(rad\)/, /rad or deg or ° \(unit required\)/, /Friction coefficient \(1\)/, /unitless number/, /data-status="editing"/, /aria-invalid="true"/]) assert.match(local, re);
  const acc = verdict(pend, enter(pend));
  assert.match(R(withScene, acc), /Setup accepted\./); assert.match(R(withScene, acc), /Length: 1 m/);
  const runReady = reduce(withScene, { type: 'INTERVIEW_SPEC', spec: pend.spec }, { validateSpec: () => ({ ok: true }) });
  const locked = R(runReady, acc);
  assert.equal(runReady.phase, 'run.ready'); assert.match(locked, /Edit setup/); assert.match(locked, /Release angle: 0\.05235987755982989 rad/); assert.match(locked, /<fieldset[^>]*disabled/);
  assert.doesNotMatch(renderToString(React.createElement(Workspace, { state: withScene, adapter, loadScene: () => {} })), /ws-template/);
  assert.match(renderToString(React.createElement(Workspace, { state: withScene, template: acc, adapter, loadScene: () => {} })), /<fieldset[^>]*disabled/);
  writeFileSync('evidence/S15/template-preview.html', '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>S15e template preview (SYNTHETIC)</title><style>' + css + '</style><main>' + rejected + '</main>');
  console.log('S15e SSR ok: units visible, validator rejection shown, accepted spec locks controls in run.ready, disabled without onAction');
}




// S15f: run controls through the real React binding (SSR): paused mid-run, then done + same-seed replay verified.
import { initialRun as IR, reduceRun as RR, prepareRun as PR, verifyReplay as VR } from '../../Build/web/src/workspace/runcontrol.mjs';
import { runParameters as RP, fixtureRunner as FR, deps as D6, validSpec as VS } from '../../Build/web/src/workspace/fixtures.mjs';
import { createReplayRecord as CRR, replayRecord as RPR } from '../../Build/simulator/replay.mjs';
{
  const ready = reduce(withScene, { type: 'INTERVIEW_SPEC', spec: VS }, D6);
  let s = reduce(ready, { type: 'RUN_START', seed: 11 }, D6), m = IR();
  const send = (e) => { m = RR(m, e, s); s = reduce(s, e, D6); };
  send({ type: 'R_LOAD', record: await PR({ createReplayRecord: CRR, runner: FR, parameters: RP, seed: 11 }) });
  for (let i = 0; i < 3; i += 1) send({ type: 'R_TICK' });
  send({ type: 'RUN_PAUSE' });
  const R = (state, run) => renderToString(React.createElement(Workspace, { state, run, onAction: () => {}, adapter, loadScene: () => {} }));
  const paused = R(s, m);
  for (const re of [/class="ws-run"/, /Paused\. Playback is frozen/, /Resume/, /Cancel run/, /Frame 3 of 8/, /<progress[^>]*max="8"[^>]*value="3"/, /Seed 11 \(simulated/]) assert.match(paused, re);
  assert.doesNotMatch(paused, />Pause</);
  assert.doesNotMatch(R(s), /ws-run/); assert.match(renderToString(React.createElement(Workspace, { state: s, run: m, adapter, loadScene: () => {} })), /<button[^>]*disabled/);
  send({ type: 'RUN_RESUME' }); for (let i = 0; i < 5; i += 1) send({ type: 'R_TICK' });
  send({ type: 'RUN_COMPLETE', seed: 11, observations: m.record.trace }); send({ type: 'R_REPLAY_START' });
  send({ type: 'R_REPLAY_RESULT', result: await VR({ replayRecord: RPR, record: m.record, runner: FR }) });
  const done = R(s, m);
  for (const re of [/Run finished \(simulated\)/, /Run again/, /Replay with same seed/, /Replay matched: identical trace and hashes\./, /Frame 8 of 8/]) assert.match(done, re);
  writeFileSync('evidence/S15/run-preview.html', '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>S15f run controls preview (SYNTHETIC)</title><style>' + css + '</style><main>' + paused + '<hr>' + done + '</main>');
  console.log('S15f SSR ok: paused mid-run controls, done + same-seed replay verified, hidden without run model, disabled without onAction');
}

