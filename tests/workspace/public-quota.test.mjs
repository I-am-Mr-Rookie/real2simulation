import test from 'node:test';
import assert from 'node:assert/strict';
import { createLive } from '../../Build/web/src/workspace/live-view.mjs';

const h = (type, props, ...children) => ({ type, props, children: children.flat(Infinity) });
const { Meter } = createLive({ createElement: h });

test('storage meter shows a muted public sample note only for excluded bytes', () => {
  for (const bytes of [undefined, 0, 42]) {
    const tree = Meter({ L: { files: { quota: { storage_bytes_used: 12, storage_bytes_limit: 1024,
      storage_bytes_remaining: 1012, uploads_remaining_today: 20, uploads_daily_limit: 20,
      storage_bytes_public: bytes } } } });
    const note = tree.children.find((n) => n?.children?.includes('Public samples not counted'));
    assert.equal(Boolean(note), bytes > 0);
    if (note) assert.equal(note.props.className, 'lv-muted');
  }
});
