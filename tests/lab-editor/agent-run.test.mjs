// N12: server-side agent bridge (editor validator + S10b RK4). Run: node --test tests/lab-editor/
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { simulate } from '../../Build/web/src/lab-editor/agent-run.mjs';

const BRIDGE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../Build/web/src/lab-editor/agent-run.mjs');
const scene = (objects) => ({ version: 'lab-scene-v1', room: { kind: 'plane', floor_y: 0 }, objects });

test('ball falls with the scene gravity and stops at floor contact', () => {
  const [t] = simulate(scene([{ id: 'b', kind: 'ball', position: [0, 1.2, 0], size: [0.05, 0.05, 0.05] }])).traces;
  assert.equal(t.label, 'SIMULATED'); assert.equal(t.ended, 'floor_contact');
  const s = t.samples[30]; // y = y0 - g t^2 / 2 exactly for RK4 on constant acceleration
  assert.ok(Math.abs(s.p[1] - (1.2 - 0.5 * 9.81 * s.t ** 2)) < 1e-9);
  assert.ok(t.samples.at(-1).p[1] - 0.025 > 0);
});

test('fixed objects and ramps produce no trace; pendulum keeps its length', () => {
  const out = simulate(scene([{ id: 'r', kind: 'ramp' }, { id: 'f', kind: 'block', fixed: true },
    { id: 'p', kind: 'pendulum', position: [0, 1.5, 0], params: { length: 0.8, angle_deg: 20 } }]), 2);
  assert.deepEqual(out.traces.map((t) => t.object_id), ['p']);
  for (const { p } of out.traces[0].samples) assert.ok(Math.abs(Math.hypot(p[0], p[1] - 1.5) - 0.8) < 1e-12);
});

test('CLI rejects invalid scenes with the editor validator message', () => {
  const r = spawnSync(process.execPath, [BRIDGE], { input: JSON.stringify({ op: 'validate', scene: { version: 'x' } }), encoding: 'utf8' });
  assert.deepEqual(JSON.parse(r.stdout), { status: 'error', error: 'version must be lab-scene-v1' });
  const ok = spawnSync(process.execPath, [BRIDGE], { input: JSON.stringify({ op: 'run', scene: scene([]) }), encoding: 'utf8' });
  assert.equal(JSON.parse(ok.stdout).status, 'ok');
});
