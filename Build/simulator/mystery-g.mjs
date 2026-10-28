import { stableHash } from './replay.mjs';
const VERSION = 's10-mystery-g-v1';
const fail = (message) => { throw new TypeError(`INVALID_MYSTERY_G: ${message}`); };
const finite = (v) => typeof v === 'number' && Number.isFinite(v);
const plain = (v) => v !== null && typeof v === 'object' && Object.getPrototypeOf(v) === Object.prototype;
const safeKeys = (v, expected) => { if (!plain(v) || Reflect.ownKeys(v).length !== expected.length || Reflect.ownKeys(v).some((k) => typeof k !== 'string' || !expected.includes(k) || !Object.getOwnPropertyDescriptor(v,k) || Object.getOwnPropertyDescriptor(v,k).get || Object.getOwnPropertyDescriptor(v,k).set)) fail('unsupported or accessor object'); };
const freeze = (v) => { if (v && typeof v === 'object' && !Object.isFrozen(v)) { Object.values(v).forEach(freeze); Object.freeze(v); } return v; };
function sample(v) { safeKeys(v, ['time_s','position_m']); if (!finite(v.time_s) || !finite(v.position_m)) fail('observation values must be finite'); return { time_s:v.time_s, position_m:v.position_m }; }
const handoffs = new WeakMap();
export async function createTrustedFitterHandoff(result, observations) {
  if (!result || result.status !== 'ok' || !Array.isArray(observations)) fail('actual S11 response and observations required');
  const gravity=result.gravity; if (!plain(gravity) || gravity.unit !== 'm/s^2' || !finite(gravity.value) || gravity.value <= 0 || !finite(gravity.uncertainty) || gravity.uncertainty < 0 || !plain(gravity.source) || gravity.source.label !== 'simulated' || typeof gravity.source.evidence !== 'string' || result.covariance?.status !== 'available' || !['iid_fixed_clock_scale', 'independent_position_time_first_order'].includes(result.uncertainty?.model)) fail('actual successful S11 fitter response required');
  const clean=freeze({ status:'ok', gravity:{ value:gravity.value, unit:'m/s^2', uncertainty:gravity.uncertainty, source:{ label:'simulated', evidence:gravity.source.evidence } } });
  const binding=await stableHash(observations.map(sample)); const handoff=Object.freeze({ result:clean, observationHash:binding }); handoffs.set(handoff, binding); return handoff;
}
export async function createMysteryGSession({ seed, gravity_m_s2, privateSetup, observations, version = VERSION }) {
  if (version !== VERSION || !Number.isSafeInteger(seed) || seed < 0 || !finite(gravity_m_s2) || gravity_m_s2 <= 0 || !plain(privateSetup) || !Array.isArray(observations) || !observations.length) fail('private parameters invalid');
  const publicObservations=observations.map(sample), observationHash=await stableHash(publicObservations); const payload=freeze({ version:VERSION, mode:'mystery-g', observations:publicObservations, observationHash }); let revealed=false;
  return Object.freeze({ projectPublic:()=>payload, revealFit:(handoff)=>{ if(revealed) fail('fit already revealed'); if(!handoffs.has(handoff) || handoffs.get(handoff)!==observationHash) fail('trusted fitter handoff does not match session observations'); revealed=true; const q=handoff.result.gravity; return freeze({...payload,reveal:{gravity:q.value,uncertainty:q.uncertainty,unit:q.unit,source:q.source.label,fitStatus:'ok'}}); } });
}
export function publicMysteryGPayload(session) { if (!session || typeof session.projectPublic !== 'function') fail('session required'); return session.projectPublic(); }
