// S15ae: activity-bar rail (Q21 section 6). Pure reducer rules + render attributes; timers/pointer wiring live in PrivateWorkspace.
import test from 'node:test';
import assert from 'node:assert/strict';
import { railReduce, initialRail, shownPane, renderShell, PANES, HOVER_OPEN_MS, HOVER_CLOSE_MS, NAV, SECTIONS } from '../../Build/web/src/shell/workspace-shell.mjs';

const h = (type, props, ...children) => ({ type, props: props ?? {}, children: children.flat().filter((c) => c != null && c !== false) });
const all = (n, out = []) => { if (n && typeof n === 'object') { out.push(n); n.children.forEach((c) => all(c, out)); } return out; };
const find = (tree, pred) => all(tree).filter(pred);
const run = (s, ...evs) => evs.reduce(railReduce, s);
const S = (pane, open, preview = null) => ({ pane, open, preview });

test('panes are real page content only: Go to = NAV routes, This project = SECTIONS anchors', () => {
  assert.deepEqual(PANES.map((p) => p.id), ['navigate', 'project']);
  assert.equal(PANES[0].items, NAV);
  assert.equal(PANES[1].items, SECTIONS);
  assert.deepEqual([HOVER_OPEN_MS, HOVER_CLOSE_MS], [150, 250]);
});

test('toggle shows/hides the CURRENT pane; rail state keeps the current pane', () => {
  assert.deepEqual(run(S('project', true), { type: 'toggle' }), S('project', false));
  assert.deepEqual(run(S('project', false), { type: 'toggle' }), S('project', true));
  assert.deepEqual(run(S('project', false, 'navigate'), { type: 'toggle' }), S('project', true)); // toggle drops a preview
});

test('icon click: current open -> close; another -> current + pinned open; current while collapsed -> open', () => {
  assert.deepEqual(run(S('navigate', true), { type: 'iconClick', id: 'navigate' }), S('navigate', false));
  assert.deepEqual(run(S('navigate', true), { type: 'iconClick', id: 'project' }), S('project', true));
  assert.deepEqual(run(S('navigate', false), { type: 'iconClick', id: 'navigate' }), S('navigate', true));
  assert.deepEqual(run(S('navigate', false), { type: 'iconClick', id: 'project' }), S('project', true));
});

test('hover preview: any pane not open (incl. current while collapsed) opens temporarily; leave closes; click/pin pins', () => {
  const open = S('navigate', true);
  assert.equal(railReduce(open, { type: 'hoverEnter', id: 'navigate' }), open); // already open: nothing
  assert.deepEqual(run(open, { type: 'hoverEnter', id: 'project' }), S('navigate', true, 'project'));
  assert.deepEqual(run(S('navigate', false), { type: 'hoverEnter', id: 'navigate' }), S('navigate', false, 'navigate')); // owner Home case
  assert.deepEqual(run(S('navigate', false), { type: 'hoverEnter', id: 'project' }, { type: 'hoverLeave' }), S('navigate', false));
  assert.deepEqual(run(S('navigate', false), { type: 'hoverEnter', id: 'project' }, { type: 'iconClick', id: 'project' }), S('project', true));
  assert.deepEqual(run(S('navigate', false), { type: 'hoverEnter', id: 'navigate' }, { type: 'iconClick', id: 'navigate' }), S('navigate', true)); // click while previewing pins
  assert.deepEqual(run(S('navigate', true), { type: 'hoverEnter', id: 'project' }, { type: 'pin' }), S('project', true));
  assert.deepEqual(run(S('navigate', true, 'project'), { type: 'hoverEnter', id: 'navigate' }), S('navigate', true)); // back on the open icon
  const st = S('navigate', false);
  for (const type of ['hoverLeave', 'escape', 'pin']) assert.equal(railReduce(st, { type }), st); // no-ops keep identity
});

test('escape closes only the temporary pane', () => {
  assert.deepEqual(run(S('navigate', true, 'project'), { type: 'escape' }), S('navigate', true));
  assert.equal(shownPane(S('navigate', true, 'project')), 'project');
  assert.equal(shownPane(S('navigate', false)), null);
});

test('persisted state: stored pane validated; narrow starts closed; default navigate open', () => {
  assert.deepEqual(initialRail(null, null, false), S('navigate', true));
  assert.deepEqual(initialRail('collapsed', 'project', false), S('project', false));
  assert.deepEqual(initialRail('expanded', 'evil', false), S('navigate', true));
  assert.deepEqual(initialRail('expanded', 'project', true), S('project', false));
});

test('render: rail always present; current icon aria-current open/collapsed/preview; panes aria-labelled; temporary has pin', () => {
  for (const rail of [S('project', true), S('project', false), S('project', false, 'navigate'), S('project', false, 'project')]) {
    const tree = renderShell(h, { title: 'T', rail, right: false, tools: [] });
    const btns = find(tree, (n) => n.props['data-pane']);
    assert.deepEqual(btns.map((b) => b.props['aria-current']), [undefined, 'true']);
    assert.ok(btns.every((b) => b.type === 'button' && b.props['aria-label'] && b.props['aria-controls'] === 'r2s-pane-' + b.props['data-pane']));
    const panes = find(tree, (n) => n.props.className === 'r2s-pane');
    assert.ok(panes.every((p) => p.props.role === 'region' && p.props['aria-label']));
    assert.deepEqual(panes.filter((p) => !p.props.hidden).map((p) => p.props.id), shownPane(rail) ? ['r2s-pane-' + shownPane(rail)] : []);
    assert.equal(tree.props['data-left'], rail.open ? 'expanded' : 'collapsed');
    assert.deepEqual(panes.filter((p) => p.props['data-mode'] === 'temporary').map((p) => p.props.id), rail.preview ? ['r2s-pane-' + rail.preview] : []);
    assert.equal(find(tree, (n) => n.props.className === 'r2s-pin').length, rail.preview ? 1 : 0);
    assert.equal(find(tree, (n) => n.props.tabIndex >= 0 || n.props.autoFocus).length, 0); // nothing steals focus
  }
});

test('render events: click/hover handlers route to the reducer events', () => {
  const got = [];
  const tree = renderShell(h, { title: 'T', rail: S('navigate', false), right: false, tools: [] },
    { rail: (e) => got.push(e), hover: (id) => got.push({ hover: id }), unhover: () => got.push('leave') });
  const [b] = find(tree, (n) => n.props['data-pane'] === 'project');
  b.props.onClick(); b.props.onPointerEnter({ pointerType: 'mouse' }); b.props.onPointerLeave();
  assert.deepEqual(got, [{ type: 'iconClick', id: 'project' }, { hover: 'project' }, 'leave']);
});
