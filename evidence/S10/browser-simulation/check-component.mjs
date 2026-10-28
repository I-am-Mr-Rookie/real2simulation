// Local element/hook harness only, not a DOM, browser, accessibility audit, or layout check.
// Usage: node check-component.mjs <existing Build/web/node_modules>
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { runBrowserSimulation } from '../../../Build/web/src/lab/browser-simulator.mjs';
import { plotPoints, sampleRows } from '../../../Build/web/src/lab/fit-contract.mjs';

const require = createRequire(import.meta.url);
const deps = path.resolve(process.argv[2]);
const babel = require(path.join(deps, 'next/dist/compiled/babel/core.js'));
const parser = require(path.join(deps, 'next/dist/compiled/babel/parser.js'));
const presetReact = require(path.join(deps, 'next/dist/compiled/babel/preset-react.js'));
const source = readFileSync(new URL('../../../Build/web/src/lab/BrowserSimulation.jsx', import.meta.url), 'utf8');
parser.parse(source, { sourceType: 'module', plugins: ['jsx'] });
console.log('Fresh JSX parse PASS (existing Next Babel parser)');
const code = babel.transformSync(source, { configFile: false, babelrc: false,
  presets: [[presetReact, { runtime: 'classic', pragma: 'h', pragmaFrag: 'Fragment' }]],
}).code.replace(/^import .*;$/gm, '').replace('export default function', 'return function');
let state = null;
let computations = 0;
const h = (type, props, ...children) => ({ type, props: props || {}, children: children.flat(Infinity) });
const Component = new Function('useId', 'useState', 'h', 'Fragment', 'runBrowserSimulation', 'plotPoints', 'sampleRows', code)(
  () => 'browser-trace-test', () => [state, (next) => { state = next; }], h, Symbol('Fragment'),
  (payload) => { computations += 1; return runBrowserSimulation(payload); }, plotPoints, sampleRows);
const nodes = (tree) => typeof tree === 'object' && tree !== null ? [tree, ...tree.children.flatMap(nodes)] : [];
const text = (tree) => typeof tree === 'object' && tree !== null ? tree.children.map(text).join(' ') : String(tree ?? '');

for (const template of ['free_fall', 'projectile', 'ramp', 'pendulum']) {
  state = null;
  const payload = { mode: 'normal', validatedSetup: JSON.parse(readFileSync(new URL(`./${template}.artifact.json`, import.meta.url), 'utf8')) };
  let tree = Component({ payload });
  const before = computations;
  assert.ok(!nodes(tree).some((node) => node.type === 'polyline'));
  nodes(tree).find((node) => node.type === 'button').props.onClick();
  assert.equal(computations, before + 1, 'compute happens on user click, not render');
  tree = Component({ payload });
  const trace = runBrowserSimulation(payload);
  const points = nodes(tree).find((node) => node.type === 'polyline').props.points;
  assert.equal(points.split(' ').length, trace.samples.length);
  assert.equal(points, plotPoints(trace.samples.map((sample) => ({ time_s: sample.time_s, position_m: sample.position_m[1] }))).points);
  assert.match(text(tree), /Computed.*actual/);
  assert.match(text(tree), /RK4-only/);
  assert.ok(nodes(tree).filter((node) => node.type === 'tr').length <= 10);
  const fresh = { ...payload };
  assert.ok(!nodes(Component({ payload: fresh })).some((node) => node.type === 'polyline'), 'new DTO cannot show stale trace');
  console.log(`${template}: click computation, full actual trace, sampled table, stale DTO reset PASS`);
}
state = null;
const mystery = { mode: 'mystery', get validatedSetup() { assert.fail('Mystery artifact accessed'); } };
let tree = Component({ payload: mystery });
nodes(tree).find((node) => node.type === 'button').props.onClick();
tree = Component({ payload: mystery });
assert.match(text(tree), /Browser simulation unavailable/);
assert.ok(!nodes(tree).some((node) => node.type === 'polyline'));
assert.doesNotMatch(text(tree), /Mystery artifact accessed|gravity_m_s2|seed|validatedSetup/);
console.log('Mystery rejection and generic rendered error PASS; no animation or frame lifecycle exists');
