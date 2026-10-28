import { stableHash } from './replay.mjs';

const fail = (message) => { throw new TypeError(`INVALID_MYSTERY_G: ${message}`); };
const finite = (value) => typeof value === 'number' && Number.isFinite(value);
const isPlain = (value) => value !== null && typeof value === 'object' && (Object.getPrototypeOf(value) === Object.prototype || Object.getPrototypeOf(value) === null);
const freezeDeep = (value, seen = new WeakSet()) => { if (value && typeof value === 'object' && !seen.has(value)) { seen.add(value); Object.values(value).forEach((v) => freezeDeep(v, seen)); Object.freeze(value); } return value; };
const clone = (value) => structuredClone(value);

function publicObservation(observation) {
  if (!isPlain(observation)) fail('observation must be an object');
  const out = clone(observation);
  if (JSON.stringify(out).toLowerCase().match(/gravity|seed|secret|hidden|setup/)) fail('observation contains a forbidden secret field');
  return out;
}

export function createMysteryGSession({ seed, gravity_m_s2, privateSetup, observations, version = 's10-mystery-g-v1' }) {
  if (!Number.isSafeInteger(seed) || seed < 0 || !finite(gravity_m_s2) || gravity_m_s2 <= 0) fail('private parameters invalid');
  if (!isPlain(privateSetup) || !Array.isArray(observations) || observations.length === 0) fail('private setup and observations required');
  const publicPayload = freezeDeep({ version, mode: 'mystery-g', observations: observations.map(publicObservation), observationHash: stableHash(observations) });
  let revealed = false;
  return Object.freeze({
    projectPublic: () => publicPayload,
    revealFit: (fitResult) => {
      if (revealed) fail('fit already revealed');
      if (!fitResult || fitResult.status !== 'ok' || !finite(fitResult.gravity_m_s2) || fitResult.gravity_m_s2 <= 0) fail('successful fitter result required');
      revealed = true;
      return freezeDeep({ ...publicPayload, reveal: { gravity_m_s2: fitResult.gravity_m_s2, source: 'measured', fitStatus: 'ok' } });
    },
  });
}

export function publicMysteryGPayload(session) {
  if (!session || typeof session.projectPublic !== 'function') fail('session required');
  return session.projectPublic();
}

