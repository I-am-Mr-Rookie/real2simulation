import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createLive } from '../../Build/web/src/workspace/live-view.mjs';

const nodes = (n) => n && typeof n === 'object' ? [n, ...n.children.flatMap(nodes)] : [];
const text = (n) => n && typeof n === 'object' ? n.children.map(text).join(' ') : String(n ?? '');

test('each own room gets a targeted confirmation; sample has no delete; Cancel never deletes', async () => {
  let values = [], cursor = 0;
  const React = {
    createElement: (type, props, ...children) => ({ type, props: props ?? {}, children: children.flat(Infinity) }),
    useState: (initial) => {
      const i = cursor++;
      if (!(i in values)) values[i] = typeof initial === 'function' ? initial() : initial;
      return [values[i], (v) => { values[i] = typeof v === 'function' ? v(values[i]) : v; }];
    }, useEffect() {}, useRef: (v) => ({ current: v }),
  };
  const { Centre } = createLive(React), deleted = [];
  const rooms = ['a', 'b', 'sample'].map((id) => ({ id, project_id: 'p', state: 'done', sample: id === 'sample' }));
  const L = { mode: 'standard', tracked: {}, files: { items: [] }, jobs: { projects: { items: [{ id: 'p', title: 'Own rooms', mode: 'room' }] },
    experiments: { items: [] }, rooms: { items: rooms } }, deleteRoom: async (id) => deleted.push(id) };
  const grid = nodes(Centre({ L })).find((n) => n.type?.name === 'ProjectsGrid');
  const card = nodes(grid.type(grid.props)).find((n) => n.type?.name === 'ProjectCard');
  values = [];
  const render = () => { cursor = 0; return nodes(card.type(card.props)); };
  const actions = () => render().find((n) => n.type?.name === 'Menu').props.items.filter(Boolean);
  assert.deepEqual(actions().filter((a) => a.label.startsWith('Delete room')).map((a) => a.label), ['Delete room a', 'Delete room b']);
  actions().find((a) => a.label === 'Delete room a').onClick();
  let tree = render();
  const css = readFileSync(new URL('../../Build/web/src/workspace/workspace.css', import.meta.url), 'utf8');
  assert.match(css, /\.lv-room-delete \[data-danger\]\s*\{[^}]*color:\s*var\(--r2s-danger[^}]*background:\s*var\(--r2s-surface/);
  assert.match(text(tree.find((n) => n.props.role === 'alertdialog')), /Delete this room\? Its 3D files and lab edits are removed\. This cannot be undone\./);
  assert.deepEqual(deleted, []);
  let focused = 0;
  const event = { currentTarget: { closest: () => ({ querySelector: () => ({ focus: () => focused++ }) }) } };
  tree.find((n) => n.type === 'button' && text(n) === 'Cancel').props.onClick(event);
  assert.equal(focused, 1);
  assert.ok(!render().some((n) => n.props.role === 'alertdialog'));
  assert.deepEqual(deleted, []);
  actions().find((a) => a.label === 'Delete room b').onClick();
  tree = render();
  await tree.find((n) => n.type === 'button' && text(n) === 'Delete room').props.onClick();
  assert.deepEqual(deleted, ['b']);
  assert.ok(!render().some((n) => n.props.role === 'alertdialog'));
});
