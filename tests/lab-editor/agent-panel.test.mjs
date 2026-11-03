// N85: the redesigned lab agent panel, executed with an offline hook harness (no DOM, no paid calls).
import test, { after } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire, registerHooks } from 'node:module';
import { defaultScene, validateScene } from '../../Build/web/src/lab-editor/scene.mjs';
import { emptyHistory, record, undo, redo, tidyView } from '../../Build/web/src/lab-editor/history.mjs';

function harness() {
  const cells = []; let cursor = 0;
  const React = {
    createElement: (type, props, ...children) => ({ type, props: props ?? {}, children: children.flat(Infinity) }),
    useState(initial) { const i = cursor++; if (!(i in cells)) cells[i] = initial; return [cells[i], (v) => { cells[i] = typeof v === 'function' ? v(cells[i]) : v; }]; },
    useRef(initial) { const i = cursor++; return cells[i] ??= { current: initial }; },
    useEffect() {}, useCallback: (f) => f,
  };
  return { React, render: (fn, ...args) => { cursor = 0; return fn(...args); } };
}
const nodes = (n) => n && typeof n === 'object' ? [n, ...n.children.flatMap(nodes)] : [];
const strings = (n) => typeof n === 'string' ? [n] : n?.children?.flatMap(strings) ?? [];
const keys = ['fetch', 'MediaRecorder', 'AudioContext', 'OfflineAudioContext'];
const saved = Object.fromEntries(keys.map((k) => [k, globalThis[k]])), nav = Object.getOwnPropertyDescriptor(globalThis, 'navigator');
after(() => { Object.assign(globalThis, saved); if (nav) Object.defineProperty(globalThis, 'navigator', nav); delete globalThis.__N85_REACT__; });

const require = createRequire(new URL('../../Build/web/package.json', import.meta.url));
const swc = require('next/dist/build/swc');
await swc.loadBindings();
const panelUrl = new URL('../../Build/web/src/lab-editor/AgentPanel.jsx', import.meta.url).href;
globalThis.__N85_REACT__ = {};
const loader = registerHooks({
  resolve(s, ctx, next) {
    if (s === 'react' && ctx.parentURL === panelUrl) return { url: 'data:text/javascript,' + encodeURIComponent('const r=globalThis.__N85_REACT__; export default r; export const useState=(...a)=>r.useState(...a), useRef=(...a)=>r.useRef(...a), useEffect=(...a)=>r.useEffect(...a);'), shortCircuit: true };
    return next(s, ctx);
  },
  load(url, ctx, next) {
    if (url !== panelUrl) return next(url, ctx);
    const source = swc.transformSync("import React from 'react';\n" + readFileSync(new URL(url), 'utf8'), {
      filename: 'AgentPanel.jsx', jsc: { parser: { syntax: 'ecmascript', jsx: true }, transform: { react: { runtime: 'classic' } } }, module: { type: 'es6' },
    }).code;
    return { format: 'module', source, shortCircuit: true };
  },
});
const { default: AgentPanel, CARDS, CONTEXT, stepName, sendsOn } = await import(panelUrl);
loader.deregister();

const props = { scene: defaultScene(), onScene() {}, load: false };
function mount(fetchImpl, extra = {}) {
  const h = harness(); Object.assign(globalThis.__N85_REACT__, h.React);
  const calls = []; globalThis.fetch = async (url, init) => { calls.push(url); return fetchImpl(url, init); };
  const all = () => nodes(h.render(AgentPanel, { ...props, ...extra }));
  const btn = (label) => all().find((n) => n.type === 'button' && (n.props['aria-label'] === label || n.children.includes(label)));
  const box = () => all().find((n) => n.type === 'textarea');
  return { calls, all, btn, box };
}
const KEY = (key, shiftKey = false) => ({ key, shiftKey, isComposing: false, preventDefault() {} });

test('empty state cards only fill the composer; cleanup card and model hint are absent', () => {
  const p = mount(() => Response.json({}));
  assert.equal(p.box().props.value, '', 'composer starts empty, with a placeholder');
  assert.ok(p.box().props.placeholder);
  assert.match(strings({ children: p.all() }).join(''), /What should we test\?/);
  assert.deepEqual(CARDS.map((c) => c.title), ['Measure g with a drop', 'Pendulum period', 'Add a ramp', 'Write report']);
  assert.doesNotMatch(strings({ children: p.all() }).join('|'), /Clean up the lab|Best with Muse Wonder/);
  for (const c of CARDS) { p.btn(c.title).props.onClick(); assert.equal(p.box().props.value, c.text); }
  assert.deepEqual(p.calls, []);
});

