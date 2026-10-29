// S15e tests: parser, reducer (only validated spec edits accepted), view (units visible). Verdicts replay the REAL Python
// answers_to_spec -> validate_setup (recorded by evidence/S15/template_fixtures.py). SYNTHETIC; not Gate P/A or physical evidence.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { FIELDS, parseQuantity, initialTemplate, reduceTemplate, validationRequest, acceptedSpec, templateView } from '../../Build/web/src/workspace/template.mjs';
import { renderTemplate } from '../../Build/web/src/workspace/template-view.mjs';
import { reduce, initialState } from '../../Build/web/src/workspace/workflow.mjs';
import { jobReady } from '../../Build/web/src/workspace/fixtures.mjs';

const fx = JSON.parse(readFileSync(new URL('./fixtures/template-cases.json', import.meta.url), 'utf8'));
const verdictFor = (template, texts) => fx.verdicts.find((v) => v.template === template && FIELDS[template].map((fd) => v.answers[fd.param].text).join('|') === texts.join('|'));
const drive = (template, texts) => {
  let s = reduceTemplate(initialTemplate(), { type: 'T_LOAD', template });
  FIELDS[template].forEach((fd, i) => { s = reduceTemplate(s, { type: 'T_EDIT', param: fd.param, text: texts[i] }); });
  return reduceTemplate(s, { type: 'T_SUBMIT' });
};

test('FIELDS match the Python interview contract (params, units, accepted typed units)', () => {
  assert.deepEqual(Object.keys(FIELDS).sort(), Object.keys(fx.fields).sort());
  for (const [t, list] of Object.entries(fx.fields)) {
    assert.deepEqual(FIELDS[t].map((f) => [f.param, f.unit, Object.keys(f.units).sort()]), list.map((f) => [f.param, f.unit, f.units]));
  }
});

test('angle factors match Python (deg -> rad); angle needs a unit', () => {
  const fd = FIELDS.ramp[0];
  assert.ok(Math.abs(parseQuantity('30 deg', fd).value - 0.5235987755982988) < 1e-15);
  assert.equal(parseQuantity('30', fd).ok, false);
  assert.equal(parseQuantity('1.5 RAD', fd).value, 1.5);
});

test('parser rejects non-numbers, bad units, non-finite, unicode digits, overlong', () => {
  const fd = FIELDS.free_fall[0];
  for (const bad of ['', 'abc', '2 ft', '1e999', '٣', 'NaN', 'Infinity', '1'.repeat(65), null, 5]) assert.equal(parseQuantity(bad, fd).ok, false, String(bad));
  assert.equal(parseQuantity(' 2 m ', fd).value, 2);
});

test('accepts only what the validator accepted: every recorded verdict agrees with the reducer', () => {
  for (const v of fx.verdicts) {
    const texts = FIELDS[v.template].map((fd) => v.answers[fd.param].text);
    let s = drive(v.template, texts);
    if (s.status !== 'checking') { assert.equal(v.ok, false, 'local parse rejected a case the validator accepted: ' + JSON.stringify(v.answers)); continue; }
    assert.deepEqual(validationRequest(s).answers, v.answers);
    s = reduceTemplate(s, { type: 'T_VERDICT', answers: v.answers, result: v.ok ? { ok: true, spec: v.spec } : { ok: false, errors: v.errors } });
    assert.equal(s.status, v.ok ? 'accepted' : 'rejected', JSON.stringify(v.answers));
    assert.equal(acceptedSpec(s) !== null, v.ok);
    if (!v.ok) assert.ok(s.errors.length && s.spec === null);
  }
});

test('local parse failures never reach the validator and keep per-field errors', () => {
  const s = drive('ramp', ['30', '0.1', '0']);
  assert.equal(s.status, 'editing');
  assert.equal(validationRequest(s), null);
  assert.match(s.fieldErrors.incline_angle, /deg/);
  assert.equal(acceptedSpec(s), null);
});

