import { stableHash } from './replay.mjs';
const fail = (message) => { throw new TypeError(`INVALID_MYSTERY_G: ${message}`); };
const finite = (v) => typeof v === 'number' && Number.isFinite(v);
const freezeDeep = (v) => { if (v && typeof v === 'object' && !Object.isFrozen(v)) { Object.values(v).forEach(freezeDeep); Object.freeze(v); } return v; };
const handoffs = new WeakSet();
function sample(value) {
  if (!value || Object.getPrototypeOf(value) !== Object.prototype || Object.keys(value).sort().join(',') !== 'position_m,time_s') fail('observation must be an allowlisted numeric sample');
  if (!finite(value.time_s) || !finite(value.position_m)) fail('observation values must be finite');
  return { time_s: value.time_s, position_m: value.position_m };
}
export function createTrustedFitterHandoff(result) {
  if (!result || result.status !== 'ok' || !result.gravity || result.gravity.unit !== 'm/s^2' || !finite(result.gravity.value) || result.gravity.value <= 0 || !finite(result.gravity.uncertainty) || result.gravity.uncertainty < 0 || result.gravity.source?.label !== 'simulated' || result.covariance?.status !== 'available' || result.uncertainty?.model !== 'iid_fixed_clock_scale') fail('actual successful S11 fitter response required');
  const handoff = Object.freeze({ result }); handoffs.add(handoff); return handoff;
}
export async function createMysteryGSession({ seed, gravity_m_s2, privateSetup, observations, version = 's10-mystery-g-v1' }) {
  if (!Number.isSafeInteger(seed) || seed < 0 || !finite(gravity_m_s2) || gravity_m_s2 <= 0 || !privateSetup || !Array.isArray(observations) || !observations.length) fail('private parameters invalid');
  const publicObservations = observations.map(sample), publicPayload = freezeDeep({ version, mode: 'mystery-g', observations: publicObservations, observationHash: await stableHash(publicObservations) });
  let revealed = false;
  return Object.freeze({ projectPublic: () => publicPayload, revealFit: (handoff) => { if (revealed) fail('fit already revealed'); if (!handoffs.has(handoff)) fail('trusted fitter handoff required'); revealed = true; const q = handoff.result.gravity; return freezeDeep({ ...publicPayload, reveal: { gravity: q.value, uncertainty: q.uncertainty, unit: q.unit, source: q.source.label, fitStatus: 'ok' } }); } });
}
export function publicMysteryGPayload(session) { if (!session || typeof session.projectPublic !== 'function') fail('session required'); return session.projectPublic(); }
