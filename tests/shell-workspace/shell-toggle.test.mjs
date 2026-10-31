// S15ab: Q21 workspace shell toggles. Pure render with a tiny h; SSR of the real PrivateWorkspace for ids/labels.
import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { renderShell, toolsOf, shellKey, initialLeft, NAV, SECTIONS } from '../../Build/web/src/shell/workspace-shell.mjs';
import PrivateWorkspace from '../../Build/web/src/shell/PrivateWorkspace.mjs';

const require = createRequire(new URL('../../Build/web/package.json', import.meta.url));
const React = require('react');
const { renderToStaticMarkup } = require('react-dom/server');
const h = (type, props, ...children) => ({ type, props: props ?? {}, children: children.flat().filter((c) => c != null && c !== false) });
const all = (n, out = []) => { if (n && typeof n === 'object') { out.push(n); n.children.forEach((c) => all(c, out)); } return out; };
const textOf = (n) => (typeof n === 'string' ? n : n && typeof n === 'object' ? n.children.map(textOf).join('') : '');
const find = (tree, pred) => all(tree).filter(pred);
const live = { live: true, phase: 'upload.idle', owner: false, jobId: null, uploadStatus: 'Choose a clip', hasReport: false };

test('left sidebar: expanded and collapsed both keep every nav link with its accessible name; toggle reports aria-expanded', () => {
  for (const left of [true, false]) {
    const tree = renderShell(h, { title: 'T', rail: { pane: 'navigate', open: left, preview: null }, right: false, tools: [] });
    assert.equal(tree.props['data-left'], left ? 'expanded' : 'collapsed');
    const [btn] = find(tree, (n) => n.props['data-toggle'] === 'left');
    assert.equal(btn.props['aria-expanded'], left);
    assert.equal(btn.props['aria-controls'], 'r2s-left');
    assert.equal(btn.props['aria-keyshortcuts'], 'Control+B');
    const links = find(tree, (n) => n.type === 'a');
    assert.deepEqual(links.map((a) => textOf(a)), [...NAV, ...SECTIONS].map((x) => x.label)); // label text stays (visually hidden when collapsed)
    assert.ok(links.every((a) => a.props.title));
  }
  assert.equal(renderShell(h, { title: 'T', left: null, right: false, tools: [] }).props['data-left'], 'auto');
});

test('right panel: rightmost header button toggles it, aria-expanded/hidden agree, heading is focusable', () => {
  for (const right of [true, false]) {
    const tree = renderShell(h, { title: 'T', left: true, right, tools: toolsOf(live) });
    const [header] = find(tree, (n) => n.type === 'header');
    const last = header.children.at(-1);
    assert.equal(last.props['data-toggle'], 'right');
    assert.equal(last.props['aria-expanded'], right);
    assert.equal(last.props['aria-controls'], 'r2s-right');
    const [panel] = find(tree, (n) => n.props.id === 'r2s-right');
    assert.equal(panel.props.hidden, !right);
    assert.equal(panel.props['aria-labelledby'], 'r2s-right-h');
    assert.equal(find(panel, (n) => n.props.id === 'r2s-right-h')[0].props.tabIndex, -1);
  }
});

test('tools: only real backend-driven features, none when the API is not connected', () => {
  assert.deepEqual(toolsOf({ ...live, live: false }), []);
  const empty = renderShell(h, { title: 'T', left: true, right: true, tools: [] });
  assert.equal(find(empty, (n) => n.props['data-tool']).length, 0);
  assert.match(textOf(empty), /No tools: the private workspace service is not connected/);
  const tools = toolsOf(live);
  assert.deepEqual(tools.map((t) => t.id), ['agent', 'clips', 'runs', 'report']);
  assert.deepEqual(new Set(tools.map((t) => t.target)), new Set(['ws-panel', 'ws-upload-file', 'ws-job']));
  const tree = renderShell(h, { title: 'T', left: true, right: true, tools });
  assert.deepEqual(find(tree, (n) => n.props['data-tool']).map((n) => n.props['aria-keyshortcuts']), ['Alt+1', 'Alt+2', 'Alt+3', 'Alt+4']);
  assert.match(toolsOf({ ...live, phase: 'interview.active', owner: true }).find((t) => t.id === 'agent').status, /Owner clip: no scene/);
  assert.equal(toolsOf({ ...live, jobId: 'j1', phase: 'run.done' })[2].status, 'Job j1: Run finished');
});

test('keys and persisted state', () => {
  const tools = toolsOf(live);
  assert.equal(shellKey({ key: 'b', ctrlKey: true }), 'left');
  assert.equal(shellKey({ key: 'B', metaKey: true }), 'left');
  assert.equal(shellKey({ key: 'j', ctrlKey: true }), 'right');
  assert.equal(shellKey({ key: 'b', ctrlKey: true, shiftKey: true }), null);
  assert.equal(shellKey({ key: '¡', code: 'Digit1', altKey: true }, tools), 'tool:agent');
  assert.equal(shellKey({ key: '4', code: 'Digit4', altKey: true }, []), null); // no tool, no shortcut
  assert.equal(shellKey({ key: 'Escape' }), 'escape');
  assert.equal(shellKey({ key: 'b' }), null);
  assert.equal(initialLeft(null, false), true);
  assert.equal(initialLeft('collapsed', false), false);
  assert.equal(initialLeft('expanded', true), false); // narrow: drawer starts closed
});

test('SSR: the real workspace renders inside the shell with jump targets and honest notices', () => {
  const html = renderToStaticMarkup(React.createElement(PrivateWorkspace, { scene: { title: 'Scene X', notice: 'FIXTURE notice' } }));
  for (const s of ['class="r2s-shell"', 'data-left="auto"', 'id="ws-viewport"', 'id="ws-panel"', 'id="ws-job"', '<h1>Scene X</h1>', 'FIXTURE notice', 'data-slot="viewport"'])
    assert.ok(html.includes(s), s);
  assert.ok(/id="r2s-right"[^>]*hidden/.test(html));
  assert.match(html, /No tools: the private workspace service is not connected/);
});
