import { createHash } from 'node:crypto';

const fail = (message) => { throw new TypeError(`INVALID_REPLAY: ${message}`); };
const finite = (value) => typeof value === 'number' && Number.isFinite(value);
const isPlain = (value) => value !== null && typeof value === 'object' && (Object.getPrototypeOf(value) === Object.prototype || Object.getPrototypeOf(value) === null);
const own = (value, key) => Object.prototype.hasOwnProperty.call(value, key);

function canonical(value) {
  if (typeof value === 'number') { if (!Number.isFinite(value)) fail('non-finite value'); return JSON.stringify(value); }
  if (value === null || typeof value === 'string' || typeof value === 'boolean') return JSON.stringify(value);
  if (Array.isArray(value)) { for (let index = 0; index < value.length; index += 1) if (!own(value, index) || value[index] === undefined) fail('sparse or undefined array value'); return `[${value.map(canonical).join(',')}]`; }
  if (isPlain(value)) return `{${Object.keys(value).sort().map((key) => { if (value[key] === undefined) fail(`undefined field ${key}`); return `${JSON.stringify(key)}:${canonical(value[key])}`; }).join(',')}}`;
  fail('parameters must contain only JSON data');
}

function freezeDeep(value, seen = new WeakSet()) {
  if (value && typeof value === 'object' && !seen.has(value)) { seen.add(value); Object.values(value).forEach((child) => freezeDeep(child, seen)); Object.freeze(value); }
  return value;
}

export function stableHash(value) { return createHash('sha256').update(canonical(value), 'utf8').digest('hex'); }

export function createReplayRecord({ seed, version = 's10-replay-v1', parameters, trace }) {
  if (!Number.isSafeInteger(seed) || seed < 0) fail('seed must be a non-negative safe integer');
  if (typeof version !== 'string' || !version || version.length > 64) fail('version must be a short non-empty string');
  if (!isPlain(parameters)) fail('parameters must be an object');
  if (!Array.isArray(trace) || trace.length === 0) fail('trace must be a non-empty array');
  const body = { version, seed, parameters, trace };
  const record = { ...body, traceHash: stableHash(trace), replayHash: stableHash(body) };
  return freezeDeep(record);
}

export function replayRecord(record, runner) {
  if (!record || typeof record !== 'object' || typeof runner !== 'function') fail('record and runner are required');
  if (record.version !== 's10-replay-v1' || !Number.isSafeInteger(record.seed) || !isPlain(record.parameters) || !Array.isArray(record.trace)) fail('invalid replay record');
  if (record.traceHash !== stableHash(record.trace) || record.replayHash !== stableHash({ version: record.version, seed: record.seed, parameters: record.parameters, trace: record.trace })) fail('replay record hash mismatch');
  const trace = runner(structuredClone(record.parameters), record.seed, record.version);
  if (!Array.isArray(trace) || trace.length === 0) fail('runner must return a non-empty trace');
  const replay = createReplayRecord({ seed: record.seed, version: record.version, parameters: record.parameters, trace });
  if (replay.traceHash !== record.traceHash || replay.replayHash !== record.replayHash) fail('runner output differs from recorded trace');
  return replay;
}

export { canonical as stableCanonicalJson };


