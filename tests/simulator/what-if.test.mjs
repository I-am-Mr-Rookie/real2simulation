// S15r (owner Q20=A): labelled what-if mode accepts only the API what-if artifact; the synthetic-only path is unchanged.
import test from 'node:test';
import assert from 'node:assert/strict';
import { runBrowserSimulation, WHAT_IF_LABEL } from '../../Build/web/src/lab/browser-simulator.mjs';

const q = (value, unit) => ({ value, unit });
const spec = { template: 'free_fall', scene: { scene_id: 'RM04', schema_version: '1.0.0' },
  environment: { gravity: q(9.81, 'm/s^2'), gravity_direction: [0, -1, 0] }, placement: { origin: q([0, 1.5, 0], 'm') },
  parameters: { drop_height: q(1.5, 'm'), initial_vertical_velocity: q(0, 'm/s') },
  simulation: { duration: q(0.6, 's'), time_step: q(0.01, 's') } };
const whatIf = { artifact_version: 's15r-what-if-setup-v1', validation: 'numeric_contract_only', what_if: true, label: WHAT_IF_LABEL,
  producer: 'contracts/experiment/validate_experiment.py#validate', spec,
  scene: { id: 'RM04', schema_version: '1.0.0', synthetic: false, scale_verified: false } };

test('what-if artifact runs only in explicit what-if mode, labelled and never synthetic', () => {
  const t = runBrowserSimulation({ mode: 'what-if', validatedSetup: whatIf });
  assert.equal(t.label, 'SIMULATED what-if of your described setup; scale unverified; not measured from the clip');
  assert.equal(t.whatIf, true);
  assert.equal(t.source, 'simulated');
  assert.equal(t.inputProvenance, 'image-derived');
  assert.ok(t.samples.length > 1);
  assert.throws(() => runBrowserSimulation({ mode: 'normal', validatedSetup: whatIf }), /INVALID_BROWSER_SIMULATION|untrusted/);
});

test('what-if mode rejects anything not marked non-synthetic, scale-unverified and exactly labelled', () => {
  for (const bad of [{ ...whatIf, label: 'measured' }, { ...whatIf, what_if: false }, { ...whatIf, scene: { ...whatIf.scene, synthetic: true } },
    { ...whatIf, scene: { ...whatIf.scene, scale_verified: true } }, { ...whatIf, validation: 'validate_setup' },
    { ...whatIf, artifact_version: 's10-validated-setup-v1', validation: 'validate_setup', producer: 'contracts/experiment/validate_experiment.py' },
    { ...whatIf, spec: { ...spec, template: 'pendulum' } }, { ...whatIf, spec: { ...spec, parameters: {} } }]) {
    assert.throws(() => runBrowserSimulation({ mode: 'what-if', validatedSetup: bad }), /INVALID_BROWSER_SIMULATION/);
  }
});

test('normal mode still rejects a recorded (non-synthetic) S10-shaped artifact', () => {
  const s10 = { artifact_version: 's10-validated-setup-v1', validation: 'validate_setup', producer: 'contracts/experiment/validate_experiment.py',
    spec, scene: { id: 'RM04', schema_version: '1.0.0', synthetic: false } };
  assert.throws(() => runBrowserSimulation({ mode: 'normal', validatedSetup: s10 }), /synthetic scene mismatch/);
  assert.throws(() => runBrowserSimulation({ mode: 'whatif', validatedSetup: whatIf }), /only explicit normal mode/);
});
