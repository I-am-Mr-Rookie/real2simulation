// Read-only fixture of the real Files component/shell, using CSS from the production build.
import { createRequire } from 'node:module';
import { readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { createLive } from '../../Build/web/src/workspace/live-view.mjs';
import { renderShell } from '../../Build/web/src/shell/workspace-shell.mjs';
import { icon } from '../../Build/web/src/shell/icons.mjs';
const require = createRequire(new URL('../../Build/web/package.json', import.meta.url));
const React = require('react'), { renderToStaticMarkup } = require('react-dom/server');
globalThis.location = { hash: '#files' }; // SSR fixture only; never overrides app/browser authentication.
const h = React.createElement, { Centre } = createLive(React, icon);
const files = [
  { id: 'tiny', name: 'n43-tiny-17.mp4', size: 34816, duration_s: 1, media_type: 'video/mp4' },
  { id: 'long', name: 'A-long-unbroken-public-fixture-filename-for-phone-wrapping.mp4', size: 34816, duration_s: 1, media_type: 'video/mp4', project_id: 'room' },
];
const L = { mode: 'standard', tracked: {}, files: { loaded: true, items: files }, jobs: { projects: { items: [{ id: 'room', mode: 'room' }] } } };
const shell = renderShell(h, { right: false, tools: [], title: 'Local Files fixture', rail: { open: false, pane: 'goto', preview: null } }, {}, {}, h(Centre, { L }));
const css = readdirSync(new URL('../../Build/web/.next/static/css/', import.meta.url)).filter((f) => {
  const text = readFileSync(new URL('../../Build/web/.next/static/css/' + f, import.meta.url), 'utf8');
  return text.includes('.lv-frow') || text.includes('--r2s-font-sans');
});
if (css.length < 2) throw new Error('Build first: global and workspace CSS required');
const html = '<!doctype html><html lang="en" data-theme="dark"><head><meta name="viewport" content="width=device-width, initial-scale=1">' + css.map((f) => '<link rel="stylesheet" href="/_next/static/css/' + f + '">').join('') + '</head><body><main>' + renderToStaticMarkup(shell) + '</main></body></html>';
writeFileSync(new URL('./files.local.html', import.meta.url), html);
console.log('Rendered real Files/shell with production CSS; synthetic read-only data, no interactive writes.');
