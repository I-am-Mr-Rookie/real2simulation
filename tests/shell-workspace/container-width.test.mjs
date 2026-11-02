import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const read = file => readFileSync(new URL('../../Build/web/src/' + file, import.meta.url), 'utf8');

test('header, main and footer share the page width, including the wide editor', () => {
  assert.match(read('app/styles.css'), /\.site-header, main, \.site-footer \{ width: var\(--site-width, min\(1120px, calc\(100% - 2\.5rem\)\)\)/);
  const editor = read('lab-editor/lab-editor.css');
  assert.match(editor, /body:has\(\.lab-editor\) \{ --site-width: min\(1680px, calc\(100% - 48px\)\); \}/);
  assert.match(editor, /body:has\(\.lab-editor\) \{ --site-width: calc\(100% - 24px\); \}/);
  assert.doesNotMatch(editor, /100vw|margin-left: 50%|translateX\(-50%\)/);
  const workspace = read('workspace/workspace.css');
  assert.match(workspace, /main:has\(\.r2s-shell\) \{ width: 100%/);
  assert.match(workspace, /body:has\(\.r2s-shell\) \.site-header \{ width: 100%/);
  assert.match(workspace, /body:has\(\.r2s-shell\) \.site-footer \{ display: none/);
});
