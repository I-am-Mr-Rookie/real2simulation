// N45: execute the actual lab panel and live-workspace hook with offline transports. No DOM or paid calls.
import test, { after } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire, registerHooks } from 'node:module';
import { createLive } from '../../Build/web/src/workspace/live-view.mjs';
import { groupJobs } from '../../Build/web/src/workspace/projects.mjs';
import { writeAgentMode, UPLOAD_QUESTION } from '../../Build/web/src/workspace/live.mjs';
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
const saved = { fetch: globalThis.fetch, localStorage: globalThis.localStorage, XMLHttpRequest: globalThis.XMLHttpRequest };
after(() => { Object.assign(globalThis, saved); delete globalThis.__N45_REACT__; });

// Use the installed Next compiler, exactly as the app does, to exercise JSX without another dependency.
const require = createRequire(new URL('../../Build/web/package.json', import.meta.url));
const swc = require('next/dist/build/swc');
await swc.loadBindings();
const panelUrl = new URL('../../Build/web/src/lab-editor/AgentPanel.jsx', import.meta.url).href;
globalThis.__N45_REACT__ = {};
const loader = registerHooks({
  resolve(s, ctx, next) {
    if (s === 'react' && ctx.parentURL === panelUrl) return { url: 'data:text/javascript,' + encodeURIComponent('const r=globalThis.__N45_REACT__; export default r; export const useState=(...a)=>r.useState(...a), useRef=(...a)=>r.useRef(...a), useEffect=(...a)=>r.useEffect(...a);'), shortCircuit: true };
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
const { default: AgentPanel } = await import(panelUrl);
loader.deregister();

test('F3: lab sends the current account saved tier/contributor and discloses the actual answering model', async () => {
  for (const [mode, tier, contributor] of [['open', 'open', false], ['standard', 'spark', false], ['contributor', 'spark', true], ['sol', 'spark', false], [null, 'spark', false]]) {
    const h = harness(); Object.assign(globalThis.__N45_REACT__, h.React);
    const storage = new Map(); globalThis.localStorage = { getItem: (k) => storage.get(k), setItem: (k, v) => storage.set(k, v) };
    writeAgentMode(globalThis.localStorage, mode, 'own-workspace');
    writeAgentMode(globalThis.localStorage, 'contributor', 'other-account');
    const calls = [];
    globalThis.fetch = async (url, init) => {
      calls.push({ url, body: init.body && JSON.parse(init.body) });
      return Response.json(url.endsWith('/session') ? { userKey: 'own-workspace' } : url.endsWith('/turn')
        ? { reply: 'Physics answer', model: 'actual-provider-model', answered_by: mode === 'open' ? 'fallback' : undefined, tool_calls: [] } : {});
    };
    const props = { scene: defaultScene(), onScene() {}, load: false };
    const tree = h.render(AgentPanel, props);
    await nodes(tree).find((n) => n.type === 'button' && n.children.includes('Write report')).props.onClick();
    const turn = calls.find((c) => c.url.endsWith('/turn')).body;
    assert.equal(turn.tier, tier); assert.equal(turn.contributor, contributor);
    assert.match(turn.text, /^In the virtual lab editor \(SIMULATED\): /);
    assert.deepEqual(turn.history, []);
    const answer = strings(h.render(AgentPanel, props)).join('');
    assert.match(answer, /Answered by actual-provider-model/);
    if (mode === 'open') assert.match(answer, /fallback model/);
    assert.ok(!nodes(tree).some((n) => n.type === 'select'), 'Sol is not selectable');
  }
});

test('F3: failed identity lookup never sends a turn with another account mode', async () => {
  const h = harness(); Object.assign(globalThis.__N45_REACT__, h.React);
  const calls = []; globalThis.fetch = async (url) => { calls.push(url); return Response.json({}, { status: 401 }); };
  const props = { scene: defaultScene(), onScene() {}, load: false };
  await nodes(h.render(AgentPanel, props)).find((n) => n.type === 'button' && n.children.includes('Write report')).props.onClick();
  assert.deepEqual(calls, ['/api/workspace/session']);
  assert.match(strings(h.render(AgentPanel, props)).join(''), /Sign in required/);
});

test('F4: a pending New Room project reaches upload and room creation, even through the previous render handler', async () => {
  const h = harness(), { useLive } = createLive(h.React), uploads = [], files = [{ id: 'legacy', project_id: null }], rooms = [];
  let resolveProject;
  const project = { id: 'chosen-project', mode: 'room', title: 'My room' };
  const roomBodies = [];
  globalThis.fetch = async (url, init = {}) => {
    if (url.endsWith('/projects') && init.method === 'POST') return new Promise((resolve) => { resolveProject = () => resolve(Response.json({ project }, { status: 201 })); });
    if (url.endsWith('/projects')) return Response.json({ projects: [project] });
    if (url.endsWith('/files')) return Response.json({ files });
    if (url.endsWith('/rooms') && init.method === 'POST') { const body = JSON.parse(init.body); roomBodies.push(body); rooms.push({ id: 'room-job', project_id: body.project_id }); return Response.json({ job: { job_id: 'room-job' } }, { status: 202 }); }
    return Response.json(url.endsWith('/rooms') ? { rooms } : url.includes('/rooms/') ? { job: { state: 'done' } } : { jobs: [] });
  };
  globalThis.XMLHttpRequest = class {
    upload = {};
    open() {}
    send(form) {
      uploads.push(form); const file = { id: 'uploaded', project_id: form.get('project_id'), media_type: 'video/mp4' };
      files.push(file); this.status = 201; this.responseText = JSON.stringify({ file }); this.onload();
    }
  };
  const old = h.render(useLive, false, null, 'own-workspace');
  old.newProject();
  const creating = old.answer({ id: 1, local: true, question: UPLOAD_QUESTION }, 1, '');
  const uploading = old.upload(new File(['synthetic'], 'room.mp4'));
  await Promise.resolve(); assert.equal(uploads.length, 0, 'wait for the chosen project before sending the file');
  resolveProject(); await creating; await uploading;
  assert.equal(uploads[0].get('project_id'), project.id);
  await h.render(useLive, false, null, 'own-workspace').buildRoom(files.at(-1));
  assert.deepEqual(roomBodies, [{ file_id: 'uploaded', project_id: project.id }]);
  assert.deepEqual(groupJobs([project], [], rooms)[0].rooms.map((r) => r.id), ['room-job']);
  assert.equal(files[0].project_id, null, 'existing unassigned files are not changed');
  old.newProject(); await old.upload(new File(['synthetic'], 'unassigned.mp4'));
  assert.equal(uploads[1].get('project_id'), null, 'New project clears the previous selection');
});

test('F4: failed or malformed project creation does not silently upload outside the chosen project', async () => {
  for (const status of [500, 200]) {
    const h = harness(), { useLive } = createLive(h.React);
    globalThis.fetch = async () => Response.json({}, { status });
    globalThis.XMLHttpRequest = class { constructor() { assert.fail('must not upload after project failure'); } };
    const old = h.render(useLive, false, null, 'own-workspace');
    await old.answer({ id: 1, local: true, question: UPLOAD_QUESTION }, 1, '');
    await old.upload(new File(['synthetic'], 'room.mp4'));
    assert.match(h.render(useLive, false, null, 'own-workspace').up.error, /Could not create the project/);
  }
});