test('a typed batch-edit turn still marks one tidied scene; chips only fill the composer', async () => {
  const seen = []; let body;
  globalThis.localStorage = { getItem: () => null, setItem() {} };
  const p = mount((url, init) => {
    if (url.endsWith('/turn')) body = JSON.parse(init.body);
    return Response.json(url.endsWith('/session') ? { userKey: 'u' } : url.endsWith('/turn') ? { reply: 'Tidied.', model: 'm-1', tool_calls: [{ name: 'lab_update_objects' }] } : { scene: defaultScene() });
  }, { onScene: (s, msg, tidied) => seen.push([msg, tidied]) });
  p.box().props.onChange({ target: { value: 'Move both balls to the floor' } });
  await p.all().find((n) => n.type === 'form').props.onSubmit({ preventDefault() {} });
  assert.equal(body.text, CONTEXT + 'Move both balls to the floor', 'only the typed request is sent');
  assert.deepEqual(seen, [['Tidied by agent · SIMULATED. Undo or Before shows the old layout.', true]], 'one scene update for the whole batch');
  const text = strings({ children: p.all() }).join('|');
  assert.ok(text.includes('Updated objects') && text.includes('Move both balls to the floor'));
  assert.doesNotMatch(text, /Clean up the lab|Best with Muse Wonder/);
  assert.ok(text.includes('Answered by |m-1') && !text.includes('fallback model'), 'no fallback: the requested model answered');
  assert.equal(p.box().props.value, '', 'sending clears the composer');
  assert.equal(body.history.length, 0);
  const chips = p.all().find((n) => n.props.className === 'la-chips');
  assert.deepEqual(strings(chips), CARDS.map((c) => c.title));
  const sent = p.calls.length;
  for (const c of CARDS) { p.btn(c.title).props.onClick(); assert.equal(p.box().props.value, c.text); }
  assert.equal(p.calls.length, sent, 'chips never send a turn');
  await p.all().find((n) => n.type === 'form').props.onSubmit({ preventDefault() {} });
  assert.deepEqual(body.history, [{ role: 'user', content: 'Move both balls to the floor' }, { role: 'assistant', content: 'Tidied.' }]);
  delete globalThis.localStorage;
});

test('a batch-edit turn is one Undo step; Before/After switches without losing either scene', () => {
  const before = validateScene({ ...defaultScene(), objects: [{ id: 'a', kind: 'block', position: [0, 2, 0] }, { id: 'b', kind: 'ball', position: [1, -1, 0] }] });
  const after = { ...before, objects: before.objects.map((o) => ({ ...o, position: [o.position[0], 0.1, 0] })) };
  const tidy = { before, after };
  const h = record(emptyHistory(), before); // the editor records one entry per scene change; the agent turn sets one scene
  assert.equal(tidyView(h, after, tidy), 'after');
  const u = undo(h, after);
  assert.equal(u.scene, before, 'one Undo restores every object'); assert.equal(u.history.past.length, 0);
  assert.equal(tidyView(u.history, u.scene, tidy), 'before');
  const r = redo(u.history, u.scene);
  assert.equal(r.scene, after); assert.equal(tidyView(r.history, r.scene, tidy), 'after');
  const edited = { ...after };
  assert.equal(tidyView(record(r.history, after), edited, tidy), null, 'toggle hides after any other edit');
  assert.equal(tidyView(h, after, null), null);
});

test('Enter sends, Shift+Enter keeps a newline', async () => {
  const p = mount(() => Response.json({}, { status: 401 }));
  p.box().props.onChange({ target: { value: 'Drop a ball' } });
  let prevented = false;
  p.box().props.onKeyDown({ ...KEY('Enter', true), preventDefault() { prevented = true; } });
  assert.equal(prevented, false); assert.deepEqual(p.calls, []);
  assert.equal(sendsOn(KEY('Enter')), true); assert.equal(sendsOn({ ...KEY('Enter'), isComposing: true }), false);
  await p.box().props.onKeyDown(KEY('Enter'));
  await new Promise((r) => setTimeout(r, 0));
  assert.deepEqual(p.calls, ['/api/workspace/session']);
  assert.match(strings({ children: p.all() }).join(''), /Sign in required/);
});

