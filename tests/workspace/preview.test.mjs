import test from 'node:test';
import assert from 'node:assert/strict';
import { createLive } from '../../Build/web/src/workspace/live-view.mjs';

const React = {
  createElement: (type, props, ...children) => ({ type, props: props ?? {}, children: children.flat(Infinity) }),
  useState: (v) => [typeof v === 'function' ? v() : v, () => {}], useEffect() {}, useRef: (v) => ({ current: v }),
};
const nodes = (n) => n && typeof n === 'object' ? [n, ...n.children.flatMap(nodes)] : [];
const { Centre } = createLive(React);
function card({ snapshot, source = 'video', preview = true, kind = 'frame', project = {},
  experiments = [{ id: 'e', project_id: 'p', file_id: 'video', status: 'done' }], rooms = [],
  files = [{ id: 'video', project_id: 'p', media_type: 'video/mp4' }], ...actions } = {}) {
  const L = { mode: 'standard', tracked: {}, files: { items: files },
    jobs: { projects: { items: [{ id: 'p', mode: 'experiment', title: 'Public test', snapshot_url: snapshot,
      track_preview: preview ? { kind, file_id: source, width: 320, height: 180, points: [[10, 20], [30, 40]], label: 'MEASURED pixels' } : null, ...project }] },
    experiments: { items: experiments }, rooms: { items: rooms } }, ...actions };
  const grid = nodes(Centre({ L })).find((n) => n.type?.name === 'ProjectsGrid');
  const projectCard = nodes(grid.type(grid.props)).find((n) => n.type?.name === 'ProjectCard');
  return nodes(projectCard.type(projectCard.props));
}
test('automatic preview uses stored pixel path only on its source video and preserves snapshots', () => {
  const path = card().find((n) => n.type === 'svg' && n.props.className === 'lv-track-preview');
  assert.equal(path.props.viewBox, '0 0 320 180');
  assert.equal(path.props['aria-label'], 'MEASURED pixels');
  assert.equal(path.children[0].props.points, '10,20 30,40');
  for (const input of [{ snapshot: '/saved.jpg' }, { source: 'other-video' }, { preview: false }]) {
    assert.equal(card(input).some((n) => n.props.className === 'lv-track-preview'), false);
  }
  const plot = card({ source: null, kind: 'plot' });
  assert.ok(plot.some((n) => n.props['data-plot'] === true));
  assert.equal(plot.find((n) => n.props['data-plot']).props.preserveAspectRatio, 'xMidYMid meet');
  assert.ok(plot.some((n) => n.props.className === 'lv-path-label'));
  assert.ok(!plot.some((n) => n.type?.name === 'Thumb'));
});

test('mixed sample card opens its room and offers its experiment separately', (t) => {
  const assigned = [], tracked = [];
  const original = Object.getOwnPropertyDescriptor(globalThis, 'location');
  Object.defineProperty(globalThis, 'location', { configurable: true, value: { assign: (href) => assigned.push(href) } });
  t.after(() => original ? Object.defineProperty(globalThis, 'location', original) : delete globalThis.location);
  const tree = card({ project: { mode: 'room', sample: true }, snapshot: '/classroom.jpg',
    rooms: [{ id: 'classroom', project_id: 'p', status: 'done', updated_at: '2026-11-02T09:00:00Z' }],
    experiments: [{ id: 'apple', project_id: 'p', status: 'done', created: '2026-11-02T10:00:00Z' }],
    track: (...args) => tracked.push(args) });
  tree.find((n) => n.props.className === 'lv-pcard-hit').props.onClick();
  assert.deepEqual(assigned, ['/lab?editor=1&room=classroom']);
  assert.deepEqual(tracked, []);
  const actions = tree.find((n) => n.type?.name === 'Menu').props.items.filter(Boolean);
  actions.find((a) => a.label === 'Open experiment').onClick();
  assert.deepEqual(tracked, [['experiment', 'apple']]);
  actions.find((a) => a.label === 'Open').onClick();
  assert.equal(assigned.length, 2);
});

test('snapshot-only saved lab opens its project editor from card and menu', (t) => {
  const assigned = [];
  const original = Object.getOwnPropertyDescriptor(globalThis, 'location');
  Object.defineProperty(globalThis, 'location', { configurable: true, value: { assign: (href) => assigned.push(href) } });
  t.after(() => original ? Object.defineProperty(globalThis, 'location', original) : delete globalThis.location);
  const tree = card({ snapshot: '/saved.jpg', experiments: [], rooms: [], files: [], openAgent: () => assert.fail('must not open agent') });
  tree.find((n) => n.props.className === 'lv-pcard-hit').props.onClick();
  tree.find((n) => n.type?.name === 'Menu').props.items.find((a) => a.label === 'Open').onClick();
  assert.deepEqual(assigned, ['/lab?editor=1&project=p', '/lab?editor=1&project=p']);
});

test('detached experiment source supplies the video and only its matching track', () => {
  const files = [{ id: 'unrelated', project_id: 'p', media_type: 'video/mp4' }, { id: 'video', project_id: null, media_type: 'video/mp4' }];
  const tree = card({ files });
  assert.equal(tree.find((n) => n.type?.name === 'Thumb').props.f.id, 'video');
  assert.ok(tree.some((n) => n.props.className === 'lv-track-preview'));
  const missing = card({ files: files.slice(0, 1) });
  assert.equal(missing.find((n) => n.type?.name === 'Thumb').props.f, undefined);
  assert.ok(!missing.some((n) => n.props.className === 'lv-track-preview'));
});

test('without a stored track, room and experiment previews still use their exact source file', () => {
  const files = [{ id: 'unrelated', project_id: 'p', media_type: 'video/mp4' }, { id: 'video', project_id: null, media_type: 'video/mp4' }];
  for (const jobs of [{}, { project: { mode: 'room' }, experiments: [], rooms: [{ id: 'room', project_id: 'p', file_id: 'video', status: 'done' }] }]) {
    assert.equal(card({ files, preview: false, ...jobs }).find((n) => n.type?.name === 'Thumb').props.f.id, 'video');
    assert.equal(card({ files: files.slice(0, 1), preview: false, ...jobs }).find((n) => n.type?.name === 'Thumb').props.f, undefined);
  }
});
