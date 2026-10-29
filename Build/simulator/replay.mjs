const fail = (message) => { throw new TypeError(`INVALID_REPLAY: ${message}`); };
const own = (value, key) => Object.prototype.hasOwnProperty.call(value, key);
const descriptorSafe = (value) => Reflect.ownKeys(value).every((key) => { const d = Object.getOwnPropertyDescriptor(value, key); return d && own(d, 'value'); });
const canonical = (value, stack = new WeakSet()) => {
  if (typeof value === 'number') { if (!Number.isFinite(value)) fail('non-finite value'); return JSON.stringify(value); }
  if (value === null || typeof value === 'string' || typeof value === 'boolean') return JSON.stringify(value);
  if (typeof value !== 'object') fail('unsupported value');
  if (stack.has(value)) fail('cyclic value'); stack.add(value);
  let out;
  if (Array.isArray(value)) {
    const length = Object.getOwnPropertyDescriptor(value, 'length').value, items = [];
    if (Reflect.ownKeys(value).some((key) => key !== 'length' && (typeof key !== 'string' || String(Number(key)) !== key || !Number.isInteger(Number(key)) || Number(key) < 0 || Number(key) >= length))) fail('extra array property');
    for (let i = 0; i < length; i += 1) {
      const d = Object.getOwnPropertyDescriptor(value, String(i));
      if (!d) fail('sparse array');
      if (!own(d, 'value')) fail('accessor property');
      items.push(canonical(d.value, stack));
    }
    out = `[${items.join(',')}]`;
  } else {
    if (Object.getPrototypeOf(value) !== Object.prototype && Object.getPrototypeOf(value) !== null) fail('unsupported object'); if (Reflect.ownKeys(value).some((key) => typeof key !== 'string')) fail('symbol property');
    if (!descriptorSafe(value)) fail('accessor property');
    out = `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonical(Object.getOwnPropertyDescriptor(value, key).value, stack)}`).join(',')}}`;
  }
  stack.delete(value); return out;
};
const clone = (value) => { const text = canonical(value); try { return structuredClone(JSON.parse(text)); } catch { fail('unsupported clone'); } };
const freezeDeep = (value) => { if (value && typeof value === 'object' && !Object.isFrozen(value)) { Object.values(value).forEach(freezeDeep); Object.freeze(value); } return value; };
export async function stableHash(value) { const bytes = new TextEncoder().encode(canonical(value)); const digest = await globalThis.crypto.subtle.digest('SHA-256', bytes); return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, '0')).join(''); }
const validateMetadata = ({ seed, version, parameters, trace }) => {
  if (!Number.isSafeInteger(seed) || seed < 0 || version !== 's10-replay-v1' || !isPlain(parameters) || !Array.isArray(trace) || !trace.length) fail('invalid replay metadata');
};
export async function createReplayRecord(input) {
  if (!isPlain(input)) fail('invalid replay metadata');
  const { seed, version = 's10-replay-v1', parameters, trace } = clone(input), body = { version, seed, parameters, trace };
  validateMetadata(body);
  return freezeDeep({ ...body, traceHash: await stableHash(trace), replayHash: await stableHash(body) });
}
const isPlain = (value) => value !== null && typeof value === 'object' && (Object.getPrototypeOf(value) === Object.prototype || Object.getPrototypeOf(value) === null);
export async function replayRecord(record, runner) {
  if (!isPlain(record) || typeof runner !== 'function') fail('invalid replay record');
  // Detach once before the first await; verification and execution must share one record.
  const snapshot = freezeDeep(clone(record));
  validateMetadata(snapshot);
  const { version, seed, parameters, trace: recordedTrace, traceHash, replayHash } = snapshot;
  if (traceHash !== await stableHash(recordedTrace) || replayHash !== await stableHash({ version, seed, parameters, trace: recordedTrace })) fail('replay record hash mismatch');
  const trace = runner(structuredClone(parameters), seed, version);
  const replay = await createReplayRecord({ seed, version, parameters, trace });
  if (replay.traceHash !== traceHash || replay.replayHash !== replayHash) fail('runner output differs from recorded trace'); return replay;
}


