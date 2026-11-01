// S15bd (S22h findings): same-file retry, plain 422 copy, Try again, session-reset note, recorded-reference divider.
import test from 'node:test';
import assert from 'node:assert/strict';
import { createController } from '../../Build/web/src/workspace/controller.mjs';
import { layoutOf } from '../../Build/web/src/workspace/layout.mjs';
import { renderWorkspace, NOT_APPROVED } from '../../Build/web/src/workspace/view.mjs';
import { renderUpload } from '../../Build/web/src/workspace/upload-view.mjs';
import { routeAction, sessionNote, SESSION_RESET } from '../../Build/web/src/shell/PrivateWorkspace.mjs';

const h = (type, props, ...children) => ({ type, props: props ?? {}, children: children.flat(Infinity) });
const strings = (n) => (typeof n === 'string' ? [n] : n?.children?.flatMap(strings) ?? []);
const find = (n, pred) => (n && typeof n === 'object' ? (pred(n) ? [n] : []).concat((n.children ?? []).flatMap((c) => find(c, pred))) : []);
const file = () => new File([new Uint8Array([1, 2, 3])], 'a.mp4', { type: 'video/mp4' });
const render = (ctl) => renderWorkspace(h, layoutOf(ctl.state, { audience: 'signed-in' }), { status: 'empty', error: null }, null, () => {});

test('same-file re-pick: the input is cleared after reading the file', () => {
  const got = [];
  const tree = renderUpload(h, { show: true, disabled: false, status: 's' }, (f) => got.push(f));
  const input = find(tree, (n) => n.type === 'input')[0];
  const e = { target: { files: ['F'], value: 'C:\\fake\\a.mp4' } };
  input.props.onChange(e);
  assert.deepEqual(got, ['F']);
  assert.equal(e.target.value, '');
});

test('service down: visible Try again re-runs the last upload', async () => {
  let up = false, n = 0;
  const f = async () => { n += 1; if (!up) throw new Error('offline'); return { ok: true, status: 200, json: async () => ({}) }; };
  const ctl = createController({ fetch: f });
  await ctl.upload(file());
  const btn = find(render(ctl), (x) => x.props['data-event'] === 'UPLOAD_RETRY')[0];
  assert.equal(strings(btn).join(''), 'Try again');
  const before = n; up = true;
  await routeAction(ctl, {}, { type: 'UPLOAD_RETRY' });
  assert.ok(n > before); // a request went out again with the same file
});

test('422 non-allowlisted: plain copy, code kept as small text', async () => {
  const f = async () => ({ ok: false, status: 422, json: async () => ({ detail: { code: 'INVALID_INPUT', message: 'sha256 is not an owner-approved clips.csv clip' } }) });
  const ctl = createController({ fetch: f });
  await ctl.upload(file());
  const all = strings(render(ctl)).join('|');
  assert.ok(all.includes(NOT_APPROVED));
  assert.doesNotMatch(all, /owner-approved clips\.csv clip/);
  assert.equal(strings(find(render(ctl), (x) => x.type === 'small')[0]).join(''), 'INVALID_INPUT');
  assert.doesNotMatch(NOT_APPROVED, /\u2014/);
});

test('reload mid-interview: idle with the flag shows the reset note; later phases clear it', () => {
  const store = new Map();
  const s = { setItem: (k, v) => store.set(k, v), getItem: (k) => store.get(k) ?? null, removeItem: (k) => store.delete(k) };
  assert.equal(sessionNote(s, 'upload.idle'), false);
  assert.equal(sessionNote(s, 'interview.active'), false);
  assert.equal(sessionNote(s, 'upload.idle'), true); // fresh page, same tab
  assert.match(SESSION_RESET, /reset/);
  assert.equal(sessionNote(s, 'report.owner'), false);
  assert.equal(sessionNote(s, 'upload.idle'), false);
});

test('owner result: divider and heading separate the live fit from the recorded reference', () => {
  const m = { clip_id: 'OWN05', input_label: 'x', status: 'recorded', label: 'l', g: 8.62, u: 1.28, unit: 'm/s^2', measured_label: 'MEASURED', source: 's', caveat: 'c',
    live_fit: { status: 'error', message: 'm' } };
  const layout = { phase: 'report.owner', viewport: {}, stages: [], jobStatus: { label: 'x', surface: null } };
  const tree = renderWorkspace(h, layout, { status: 'empty', error: null }, null, undefined, undefined, undefined, undefined, undefined, undefined, undefined, undefined, { measurement: m });
  const meas = find(tree, (x) => x.props.className === 'ws-measurement')[0];
  const kinds = meas.children.filter(Boolean).map((c) => c.type);
  assert.ok(kinds.indexOf('hr') > 0 && kinds[kinds.indexOf('hr') + 1] === 'h4');
  assert.match(strings(meas).join('|'), /Recorded reference \(not affected by your scale\)/);
});