function micMocks() {
  const rec = {};
  Object.defineProperty(globalThis, 'navigator', { configurable: true, value: { mediaDevices: { getUserMedia: async () => ({ getTracks: () => [{ stop() {} }] }) } } });
  globalThis.MediaRecorder = class {
    state = 'inactive';
    constructor() { rec.last = this; }
    start() { this.state = 'recording'; }
    stop() { this.state = 'inactive'; this.ondataavailable({ data: new Blob(['x']) }); this.done = this.onstop(); }
  };
  globalThis.AudioContext = class { async decodeAudioData() { return { duration: .01 }; } close() {} };
  globalThis.OfflineAudioContext = class { destination = {}; createBufferSource() { return { connect() {}, start() {} }; } async startRendering() { return { getChannelData: () => new Float32Array(160) }; } };
  return rec;
}

test('mic stop transcribes into the composer for editing and never sends', async () => {
  const rec = micMocks(), p = mount((url) => Response.json(url.endsWith('/transcribe') ? { text: 'pendulum please' } : {}));
  p.box().props.onChange({ target: { value: 'Try a' } });
  await p.btn('Voice input').props.onClick();
  assert.equal(p.box(), undefined, 'recording row replaces the text field');
  assert.ok(p.btn('Cancel recording') && p.all().some((n) => n.props.className === 'la-level'));
  p.btn('Stop recording').props.onClick();
  await rec.last.done;
  assert.equal(p.box().props.value, 'Try a pendulum please');
  assert.deepEqual(p.calls, ['/api/workspace/agent/transcribe']);
});

test('mic cancel discards the recording without a transcription call', async () => {
  const rec = micMocks(), p = mount(() => Response.json({ text: 'should not appear' }));
  await p.btn('Voice input').props.onClick();
  p.btn('Cancel recording').props.onClick();
  await rec.last.done;
  assert.equal(p.box().props.value, '');
  assert.ok(p.btn('Voice input'));
  assert.deepEqual(p.calls, []);
});

test('agent replies show readable steps, model line, fallback tag and a collapsed report card', async () => {
  assert.equal(stepName('lab_add_object'), 'Added object'); assert.equal(stepName('lab_run'), 'Ran simulation');
  assert.equal(stepName('fit_equation'), 'Fitted'); assert.equal(stepName('start_experiment_track'), 'Start experiment track');
  const p = mount((url) => Response.json(url.endsWith('/session') ? { userKey: 'u' } : url.endsWith('/turn')
    ? { reply: 'Done.', model: 'm-1', answered_by: 'fb-9', tool_calls: [{ name: 'lab_add_object' }, { name: 'write_report' }], question: { question: 'Next?', options: [{ label: 'Run it', recommended: true }, { label: 'Stop' }] } }
    : url.endsWith('/lab/report') ? { markdown: '# Report' } : { scene: defaultScene() }));
  globalThis.localStorage = { getItem: () => null, setItem() {} };
  p.box().props.onChange({ target: { value: 'Add a ball' } });
  await p.all().find((n) => n.type === 'form').props.onSubmit({ preventDefault() {} });
  const text = strings({ children: p.all() }).join('|');
  for (const s of ['Added object', 'Wrote report', 'Answered by |fb-9', 'fallback model', 'Recommended']) assert.ok(text.includes(s), s);
  assert.ok(!text.includes('m-1'), 'a fallback reply never names the requested model as its author');
  assert.doesNotMatch(text, /tools:/);
  // the report card is its own component: render it right after the panel so its hook cell index is stable
  const card = () => { const el = p.all().find((n) => n.props?.md); assert.equal(el.props.md, '# Report'); return nodes(el.type(el.props)); };
  assert.match(strings({ children: card() }).join('|'), /Lab report\|SIMULATED/);
  assert.ok(!card().some((n) => n.type === 'pre'), 'report starts collapsed');
  card().find((n) => n.children.includes('Open')).props.onClick();
  assert.ok(card().some((n) => n.type === 'pre'));
  assert.ok(card().some((n) => n.type === 'button' && n.children.includes('Download (.md)')));
  assert.ok(p.all().some((n) => n.props.className === 'la-chips'), 'suggestions move to a chip row after the first message');
  p.btn('New chat').props.onClick();
  assert.match(strings({ children: p.all() }).join(''), /What should we test\?/);
  delete globalThis.localStorage;
});

test('no em dashes in the panel text', () => {
  assert.doesNotMatch(readFileSync(new URL(panelUrl), 'utf8'), /\u2014/);
});

