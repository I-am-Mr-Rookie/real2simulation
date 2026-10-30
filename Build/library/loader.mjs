// S18f guest metadata -> S09 viewer boundary. No asset URL is inferred from audit paths.
import { checkViewerRequest, ViewerError } from '../web/src/viewer/adapter.mjs';
import { checkManifest, DEFAULT_LIMITS, readCapped } from '../web/src/viewer/artifact-loader.mjs';
import { SCALE_UNVERIFIED_BANNER } from '../web/src/viewer/fixture.mjs';
import { deepFreeze } from '../web/src/viewer/common.mjs';

const bad = (message) => { throw new ViewerError('INVALID_ARTIFACT', message); };
const object = (value) => value && typeof value === 'object' && !Array.isArray(value);
const keysAre = (value, keys) => object(value) && Object.keys(value).length === keys.length &&
  keys.every((key) => Object.hasOwn(value, key));
const simulatedBanner = 'SIMULATED — setup metadata only, not a playable replay; SCALE_UNVERIFIED';

export function validateTrace(trace) {
  if (!keysAre(trace, ['kind', 'source', 'inputProvenance', 'dt_s', 'samples', 'label']) ||
      !['free-fall', 'projectile', 'pendulum'].includes(trace.kind) || trace.source !== 'simulated' ||
      trace.inputProvenance !== 'synthetic' || trace.label !== 'SIMULATED' ||
      !Number.isFinite(trace.dt_s) || trace.dt_s <= 0 || !Array.isArray(trace.samples) ||
      trace.samples.length < 2 || trace.samples.length > 4096) bad('Simulation trace labels/bounds are invalid');
  for (let i = 0; i < trace.samples.length; i++) {
    const sample = trace.samples[i];
    if (!keysAre(sample, ['step', 'time_s', 'position_m']) || sample.step !== i ||
        !Number.isFinite(sample.time_s) || sample.time_s !== i * trace.dt_s ||
        !Array.isArray(sample.position_m) || sample.position_m.length !== 3 ||
        ![0, 1, 2].every((j) => Object.hasOwn(sample.position_m, j) && Number.isFinite(sample.position_m[j]))) {
      bad('Simulation trace sample is invalid');
    }
  }
  return trace;
}