test('forged, stale, mismatching or out-of-order verdicts are not accepted', () => {
  const v = verdictFor('free_fall', ['2', '0']);
  const checking = drive('free_fall', ['2', '0']);
  const ok = { ok: true, spec: v.spec };
  assert.equal(reduceTemplate(initialTemplate(), { type: 'T_VERDICT', answers: v.answers, result: ok }).status, 'empty');
  assert.equal(reduceTemplate(reduceTemplate(initialTemplate(), { type: 'T_LOAD', template: 'free_fall' }), { type: 'T_VERDICT', answers: v.answers, result: ok }).status, 'editing');
  assert.equal(reduceTemplate(checking, { type: 'T_VERDICT', answers: { ...v.answers, drop_height: { text: '3' } }, result: ok }), checking); // stale answers
  const other = verdictFor('free_fall', ['2', '0']).spec;
  const wrongNumber = structuredClone(other); wrongNumber.parameters.drop_height.value = 99;
  assert.equal(reduceTemplate(checking, { type: 'T_VERDICT', answers: v.answers, result: { ok: true, spec: wrongNumber } }).status, 'rejected');
  const wrongUnit = structuredClone(other); wrongUnit.parameters.drop_height.unit = 'ft';
  assert.equal(reduceTemplate(checking, { type: 'T_VERDICT', answers: v.answers, result: { ok: true, spec: wrongUnit } }).status, 'rejected');
  const wrongTemplate = verdictFor('projectile', ['2', '1.5']).spec;
  assert.equal(reduceTemplate(checking, { type: 'T_VERDICT', answers: v.answers, result: { ok: true, spec: wrongTemplate } }).status, 'rejected');
  for (const result of [undefined, null, {}, { ok: 'yes', spec: other }, { ok: false }]) assert.notEqual(reduceTemplate(checking, { type: 'T_VERDICT', answers: v.answers, result }).status, 'accepted');
});

test('editing clears an accepted spec; edits are blocked while checking; illegal events return the same object', () => {
  const v = verdictFor('free_fall', ['2', '0']);
  const checking = drive('free_fall', ['2', '0']);
  assert.equal(reduceTemplate(checking, { type: 'T_EDIT', param: 'drop_height', text: '5' }), checking);
  assert.equal(reduceTemplate(checking, { type: 'T_LOAD', template: 'ramp' }), checking);
  assert.equal(reduceTemplate(checking, { type: 'T_SUBMIT' }), checking);
  const accepted = reduceTemplate(checking, { type: 'T_VERDICT', answers: v.answers, result: { ok: true, spec: v.spec } });
  const edited = reduceTemplate(accepted, { type: 'T_EDIT', param: 'drop_height', text: '5' });
  assert.equal(edited.status, 'editing'); assert.equal(acceptedSpec(edited), null);
  assert.equal(reduceTemplate(edited, { type: 'T_EDIT', param: '__proto__', text: 'x' }), edited);
  assert.equal(reduceTemplate(edited, { type: 'T_EDIT', param: 'toString', text: 'x' }), edited);
  const empty = initialTemplate();
  for (const e of [{ type: 'T_EDIT', param: 'drop_height', text: '1' }, { type: 'T_SUBMIT' }, { type: 'NOPE' }, null]) assert.equal(reduceTemplate(empty, e), empty);
  assert.equal(reduceTemplate(empty, { type: 'T_LOAD', template: 'constructor' }), empty);
  assert.equal(reduceTemplate(accepted, { type: 'T_RESET' }).status, 'empty');
});

test('control characters are stripped and input length bounded', () => {
  let s = reduceTemplate(initialTemplate(), { type: 'T_LOAD', template: 'free_fall' });
  s = reduceTemplate(s, { type: 'T_EDIT', param: 'drop_height', text: '1\u0000\n2' + 'x'.repeat(100) });
  assert.ok(s.texts.drop_height.length <= 64 && !/[\u0000-\u001f]/.test(s.texts.drop_height));
});

test('T_LOAD prefills from a spec only for contract-unit numbers', () => {
  const s = reduceTemplate(initialTemplate(), { type: 'T_LOAD', template: 'free_fall', spec: verdictFor('free_fall', ['2', '0']).spec });
  assert.deepEqual(s.texts, { drop_height: '2', initial_vertical_velocity: '0' });
});

test('accepted spec passes the S15a reducer only with its validator; fail-closed without one', () => {
  const v = verdictFor('free_fall', ['2', '0']);
  let w = reduce(initialState(), { type: 'UPLOAD_STARTED', jobId: 'synthetic-job-v1' });
  w = reduce(w, { type: 'JOB_UPDATE', job: jobReady(1) });
  assert.equal(w.phase, 'interview.active');
  assert.equal(reduce(w, { type: 'INTERVIEW_SPEC', spec: v.spec }).phase, 'interview.active'); // no validator injected
  const strict = { validateSpec: (spec) => (spec?.template === 'free_fall' ? { ok: true } : { ok: false, errors: ['no'] }) };
  assert.equal(reduce(w, { type: 'INTERVIEW_SPEC', spec: v.spec }, strict).phase, 'run.ready');
});

