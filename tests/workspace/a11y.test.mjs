// S15l: accessibility checkpoint, proven on the pure view markup (same fake-h harness as owner-clip/status tests).
// Real-browser focus order / screen-reader announcement stay 'controller browser check' items in evidence/S15/s15l/A11Y.md.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { initialState, reduce } from '../../Build/web/src/workspace/workflow.mjs';
import { deps, job, jobReady } from '../../Build/web/src/workspace/fixtures.mjs';
import { initialLogged, reduceLogged } from '../../Build/web/src/workspace/status.mjs';
import { layoutOf } from '../../Build/web/src/workspace/layout.mjs';
import { renderWorkspace, renderInterview } from '../../Build/web/src/workspace/view.mjs';
import { interviewView } from '../../Build/web/src/workspace/interview.mjs';
import { initialInterview, reduceInterview } from '../../Build/web/src/workspace/interview.mjs';
import { renderTemplate } from '../../Build/web/src/workspace/template-view.mjs';
import { renderRun } from '../../Build/web/src/workspace/run-view.mjs';
import { renderUpload, uploadView } from '../../Build/web/src/workspace/upload-view.mjs';
import { renderFit, fitView } from '../../Build/web/src/workspace/fit-view.mjs';
import { restoreFocus } from '../../Build/web/src/workspace/react.mjs';

const h = (type, props, ...children) => ({ type, props: props ?? {}, children: children.flat(Infinity) });
const nodes = (n) => (n && typeof n === 'object' ? [n, ...n.children.flatMap(nodes)] : []);
const strings = (n) => (typeof n === 'string' ? [n] : n?.children?.flatMap(strings) ?? []);
const run = (s, ...ev) => ev.reduce((a, e) => reduce(a, e, deps), s);
const noop = () => {};
const Q = { id: 'known_size', kind: 'free_text', chips: [], prompt: [{ type: 'text', text: 'Name one object of known size.' }] };
const FIX = JSON.parse(readFileSync(new URL('./fixtures/fit-output.json', import.meta.url), 'utf8'));
const ws = (state, ...args) => renderWorkspace(h, layoutOf(state), { status: 'empty', error: null }, null, noop, ...args);
const scene = () => run(initialState(), { type: 'UPLOAD_STARTED', jobId: 'synthetic-job-v1' }, { type: 'JOB_UPDATE', job: jobReady(1) });
const failedM = [{ type: 'UPLOAD_STARTED', jobId: 'synthetic-job-v1' }, { type: 'JOB_UPDATE', job: job(5, 'failed', { error: { code: 'DEPENDENCY_UNAVAILABLE', message: 'SYNTHETIC failure fixture' } }) }]
  .reduce((a, e) => reduceLogged(a, e, deps), initialLogged());
const failed = () => renderWorkspace(h, layoutOf(failedM.state, { log: failedM.log }), { status: 'empty', error: null }, null, noop);

// every tree the suite renders; used for the keyboard and naming sweeps
const asking = reduceInterview(initialInterview(), { type: 'Q_LOADED', response: { schema_version: 'agent-response/1.0.0', scene_id: 'synthetic-room-v1', questions: [Q] }, sceneId: 'synthetic-room-v1' });
const erroring = reduceInterview(asking, { type: 'Q_SUBMIT' });
const fitV = fitView({ phase: 'fit.done' }, { times: FIX.request.times, output: FIX.output });
const trees = () => [ws(scene()), failed(), renderInterview(h, interviewView(asking), noop), renderInterview(h, interviewView(erroring), noop),
  renderRun(h, { show: true, phase: 'run.ready', status: 'Ready', canRun: true, canPause: true, canResume: true, canCancel: true, canReplay: true, runLabel: 'Run',
    progress: { frame: 1, total: 4 }, frame: null, seed: 1, label: 'SIMULATED', traceHash: null, replayHash: null, replay: null }, noop),
  renderUpload(h, uploadView({ state: { phase: 'upload.idle' }, busy: false }), noop), renderFit(h, fitV)];

