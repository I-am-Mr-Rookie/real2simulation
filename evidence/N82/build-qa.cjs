const path = require('node:path');
const assert = require('node:assert/strict');
const { webpack } = require('../../Build/web/node_modules/next/dist/compiled/webpack/webpack');
webpack({ mode: 'production', entry: path.join(__dirname, 'qa-entry.mjs'),
  optimization: { minimize: false },
  output: { path: path.join(__dirname, 'harness.local'), filename: 'qa.js' },
  resolve: { modules: [path.resolve(__dirname, '../../Build/web/node_modules'), 'node_modules'] },
}, (err, stats) => {
  assert.ifError(err);
  if (stats.hasErrors()) { console.error(stats.toString({ all: false, errors: true })); process.exitCode = 1; }
  else console.log('PASS: bundled actual workspace module with installed React');
});