// ---- view: tiny h() that builds a plain tree
const h = (type, props, ...kids) => ({ type, props: props ?? {}, kids: kids.flat().filter((k) => k !== null && k !== undefined && k !== false) });
const walk = (n, f) => { if (n && typeof n === 'object') { f(n); n.kids?.forEach((k) => walk(k, f)); } };
const textOf = (n) => (typeof n === 'string' ? n : n.kids.map(textOf).join(' '));
const find = (n, pred) => { const out = []; walk(n, (x) => pred(x) && out.push(x)); return out; };

test('view: every field label shows its unit and hint; check button reports T_SUBMIT', () => {
  for (const t of Object.keys(FIELDS)) {
    const sent = [];
    const tree = renderTemplate(h, templateView(reduceTemplate(initialTemplate(), { type: 'T_LOAD', template: t })), 'interview.active', (a) => sent.push(a));
    const labels = find(tree, (n) => n.type === 'label').map(textOf);
    assert.equal(labels.length, FIELDS[t].length);
    FIELDS[t].forEach((fd, i) => { assert.ok(labels[i].includes('(' + fd.unit + ')'), labels[i]); for (const u of Object.keys(fd.units).filter(Boolean)) assert.ok(labels[i].includes(u), labels[i] + ' lacks ' + u); });
    find(tree, (n) => n.type === 'input')[0].props.onChange({ target: { value: '2' } });
    tree.props.onSubmit({ preventDefault() {} });
    assert.deepEqual(sent, [{ type: 'T_EDIT', param: FIELDS[t][0].param, text: '2' }, { type: 'T_SUBMIT' }]);
  }
});

test('view: disabled without onAction, while checking and when locked (run.ready); accepted values show units; errors are alerts', () => {
  const v = verdictFor('pendulum', ['1', '3 deg', '0']);
  const checking = drive('pendulum', ['1', '3 deg', '0']);
  const fs = (tree) => find(tree, (n) => n.type === 'fieldset')[0].props.disabled;
  assert.equal(fs(renderTemplate(h, templateView(checking), 'interview.active', () => {})), true);
  assert.equal(fs(renderTemplate(h, templateView(reduceTemplate(initialTemplate(), { type: 'T_LOAD', template: 'pendulum' })), 'interview.active', undefined)), true);
  const accepted = reduceTemplate(checking, { type: 'T_VERDICT', answers: v.answers, result: { ok: true, spec: v.spec } });
  const locked = renderTemplate(h, templateView(accepted), 'run.ready', () => {});
  assert.equal(fs(locked), true);
  const items = find(locked, (n) => n.props.className === 'ws-accepted')[0].kids.map(textOf);
  assert.deepEqual(items, ['Length: 1 m', 'Release angle: ' + v.spec.parameters.release_angle.value + ' rad', 'Initial angular speed: 0 rad/s']);
  const sent = [];
  find(renderTemplate(h, templateView(accepted), 'run.ready', (a) => sent.push(a)), (n) => n.props.className === 'ws-back')[0].props.onClick();
  assert.deepEqual(sent, [{ type: 'EDIT_SPEC' }]);
  const rej = reduceTemplate(drive('free_fall', ['-1', '0']), { type: 'T_VERDICT', answers: verdictFor('free_fall', ['-1', '0']).answers, result: { ok: false, errors: verdictFor('free_fall', ['-1', '0']).errors } });
  const tree = renderTemplate(h, templateView(rej), 'interview.active', () => {});
  assert.ok(find(tree, (n) => n.props.role === 'alert').map(textOf).join().includes('must be > 0'));
  assert.equal(renderTemplate(h, templateView(initialTemplate()), 'interview.active', () => {}), null);
});

test('view: user text is data only (no raw HTML props)', () => {
  const s = reduceTemplate(reduceTemplate(initialTemplate(), { type: 'T_LOAD', template: 'free_fall' }), { type: 'T_EDIT', param: 'drop_height', text: '<img onerror=x>' });
  const tree = renderTemplate(h, templateView(s), 'interview.active', () => {});
  assert.equal(find(tree, (n) => 'dangerouslySetInnerHTML' in n.props).length, 0);
});

