// Offline real static component render; reuse installed Next SWC/React, no server or install.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
const dependencies = process.argv[2];
assert.ok(dependencies, 'pass existing web package.json path for dependency resolution');
const require = createRequire(path.resolve(dependencies));
const React = require('react');
const { renderToStaticMarkup } = require('react-dom/server');
const swc = require('next/dist/build/swc');
await swc.loadBindings();
const filename = path.join(root, 'Build/web/src/app/(public)/library/page.jsx');
const source = readFileSync(filename, 'utf8');
assert.doesNotMatch(source, /\b(import|require|fetch|SPEND_PAUSED|require_reconstruction)\b/);
const { code } = swc.transformSync(source, {
  filename,
  jsc: { target: 'es2022', parser: { syntax: 'ecmascript', jsx: true },
    transform: { react: { runtime: 'classic' } } },
  module: { type: 'commonjs' }
});
const exports = {};
new Function('React', 'exports', code)(React, exports);
const html = renderToStaticMarkup(React.createElement(exports.default));
assert.ok(html.includes('Guest browsing needs no account'));
assert.ok(html.includes('No demos are published yet'));
assert.ok(html.includes('data-state="unavailable"'));
console.log('PASS real guest library component renders with no admission-state dependency');
console.log('LIMIT: static empty guest page only; no HTTP request or precomputed playback tested');
