// N85: the redesigned lab agent panel, executed with an offline hook harness (no DOM, no paid calls).
import test, { after } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire, registerHooks } from 'node:module';
import { defaultScene } from '../../Build/web/src/lab-editor/scene.mjs';

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
const { default: AgentPanel, CARDS, stepName, sendsOn } = await import(panelUrl);
loader.deregister();

const props = { scene: defaultScene(), onScene() {}, load: false };
function mount(fetchImpl) {
  const h = harness(); Object.assign(globalThis.__N85_REACT__, h.React);
  const calls = []; globalThis.fetch = async (url, init) => { calls.push(url); return fetchImpl(url, init); };
  const all = () => nodes(h.render(AgentPanel, props));
  const btn = (label) => all().find((n) => n.type === 'button' && (n.props['aria-label'] === label || n.children.includes(label)));
  const box = () => all().find((n) => n.type === 'textarea');
  return { calls, all, btn, box };
}
const KEY = (key, shiftKey = false) => ({ key, shiftKey, isComposing: false, preventDefault() {} });

test('empty state cards only fill the composer; nothing is sent', () => {
  const p = mount(() => Response.json({}));
  assert.equal(p.box().props.value, '', 'composer starts empty, with a placeholder');
  assert.ok(p.box().props.placeholder);
  assert.match(strings({ children: p.all() }).join(''), /What should we test\?/);
  assert.deepEqual(CARDS.map((c) => c.title), ['Measure g with a drop', 'Pendulum period', 'Add a ramp', 'Write report']);
  for (const c of CARDS) { p.btn(c.title).props.onClick(); assert.equal(p.box().props.value, c.text); }
  assert.deepEqual(p.calls, []);
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
    ? { reply: 'Done.', model: 'm-1', answered_by: 'fallback', tool_calls: [{ name: 'lab_add_object' }, { name: 'write_report' }], question: { question: 'Next?', options: [{ label: 'Run it', recommended: true }, { label: 'Stop' }] } }
    : url.endsWith('/lab/report') ? { markdown: '# Report' } : { scene: defaultScene() }));
  globalThis.localStorage = { getItem: () => null, setItem() {} };
  p.box().props.onChange({ target: { value: 'Add a ball' } });
  await p.all().find((n) => n.type === 'form').props.onSubmit({ preventDefault() {} });
  const text = strings({ children: p.all() }).join('|');
  for (const s of ['Added object', 'Wrote report', 'Answered by |m-1', 'fallback model', 'Recommended']) assert.ok(text.includes(s), s);
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

