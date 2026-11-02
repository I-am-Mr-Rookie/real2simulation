import test from 'node:test';
import assert from 'node:assert/strict';
import { createLive } from '../../Build/web/src/workspace/live-view.mjs';

const React = {
  createElement: (type, props, ...children) => ({ type, props: props ?? {}, children: children.flat(Infinity) }),
  useState: (v) => [typeof v === 'function' ? v() : v, () => {}], useEffect() {}, useRef: (v) => ({ current: v }),
};
const nodes = (n) => n && typeof n === 'object' ? [n, ...n.children.flatMap(nodes)] : [];
const { Centre } = createLive(React);
function card({ snapshot, source = 'video', preview = true, kind = 'frame' } = {}) {
  const L = { mode: 'standard', tracked: {}, files: { items: [{ id: 'video', project_id: 'p', media_type: 'video/mp4' }] },
    jobs: { projects: { items: [{ id: 'p', mode: 'experiment', title: 'Public test', snapshot_url: snapshot,
      track_preview: preview ? { kind, file_id: source, width: 320, height: 180, points: [[10, 20], [30, 40]], label: 'MEASURED pixels' } : null }] },
    experiments: { items: [{ id: 'e', project_id: 'p', status: 'done' }] }, rooms: { items: [] } } };
  const grid = nodes(Centre({ L })).find((n) => n.type?.name === 'ProjectsGrid');
  const project = nodes(grid.type(grid.props)).find((n) => n.type?.name === 'ProjectCard');
  return nodes(project.type(project.props));
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
