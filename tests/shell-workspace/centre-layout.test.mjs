import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const css = readFileSync(new URL('../../Build/web/src/workspace/workspace.css', import.meta.url), 'utf8');
test('S15ad: centre is a container that stacks viewport above stage/job; cards wrap long tokens', () => {
  assert.match(css, /\.r2s-center \{ container-type: inline-size; \}/);
  assert.match(css, /@container \(max-width: 56rem\) \{[^}]*grid-template-areas: "nav" "viewport" "panel" "job" "side"/);
  assert.match(css, /\.ws-panel, \.ws-job \{ overflow-wrap: anywhere; \}/);
});

