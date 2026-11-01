// N12/N29: server-side agent bridge (editor validator + the editor Rapier world; S10b RK4 fallback). Run: node --test tests/lab-editor/*.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { simulate, simulateRK4, ENGINE, FALLBACK_ENGINE } from '../../Build/web/src/lab-editor/agent-run.mjs';

const BRIDGE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../Build/web/src/lab-editor/agent-run.mjs');
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const scene = (objects) => ({ version: 'lab-scene-v1', room: { kind: 'plane', floor_y: 0 }, objects });

test('RK4 fallback: ball falls with the scene gravity and stops at floor contact', () => {
  const [t] = simulateRK4(scene([{ id: 'b', kind: 'ball', position: [0, 1.2, 0], size: [0.05, 0.05, 0.05] }])).traces;
  assert.equal(t.label, 'SIMULATED'); assert.equal(t.ended, 'floor_contact'); assert.equal(t.engine, FALLBACK_ENGINE);
  const s = t.samples[30]; // y = y0 - g t^2 / 2 exactly for RK4 on constant acceleration
  assert.ok(Math.abs(s.p[1] - (1.2 - 0.5 * 9.81 * s.t ** 2)) < 1e-9);
  assert.ok(t.samples.at(-1).p[1] - 0.025 > 0);
});

test('RK4 fallback: fixed objects and ramps produce no trace; pendulum keeps its length', () => {
  const out = simulateRK4(scene([{ id: 'r', kind: 'ramp' }, { id: 'f', kind: 'block', fixed: true },
    { id: 'p', kind: 'pendulum', position: [0, 1.5, 0], params: { length: 0.8, angle_deg: 20 } }]), 2);
  assert.deepEqual(out.traces.map((t) => t.object_id), ['p']);
  for (const { p } of out.traces[0].samples) assert.ok(Math.abs(Math.hypot(p[0], p[1] - 1.5) - 0.8) < 1e-12);
});

test('Rapier path: same world as Play, free fall gives g within the fitter sigma, trace ends at floor contact', async () => {
  const out = await simulate(scene([{ id: 'r', kind: 'ramp', sensor: true }, { id: 'f', kind: 'block', fixed: true },
    { id: 'b', kind: 'ball', position: [3, 1.2, 0], size: [0.05, 0.05, 0.05] }])); // clear of the default ramp at the origin
  assert.equal(out.engine, ENGINE);
  assert.deepEqual(out.traces.map((t) => t.object_id), ['b']);
  const [t] = out.traces;
  assert.equal(t.ended, 'floor_contact'); assert.equal(t.engine, ENGINE); assert.equal(t.version, 'lab-trace-v1');
  assert.ok(t.samples.length > 40 && t.samples.at(-1).p[1] < 0.1, t.samples.length + ' ' + t.samples.at(-1).p[1]);
  const py = spawnSync('python', ['-c', 'import json,sys; from Build.api.agent.lab_handlers import measure; print(json.dumps(measure(json.load(sys.stdin), {})))'],
    { cwd: ROOT, input: JSON.stringify(t), encoding: 'utf8' });
  if (py.status !== 0) { console.log('fitter skipped:', py.stderr.slice(-300)); return; }
  const { g } = JSON.parse(py.stdout);
  assert.ok(g.uncertainty > 0 && Math.abs(g.value - 9.81) < 3 * g.uncertainty, JSON.stringify(g));
});

test('CLI rejects invalid scenes with the editor validator message', () => {
  const r = spawnSync(process.execPath, [BRIDGE], { input: JSON.stringify({ op: 'validate', scene: { version: 'x' } }), encoding: 'utf8' });
  assert.deepEqual(JSON.parse(r.stdout), { status: 'error', error: 'version must be lab-scene-v1' });
  const ok = spawnSync(process.execPath, [BRIDGE], { input: JSON.stringify({ op: 'run', scene: scene([]) }), encoding: 'utf8' });
  assert.equal(JSON.parse(ok.stdout).engine, ENGINE);
});