/** One entry from guest-1.0.0. Returns metadata + an exact viewer request, never invented render bytes. */
export async function loadLibraryEntry(entry, { fetch: fetchImpl = globalThis.fetch, signal } = {}) {
  if (signal?.aborted) throw new DOMException('Library load aborted', 'AbortError');
  if (!object(entry) || typeof entry.id !== 'string' || typeof entry.title !== 'string') bad('Library entry is invalid');
  // Snapshot safety defaults before awaiting transport; callers may change selection meanwhile.
  try { entry = structuredClone(entry); } catch { bad('Library entry must be plain metadata'); }
  if (entry.label === 'UNAVAILABLE') {
    if (entry.availability !== 'unavailable' || entry.artifact !== null || typeof entry.reason !== 'string') {
      bad('Unavailable entry is inconsistent');
    }
    return deepFreeze({ id: entry.id, title: entry.title, label: 'UNAVAILABLE', availability: 'unavailable',
      banner: 'UNAVAILABLE', reason: entry.reason, canMount: false, viewerRequest: null, metadata: null });
  }
  const defaults = entry.defaults;
  if (!['SIMULATED', 'SCALE_UNVERIFIED'].includes(entry.label) || entry.scale_verified !== false ||
      entry.scale_label !== 'SCALE_UNVERIFIED' || entry.display_only !== true ||
      !['metadata-only', 'playable'].includes(entry.availability) ||
      !object(defaults) || defaults.demo_id !== entry.id || defaults.autoplay !== false ||
      defaults.physics_enabled !== false || defaults.real_scene_prediction !== 'WITHHELD' ||
      !Array.isArray(defaults.parameters) || defaults.parameters.length !== 0) bad('Library safety labels/defaults are invalid');
  const artifact = entry.artifact;
  if (!object(artifact)) bad('Library artifact reference is missing');
  if (!['simulation-trace', 'simulation-setup', 'scene-descriptor', 'challenge-record'].includes(artifact.kind)) {
    throw new ViewerError('UNSUPPORTED', 'Library artifact kind is unsupported');
  }
  const playable = artifact.kind === 'simulation-trace';
  if (playable !== (entry.availability === 'playable') || (playable &&
      (entry.label !== 'SIMULATED' || entry.source?.kind !== 'synthetic' || entry.challenge ||
       entry.gates?.M !== 'NOT_MET' || entry.gates?.RS !== 'NOT_MET'))) bad('Library trace safety labels are invalid');
  if (artifact.media_type !== 'application/json' || typeof artifact.sha256 !== 'string' || !/^[a-f0-9]{64}$/.test(artifact.sha256) ||
      artifact.href !== `/api/library/artifacts/${artifact.sha256}`) bad('Library artifact URL/hash is invalid');
  if (!Number.isSafeInteger(artifact.bytes) || artifact.bytes < 1 || artifact.bytes > DEFAULT_LIMITS.manifestBytes) {
    bad('Library metadata exceeds size limit');
  }
  if (typeof fetchImpl !== 'function') throw new TypeError('fetch is required');
  let response;
  try {
    response = await fetchImpl(artifact.href, { signal, redirect: 'error', credentials: 'omit' });
  } catch (error) {
    if (signal?.aborted) throw error;
    throw new ViewerError('LOAD_FAILED', 'Library metadata could not be fetched');
  }
  let bytes;
  try { bytes = await readCapped(response, artifact.bytes, 'Library metadata'); }
  catch (error) {
    if (signal?.aborted || error instanceof ViewerError) throw error;
    throw new ViewerError('LOAD_FAILED', 'Library metadata stream could not be read');
  }
  if (signal?.aborted) throw new DOMException('Library load aborted', 'AbortError');
  if (bytes.byteLength !== artifact.bytes) bad('Library artifact byte length mismatch');
  const hash = new Uint8Array(await globalThis.crypto.subtle.digest('SHA-256', bytes));
  if (signal?.aborted) throw new DOMException('Library load aborted', 'AbortError');
  if (Array.from(hash, (b) => b.toString(16).padStart(2, '0')).join('') !== artifact.sha256) bad('Library artifact sha256 mismatch');
  let metadata;
  try { metadata = JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(bytes)); }
  catch { bad('Library metadata is not valid JSON'); }
  if (!object(metadata)) bad('Library metadata must be an object');
  let viewerRequest = null;
  let reason;
  if (playable) {
    validateTrace(metadata);
    reason = 'Accepted synthetic simulator trace; display-only, not measured physical evidence.';
  } else if (artifact.kind === 'scene-descriptor') {
    if (entry.label !== 'SCALE_UNVERIFIED' || metadata.synthetic !== false || metadata.scale?.status === 'measured') {
      bad('Scene safety labels disagree');
    }
    viewerRequest = { contract_version: '1.0.0', kind: 'viewer', audience: 'guest', mode: 'inspect',
      scene: { scene_id: metadata.id, scene_version: metadata.schema_version, access: 'public-library', evidence: 'reconstructed' } };
    const why = checkViewerRequest(viewerRequest);
    if (why) bad(why);
    checkManifest(metadata, viewerRequest.scene);
    reason = 'Display-only scene descriptor; render assets are not exposed by the guest API.';
  } else {
    const challenge = artifact.kind === 'challenge-record';
    const keys = challenge ? ['source', 'mode', 'answer_visibility', 'duration_s', 'time_step_s'] :
      ['source', 'template', 'duration_s', 'time_step_s', 'display_only', 'availability'];
    if (!keysAre(metadata, keys) || entry.label !== 'SIMULATED' || metadata.source !== 'simulated' ||
        !Number.isFinite(metadata.duration_s) || metadata.duration_s <= 0 ||
        !Number.isFinite(metadata.time_step_s) || metadata.time_step_s <= 0 || metadata.time_step_s > metadata.duration_s) {
      bad('Simulation setup metadata is invalid');
    }
    if (challenge) {
      if (metadata.mode !== 'mystery-g' || metadata.answer_visibility !== 'withheld-until-fit' ||
          entry.challenge?.mode !== 'mystery-g' || entry.challenge?.answer_visibility !== 'withheld-until-fit' ||
          entry.challenge?.target !== '/lab') bad('Challenge answer boundary is invalid');
      reason = 'Mystery-g setup only; open /lab and reveal only after its server-owned fit.';
    } else {
      if (!['free_fall', 'projectile', 'pendulum'].includes(metadata.template) || metadata.display_only !== true ||
          metadata.availability !== 'metadata-only') bad('Simulation template/availability is invalid');
      reason = 'Simulation setup only; no trajectory or scene-v1 render bundle is exposed.';
    }
  }
  return deepFreeze({ id: entry.id, title: entry.title, label: entry.label, scaleLabel: 'SCALE_UNVERIFIED',
    availability: entry.availability, displayOnly: true, defaults: structuredClone(defaults),
    source: structuredClone(entry.source), gates: structuredClone(entry.gates), limitations: structuredClone(entry.limitations),
    banner: playable ? 'SIMULATED — synthetic trace; SCALE_UNVERIFIED' :
      entry.label === 'SIMULATED' ? simulatedBanner : SCALE_UNVERIFIED_BANNER,
    reason, canMount: playable, viewerRequest, metadata,
    ...(playable ? { trace: { ...metadata, sha256: artifact.sha256 } } : {}) });
}