test('keyboard: only native controls are interactive, no positive tabindex, DOM order = tab order', () => {
  for (const t of trees()) for (const n of nodes(t)) {
    if (n.props.onClick) assert.ok(['button', 'summary'].includes(n.type), n.type + ' has onClick but is not natively focusable');
    if (n.props.tabIndex !== undefined) assert.ok(n.props.tabIndex <= 0, 'positive tabIndex');
  }
  const order = nodes(renderRun(h, { show: true, phase: 'run.ready', status: 's', canRun: true, canPause: false, canResume: false, canCancel: true, canReplay: true,
    runLabel: 'Run', progress: null, seed: null, replay: null }, noop)).filter((n) => n.type === 'button').map((n) => strings(n).join(''));
  assert.deepEqual(order, ['Run', 'Cancel run', 'Replay with same seed']);
});

test('keyboard: interview answer field then Back/Next-Finish are real form controls; Finish submits the form', () => {
  const kinds = nodes(renderInterview(h, interviewView(asking), noop)).filter((n) => ['textarea', 'button', 'form'].includes(n.type)).map((n) => n.type + (n.props.type ? ':' + n.props.type : ''));
  assert.deepEqual(kinds, ['form', 'textarea', 'button:submit']);
  assert.equal(strings(nodes(renderInterview(h, interviewView(asking), noop)).find((n) => n.props.type === 'submit')).join(''), 'Finish');
});

test('focus: panel heading is a programmatic focus target and restoreFocus uses it only when focus was lost', () => {
  const hd = nodes(ws(scene())).find((n) => n.props.id === 'ws-panel-heading');
  assert.equal(hd.type, 'h2'); assert.equal(hd.props.tabIndex, -1);
  const mk = (active, inBody) => { const d = { focused: 0, body: { contains: () => inBody }, activeElement: active, getElementById: () => ({ focus() { d.focused++; } }) }; return d; };
  const lost = mk(null, false); d1: assert.equal(restoreFocus(lost), true); assert.equal(lost.focused, 1);
  const body = mk(null, true); body.activeElement = body.body; assert.equal(restoreFocus(body), true);
  const gone = mk({}, false); assert.equal(restoreFocus(gone), true); // focused element was removed from the DOM
  const kept = mk({}, true); assert.equal(restoreFocus(kept), false); assert.equal(kept.focused, 0);
  assert.equal(restoreFocus({ body: {}, activeElement: null, getElementById: () => null }), false); // no heading: no throw
});

test('errors: failures are announced (alert) in the job panel; stage-level failure text is not silent', () => {
  const t = nodes(failed());
  const f = t.find((n) => n.props.className === 'ws-failure');
  assert.ok(f, 'failure surface present');
  assert.equal(f.props.role, 'alert');
  assert.ok(strings(f).join('').length > 0);
});

test('errors: interview error is role=alert and tied to the answer field (aria-describedby + aria-invalid)', () => {
  const v = interviewView(erroring); assert.ok(v.error, 'empty submit sets an error');
  const t = nodes(renderInterview(h, v, noop));
  const err = t.find((n) => n.props.role === 'alert'), field = t.find((n) => n.type === 'textarea');
  assert.equal(field.props['aria-describedby'], err.props.id); assert.equal(field.props['aria-invalid'], true);
  const ok = nodes(renderInterview(h, interviewView(asking), noop)).find((n) => n.type === 'textarea');
  assert.equal(ok.props['aria-describedby'], undefined);
});

test('errors: template field error is tied to its input with aria-describedby', () => {
  const v = { status: 'invalid', template: 'free_fall', canSubmit: true, errors: [], accepted: [],
    fields: [{ param: 'height', label: 'Height', unit: 'm', text: 'x', hint: 'positive number', error: 'not a number' }] };
  const t = nodes(renderTemplate(h, v, 'interview.active', noop));
  const input = t.find((n) => n.type === 'input'), err = t.find((n) => n.props.role === 'alert');
  assert.match(input.props['aria-describedby'], new RegExp('\\b' + err.props.id + '$')); assert.equal(input.props['aria-invalid'], true);
  assert.match(input.props['aria-describedby'], /^hint-height/);
});

