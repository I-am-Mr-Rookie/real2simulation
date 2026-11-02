import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const read = file => readFileSync(new URL('../../Build/web/src/' + file, import.meta.url), 'utf8');

test('header, main and footer share the page width; the lab editor is full-window', () => {
  assert.match(read('app/styles.css'), /\.site-header, main, \.site-footer \{ width: var\(--site-width, min\(1120px, calc\(100% - 2\.5rem\)\)\)/);
  const editor = read('lab-editor/lab-editor.css');
  // N56 superseded N54's wide-editor width: the editor hides the site chrome and fills the window.
  assert.match(editor, /body:has\(\.lab-editor\) \.site-header, body:has\(\.lab-editor\) \.site-footer/);
  assert.match(editor, /position: fixed; inset: 0;/);
  assert.doesNotMatch(editor, /100vw|margin-left: 50%/); // translateX(-50%) is now legit: it centres the floating toolbar
  const workspace = read('workspace/workspace.css');
  assert.match(workspace, /main:has\(\.r2s-shell\) \{ width: 100%/);
  assert.match(workspace, /body:has\(\.r2s-shell\) \.site-header \{ width: 100%/);
  assert.match(workspace, /body:has\(\.r2s-shell\) \.site-footer \{ display: none/);
});
