import test from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { GUIDE } from '../../Build/web/src/app/(public)/guide/guide-data.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const dir = path.join(root, 'Build/web/src/app/(public)/guide');
const read = (f) => readFileSync(path.join(dir, f), 'utf8');

test('guide has the ten sections and each image exists with alt text', () => {
  assert.equal(GUIDE.length, 10);
  for (const s of GUIDE) for (const [f, alt] of s.images) {
    assert.ok(existsSync(path.join(root, 'Build/web/public/guide', f)), f);
    assert.ok(alt.length > 15, 'alt for ' + f);
  }
});

test('no em dash, no price in guide copy; page wires data; nav links exist', () => {
  for (const f of ['guide-data.mjs', 'page.jsx', 'guide.css']) assert.ok(!/\u2014/.test(read(f)), f);
  assert.ok(!/[$]\d/.test(read('guide-data.mjs')));
  assert.match(read('page.jsx'), /GUIDE\.map/);
  const frame = readFileSync(path.join(root, 'Build/web/src/app/SiteFrame.jsx'), 'utf8');
  assert.ok(frame.includes('href="/guide"'));
  assert.ok(frame.includes('<footer className="site-footer">') && /footer[\s\S]*\/guide/.test(frame));
});