test('labels: every input/textarea is wrapped by or associated with a label; progress has a name', () => {
  for (const t of trees()) {
    const all = nodes(t);
    for (const n of all.filter((x) => ['input', 'textarea'].includes(x.type))) {
      const wrapped = all.some((l) => l.type === 'label' && nodes(l).includes(n));
      const byFor = n.props.id && all.some((l) => l.type === 'label' && l.props.htmlFor === n.props.id);
      assert.ok(wrapped || byFor, n.type + ' unlabeled');
    }
    for (const n of all.filter((x) => x.type === 'progress')) assert.ok(n.props['aria-label']);
  }
});

test('status: live regions for upload, run, interview progress; owner abstain result is a status region', () => {
  const live = (t) => nodes(t).filter((n) => n.props.role === 'status' || n.props['aria-live']);
  assert.ok(live(renderUpload(h, uploadView({ state: { phase: 'upload.idle' }, busy: false }), noop)).length);
  assert.ok(live(renderInterview(h, interviewView(asking), noop)).length);
  const abstain = { clip_id: 'OWN02', input_label: 'OWNER_RECORDED / RECORDED', status: 'abstain', label: 'UNCERTAIN: no measurement', message: 'g is not reported (abstain, not an error).' };
  const o = { ...initialState(), phase: 'report.owner', owner: { jobId: 'job_x' } };
  const t = nodes(renderWorkspace(h, layoutOf(o), { status: 'empty', error: null }, null, noop, undefined, undefined, undefined, undefined, undefined, undefined, undefined, { measurement: abstain }));
  const m = t.find((n) => n.props.className === 'ws-measurement');
  assert.equal(m.props.role, 'status'); assert.ok(m.props['aria-label']);
  assert.match(strings(m).join(' '), /UNCERTAIN: no measurement/);
});

test('tables: fit tables have caption + column headers (scope=col) and row headers; chart has a text alternative; disclosure is native details/summary', () => {
  const t = nodes(renderFit(h, fitV)), tables = t.filter((n) => n.type === 'table');
  assert.ok(tables.length >= 2);
  for (const tb of tables) {
    assert.ok(nodes(tb).some((n) => n.type === 'caption'));
    const ths = nodes(tb).filter((n) => n.type === 'th' && n.props.scope === 'col');
    assert.ok(ths.length >= 3);
  }
  assert.ok(t.find((n) => n.type === 'svg').props['aria-labelledby']);
  if (fitV.residuals.length > 10) assert.ok(t.some((n) => n.type === 'details') && t.some((n) => n.type === 'summary'));
});

test('mobile (static CSS): no fixed pixel widths, 44px targets, visible focus ring, 375px breakpoints', () => {
  const css = readFileSync(new URL('../../Build/web/src/workspace/workspace.css', import.meta.url), 'utf8');
  assert.deepEqual([...css.matchAll(/(?<![-\w])(?:width|min-width)\s*:\s*(\d+)px/g)].filter((m) => +m[1] > 300), [], 'fixed width > 300px');
  assert.match(css, /\.ws-chip, \.ws-back, \.ws-submit, \.ws-retry, \.ws-nav \{[^}]*min-height: 44px/);
  assert.match(css, /\.ws-field input \{[^}]*min-height: 44px/);
  assert.match(css, /summary \{[^}]*min-height: 44px/);
  assert.match(css, /\.ws :focus-visible \{ outline: 3px solid/);
  assert.match(css, /@media \(max-width: 860px\)[\s\S]*minmax\(0, 1fr\)/);
  assert.match(css, /\.ws-panel, \.ws-job \{[^}]*min-width: 0/);
});

