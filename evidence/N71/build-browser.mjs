// Reuses Next's installed webpack; no npm install, new dependency or production route.
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { THEME_CSS } from '../../Build/web/src/shell/theme.mjs';
const req = createRequire(new URL('../../Build/web/package.json', import.meta.url));
const { webpack } = req('next/dist/compiled/webpack/webpack');
const root = new URL('../../', import.meta.url), out = new URL('./runtime/', import.meta.url);
mkdirSync(out, { recursive: true });
writeFileSync(new URL('app.css', out), THEME_CSS + ['Build/web/src/app/styles.css', 'Build/web/src/workspace/workspace.css']
  .map((p) => readFileSync(new URL(p, root), 'utf8')).join('\n'));
const stats = await new Promise((resolve, reject) => webpack({ mode: 'development', devtool: false,
  entry: fileURLToPath(new URL('./browser-client.mjs', import.meta.url)),
  resolve: { modules: [fileURLToPath(new URL('Build/web/node_modules', root)), 'node_modules'] },
  output: { path: fileURLToPath(out), filename: 'bundle.js' } }, (err, stats) => err ? reject(err) : resolve(stats)));
if (stats.hasErrors()) throw new Error(stats.toString({ all: false, errors: true }));
console.log('N71 local browser bundle built');
