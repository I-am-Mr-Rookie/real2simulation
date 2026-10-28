const fail = (message) => { throw new TypeError(`INVALID_REPLAY: ${message}`); };
const own = (value, key) => Object.prototype.hasOwnProperty.call(value, key);
const descriptorSafe = (value) => Object.keys(value).every((key) => { const d = Object.getOwnPropertyDescriptor(value, key); return d && !d.get && !d.set; });
const canonical = (value, stack = new WeakSet()) => {
  if (typeof value === 'number') { if (!Number.isFinite(value)) fail('non-finite value'); return JSON.stringify(value); }
  if (value === null || typeof value === 'string' || typeof value === 'boolean') return JSON.stringify(value);
  if (typeof value !== 'object') fail('unsupported value');
  if (stack.has(value)) fail('cyclic value'); stack.add(value);
  let out;
  if (Array.isArray(value)) {
    if (Reflect.ownKeys(value).some((key) => typeof key !== 'string' || !/^\d+$/.test(key) && key !== 'length')) fail('extra array property');
    for (let i = 0; i < value.length; i += 1) if (!own(value, i)) fail('sparse array');
    out = `[${value.map((item) => canonical(item, stack)).join(',')}]`;
  } else {
    if (Object.getPrototypeOf(value) !== Object.prototype && Object.getPrototypeOf(value) !== null) fail('unsupported object'); if (Reflect.ownKeys(value).some((key) => typeof key !== 'string')) fail('symbol property');
    if (!descriptorSafe(value)) fail('accessor property');
    out = `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonical(value[key], stack)}`).join(',')}}`;
  }
  stack.delete(value); return out;
};
const clone = (value) => { const text = canonical(value); try { return structuredClone(JSON.parse(text)); } catch { fail('unsupported clone'); } };
const freezeDeep = (value) => { if (value && typeof value === 'object' && !Object.isFrozen(value)) { Object.values(value).forEach(freezeDeep); Object.freeze(value); } return value; };
export async function stableHash(value) { const bytes = new TextEncoder().encode(canonical(value)); const digest = await globalThis.crypto.subtle.digest('SHA-256', bytes); return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, '0')).join(''); }
export async function createReplayRecord({ seed, version = 's10-replay-v1', parameters, trace }) {
  if (!Number.isSafeInteger(seed) || seed < 0 || typeof version !== 'string' || !version || !isPlain(parameters) || !Array.isArray(trace) || !trace.length) fail('invalid replay metadata');
  const safeParameters = clone(parameters), safeTrace = clone(trace), body = { version, seed, parameters: safeParameters, trace: safeTrace };
  return freezeDeep({ ...body, traceHash: await stableHash(safeTrace), replayHash: await stableHash(body) });
}
const isPlain = (value) => value !== null && typeof value === 'object' && (Object.getPrototypeOf(value) === Object.prototype || Object.getPrototypeOf(value) === null);
export async function replayRecord(record, runner) {
  if (!record || typeof runner !== 'function' || record.version !== 's10-replay-v1') fail('invalid replay record');
  if (record.traceHash !== await stableHash(record.trace) || record.replayHash !== await stableHash({ version: record.version, seed: record.seed, parameters: record.parameters, trace: record.trace })) fail('replay record hash mismatch');
  const trace = runner(structuredClone(record.parameters), record.seed, record.version);
  const replay = await createReplayRecord({ seed: record.seed, version: record.version, parameters: record.parameters, trace });
  if (replay.traceHash !== record.traceHash || replay.replayHash !== record.replayHash) fail('runner output differs from recorded trace'); return replay;
}


