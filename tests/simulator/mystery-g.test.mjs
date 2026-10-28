import assert from 'node:assert/strict';
import test from 'node:test';
import { createMysteryGSession, publicMysteryGPayload } from '../../Build/simulator/mystery-g.mjs';

const session = () => createMysteryGSession({ seed: 42, gravity_m_s2: 9.81, privateSetup: { chamber: 'sealed', hiddenValue: 9.81 }, observations: [{ time_s: 0, position_m: 2 }, { time_s: 1, position_m: -2.905 }] });

test('public projection contains observations but no private gravity, seed, or setup', () => {
  const payload = publicMysteryGPayload(session());
  const text = JSON.stringify(payload).toLowerCase();
  assert.equal(payload.mode, 'mystery-g');
  assert.match(text, /observations/);
  assert.doesNotMatch(text, /gravity|seed|hidden|secret|setup/);
  assert.ok(Object.isFrozen(payload) && Object.isFrozen(payload.observations));
});

test('reveal requires a successful explicit fitter handoff and is immutable/single-use', () => {
  const mystery = session();
  assert.throws(() => mystery.revealFit({ status: 'error', gravity_m_s2: 9.81 }), /successful/);
  assert.throws(() => mystery.revealFit({ status: 'ok', gravity_m_s2: NaN }), /successful/);
  const revealed = mystery.revealFit({ status: 'ok', gravity_m_s2: 9.806 });
  assert.equal(revealed.reveal.source, 'measured');
  assert.equal(revealed.reveal.gravity_m_s2, 9.806);
  assert.throws(() => mystery.revealFit({ status: 'ok', gravity_m_s2: 9.81 }), /already/);
  assert.throws(() => { revealed.reveal.gravity_m_s2 = 0; }, TypeError);
});

test('rejects private invalid inputs and keeps errors value-free', () => {
  assert.throws(() => createMysteryGSession({ seed: 1, gravity_m_s2: Infinity, privateSetup: {}, observations: [{}] }), /private parameters invalid/);
  assert.throws(() => createMysteryGSession({ seed: 1, gravity_m_s2: 9.8, privateSetup: {}, observations: [{ setup: 'bad' }] }), /forbidden/);
});
