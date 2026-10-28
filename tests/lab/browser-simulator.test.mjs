import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { runBrowserSimulation } from '../../Build/web/src/lab/browser-simulator.mjs';
import { consumeValidatedTrajectoryArtifact, trajectoryFromValidatedArtifact } from '../../Build/simulator/trajectories.mjs';
import { extendedTrajectoryFromValidatedArtifact } from '../../Build/simulator/extended-templates.mjs';

const root = new URL('../../', import.meta.url);
const fixture = (template, suffix = 'artifact') => JSON.parse(readFileSync(new URL(`evidence/S10/browser-simulation/${template}.${suffix}.json`, root), 'utf8'));
const payload = (template = 'free_fall') => ({ mode: 'normal', validatedSetup: fixture(template) });

for (const template of ['free_fall', 'projectile', 'ramp', 'pendulum']) {
  test(`${template}: browser wrapper exactly preserves current engine and server trace`, () => {
    const input = payload(template);
    const before = structuredClone(input);
    const actual = runBrowserSimulation(input);
    const engine = ['ramp', 'pendulum'].includes(template)
      ? extendedTrajectoryFromValidatedArtifact(input.validatedSetup)
      : trajectoryFromValidatedArtifact(consumeValidatedTrajectoryArtifact(input.validatedSetup));
    const server = spawnSync(process.execPath, [fileURLToPath(new URL('Build/lab/simulate.mjs', root))], {
      input: JSON.stringify(input.validatedSetup), encoding: 'utf8', timeout: 30_000,
    });
    assert.equal(server.status, 0, server.stderr);
    assert.deepEqual(actual, engine);
    // JSON transport normalizes signed zero; in-memory engine equality above remains bit-exact.
    assert.equal(JSON.stringify(actual), server.stdout);
    assert.equal(JSON.stringify(actual), JSON.stringify(fixture(template, 'server-trace')));
    assert.deepEqual(runBrowserSimulation(input), actual, 'repeat is deterministic');
    assert.deepEqual(input, before, 'caller DTO is not mutated');
    assert.equal(actual.source, 'simulated');
    assert.equal(actual.inputProvenance, 'synthetic');
    assert.equal(actual.integrator, 'rk4-fixed-step');
    assert.ok(Object.isFrozen(actual));
    assert.ok(actual.samples.length <= 2000);
    assert.ok(actual.samples.every((sample) => [sample.time_s, ...sample.position_m, ...sample.velocity_m_s].every(Number.isFinite)));
  });
}

test('rejects Mystery and absent/bad modes before reading any artifact', () => {
  for (const mode of [undefined, null, 'mystery', 'Mystery', 'NORMAL', '', 0]) {
    assert.throws(() => runBrowserSimulation({ mode, get validatedSetup() { assert.fail('artifact was accessed'); } }), /only explicit normal/);
  }
  assert.throws(() => runBrowserSimulation(null), /only explicit normal/);
  assert.throws(() => runBrowserSimulation(), /only explicit normal/);
});

test('bounds work before touching scene/engine, even if an early event would shorten the run', () => {
  for (const template of ['free_fall', 'projectile', 'ramp', 'pendulum']) {
    const input = payload(template);
    input.validatedSetup.spec.simulation.duration.value = 2;
    Object.defineProperty(input.validatedSetup, 'scene', { get() { assert.fail('engine accessed scene'); } });
    assert.throws(() => runBrowserSimulation(input), /2000 samples/);
  }
});

test('2000 samples includes the initial point; one more is rejected without truncation', () => {
  const input = payload('pendulum');
  input.validatedSetup.spec.simulation.duration.value = 1.999;
  assert.equal(runBrowserSimulation(input).samples.length, 2000);
  input.validatedSetup.spec.simulation.duration.value = 2;
  assert.throws(() => runBrowserSimulation(input), /2000 samples/);
  input.validatedSetup.spec.simulation.duration.value = 0;
  assert.equal(runBrowserSimulation(input).samples.length, 1);
});

test('bad horizons are rejected, not coerced, floored, or silently downsampled', () => {
  for (const [duration, dt] of [[NaN, 0.001], [Infinity, 0.001], [-1, 0.001], ['1', 0.001],
    [1, 0], [1, -0.1], [1, NaN], [1, Infinity], [1, '0.001'], [1, Number.MIN_VALUE], [0.2, 0.003]]) {
    const input = payload();
    input.validatedSetup.spec.simulation.duration.value = duration;
    input.validatedSetup.spec.simulation.time_step.value = dt;
    assert.throws(() => runBrowserSimulation(input));
  }
});

test('actual existing artifact consumers reject malformed envelopes and non-synthetic scenes', () => {
  for (const template of ['free_fall', 'projectile', 'ramp', 'pendulum']) {
    for (const corrupt of [
      (a) => { a.artifact_version = 'forged'; },
      (a) => { delete a.validation; },
      (a) => { a.producer = 'browser'; },
      (a) => { a.scene.synthetic = false; },
      (a) => { a.spec.scene.scene_id = 'different-scene'; },
      (a) => { a.spec.environment.gravity.value = NaN; },
      (a) => { a.spec.placement.origin.value = [0, Infinity, 0]; },
      (a) => { a.spec.environment.gravity_direction = [0, 1, 0]; },
    ]) {
      const input = payload(template);
      corrupt(input.validatedSetup);
      assert.throws(() => runBrowserSimulation(input));
    }
  }
  for (const validatedSetup of [null, {}, { spec: { template: 'real_scene' } }, { spec: { template: 'mystery' } }]) {
    assert.throws(() => runBrowserSimulation({ mode: 'normal', validatedSetup }));
  }
});

test('browser entry dependency graph uses only the existing browser-compatible RK4 modules', () => {
  const entry = readFileSync(new URL('Build/web/src/lab/browser-simulator.mjs', root), 'utf8');
  const files = ['Build/simulator/trajectories.mjs', 'Build/simulator/extended-templates.mjs', 'Build/simulator/rk4.mjs'];
  for (const source of [entry, ...files.map((file) => readFileSync(new URL(file, root), 'utf8'))]) {
    assert.doesNotMatch(source, /node:|require\(|fetch\(|child_process|rapier|requestAnimationFrame|setInterval/);
  }
  const component = readFileSync(new URL('Build/web/src/lab/BrowserSimulation.jsx', root), 'utf8');
  assert.match(component, /'use client'/);
  assert.match(component, /runBrowserSimulation\(payload\)/);
  assert.match(component, /Compute in browser/);
  assert.match(component, /RK4-only/);
  assert.match(component, /role="status"/);
  assert.match(component, /role="img" aria-labelledby/);
  assert.match(component, /sample\.position_m\[1\]/);
  assert.doesNotMatch(component, /requestAnimationFrame|setInterval|setTimeout|fetch\(|JSON\.stringify|gravity|seed/);
});
