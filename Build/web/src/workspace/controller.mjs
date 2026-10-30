// S15n: workspace controller = workflow.reduce() + fetch adapters for the S15m PLAN §2 BFF contract (/api/workspace/*).
// Never fabricates data: every state change comes from a validated API response or the injected browser simulator.
// Transport/API failures set state.error to a reducer code and leave the phase (and any prior real data) unchanged.
import { reduce, initialState } from './workflow.mjs';

export const API_BASE = '/api/workspace';
const CODES = ['UNAUTHORIZED', 'NOT_FOUND', 'INVALID_INPUT', 'DEPENDENCY_UNAVAILABLE', 'SPEND_PAUSED', 'PROCESSING_FAILED'];
const BY_STATUS = { 401: 'UNAUTHORIZED', 403: 'UNAUTHORIZED', 404: 'NOT_FOUND', 400: 'INVALID_INPUT', 409: 'INVALID_INPUT', 413: 'INVALID_INPUT', 415: 'INVALID_INPUT', 422: 'INVALID_INPUT', 402: 'SPEND_PAUSED' };

// Body code wins (API {error:{code,message}} or FastAPI {detail:{code,message}}); else HTTP status; 5xx/network = dependency down.
export function errorOf(status, body) {
  const e = body?.error ?? body?.detail;
  const code = CODES.includes(e?.code) ? e.code : BY_STATUS[status] ?? 'DEPENDENCY_UNAVAILABLE';
  const message = typeof e?.message === 'string' && e.message ? e.message : typeof e === 'string' && e ? e : `Workspace API ${status || 'unreachable'}`;
  return { code, message: message.slice(0, 240) };
}

export async function sha256Hex(bytes) {
  const d = await globalThis.crypto.subtle.digest('SHA-256', bytes);
  return [...new Uint8Array(d)].map((b) => b.toString(16).padStart(2, '0')).join('');
}

const ACTIVE = new Set(['upload.queued', 'upload.running']);

// deps: fetch (BFF, same-origin cookies), simulate(validatedSetup, seed) -> observations (runBrowserSimulation wrapper),
// sleep(ms), onChange(snapshot). Missing simulate = honest DEPENDENCY_UNAVAILABLE, never fixture output.
export function createController({ fetch: f = globalThis.fetch, base = API_BASE, simulate, sleep = (ms) => new Promise((r) => setTimeout(r, ms)),
  pollMs = 1000, maxPolls = 900, onChange, newSessionId = () => 'fit-' + Date.now().toString(36) } = {}) {
  let state = initialState();
  const meta = { busy: false, upload: null, events: [], questions: null, validatedSetup: null, report: null, provenance: null };
  const snap = () => ({ state, ...meta });
  const set = (s) => { state = s; onChange?.(snap()); return state; };
  const patch = (m) => { Object.assign(meta, m); onChange?.(snap()); };
  const dispatch = (event, deps) => set(reduce(state, event, deps));
  const failWith = (error) => { set({ ...state, error }); return null; };

  async function call(method, path, body, headers = {}) {
    let res;
    try {
      const raw = body instanceof Uint8Array;
      res = await f(base + '/' + path, { method, credentials: 'same-origin', cache: 'no-store',
        headers: raw ? { 'content-type': 'application/octet-stream', ...headers } : body === undefined ? headers : { 'content-type': 'application/json', ...headers },
        body: body === undefined ? undefined : raw ? body : JSON.stringify(body) });
    } catch { return { error: { code: 'DEPENDENCY_UNAVAILABLE', message: 'Workspace API unreachable.' } }; }
    let data = null;
    try { data = await res.json(); } catch { /* non-JSON body: status decides */ }
    if (res.ok && data === null) return { error: { code: 'PROCESSING_FAILED', message: 'Workspace API returned a non-JSON response.' } };
    return res.ok ? { data } : { error: errorOf(res.status, data) };
  }

  async function poll(jobId) {
    let after = 0;
    // first read always runs: the S13i RECORDED replay can already be ready in the complete response, and its events still show
    for (let i = 0; i < maxPolls && (i === 0 || ACTIVE.has(state.phase)); i += 1) {
      const r = await call('GET', `jobs/${encodeURIComponent(jobId)}?after=${after}`);
      if (r.error) return failWith(r.error);
      const doc = r.data;
      if (doc?.kind !== 'job_progress' || doc.job_id !== jobId) return failWith({ code: 'PROCESSING_FAILED', message: 'Progress response failed validation.' });
      if (Array.isArray(doc.events) && doc.events.length) patch({ events: [...meta.events, ...doc.events] });
      after = Math.max(after, ...(doc.events ?? []).map((e) => (Number.isInteger(e?.revision) ? e.revision : 0)));
      dispatch({ type: 'JOB_UPDATE', job: doc.job });
      if (ACTIVE.has(state.phase)) await sleep(pollMs);
    }
    if (ACTIVE.has(state.phase)) failWith({ code: 'DEPENDENCY_UNAVAILABLE', message: 'Job progress timed out; the job may still finish on the server.' });
    return state;
  }

  return {
    get state() { return state; },
    snapshot: snap,
    dispatch,

    // file: File/Blob with name, type, size. Bytes go up in policy-sized chunks; the server decides approval by sha256.
    async upload(file) {
      if (meta.busy) return null;
      patch({ busy: true, upload: { name: file?.name ?? 'upload', committed: 0, total: file?.size ?? 0 }, events: [], report: null });
      try {
        // shortcut: whole file in memory (crypto.subtle has no streaming hash); fine for approved short clips, upgrade to chunked hashing if large uploads are allowed.
        const bytes = new Uint8Array(await file.arrayBuffer());
        const sha256 = await sha256Hex(bytes);
        let r = await call('POST', 'uploads', { filename: file.name, media_type: file.type, size_bytes: bytes.length, sha256 });
        if (r.error) return failWith(r.error);
        const session = r.data, step = session.chunk_bytes;
        if (typeof session.upload_id !== 'string' || !(Number.isInteger(step) && step > 0)) return failWith({ code: 'PROCESSING_FAILED', message: 'Upload session failed validation.' });
        const id = encodeURIComponent(session.upload_id);
        for (let off = session.committed_bytes ?? 0; off < bytes.length; off += step) {
          const chunk = bytes.subarray(off, off + step);
          r = await call('PUT', `uploads/${id}/chunks/${off}`, chunk, { 'x-chunk-sha256': await sha256Hex(chunk) });
          if (r.error) return failWith(r.error);
          patch({ upload: { ...meta.upload, committed: Math.min(bytes.length, off + chunk.length) } });
        }
        // S13i: complete starts the job and returns {upload, job, provenance}; there is no separate POST /jobs.
        r = await call('POST', `uploads/${id}/complete`, {});
        if (r.error) return failWith(r.error);
        const job = r.data?.job;
        patch({ upload: { ...meta.upload, approvedClip: typeof r.data?.upload?.sha256 === 'string' ? 'sha256 ' + r.data.upload.sha256.slice(0, 12) : null }, provenance: r.data?.provenance ?? null });
        dispatch({ type: 'UPLOAD_STARTED', jobId: job?.job_id });
        if (state.phase !== 'upload.queued') return failWith({ code: 'PROCESSING_FAILED', message: 'Job response failed validation.' });
        dispatch({ type: 'JOB_UPDATE', job });
        return await poll(job.job_id);
      } finally { patch({ busy: false }); }
    },

    async loadQuestions() {
      if (state.phase !== 'interview.active') return null;
      const r = await call('GET', `scenes/${encodeURIComponent(state.scene?.scene_id ?? '')}/questions`);
      if (r.error) return failWith(r.error);
      patch({ questions: r.data });
      return r.data;
    },

    // The API (S08 validate_setup) is the validator; the reducer accepts only the exact spec object it returned.
    async submitAnswers(answers) {
      if (state.phase !== 'interview.active') return state;
      const r = await call('POST', `scenes/${encodeURIComponent(state.scene?.scene_id ?? '')}/spec`, { answers });
      if (r.error) return failWith(r.error);
      const d = r.data;
      const ok = d?.ok === true && !!d.spec && !!d.validated_setup;
      if (ok) patch({ validatedSetup: d.validated_setup });
      return dispatch({ type: 'INTERVIEW_SPEC', spec: ok ? d.spec : null },
        { validateSpec: (s) => (ok && s === d.spec ? { ok: true } : { ok: false, errors: Array.isArray(d?.errors) && d.errors.length ? d.errors.map(String) : ['spec rejected'] }) });
    },

    async run(seed) {
      dispatch({ type: 'RUN_START', seed });
      if (state.phase !== 'run.running') return state;
      if (typeof simulate !== 'function' || !meta.validatedSetup) {
        dispatch({ type: 'RUN_FAIL', error: { message: 'Browser simulator unavailable.' } });
        return failWith({ code: 'DEPENDENCY_UNAVAILABLE', message: 'Browser simulator unavailable.' });
      }
      try { return dispatch({ type: 'RUN_COMPLETE', seed, observations: await simulate(meta.validatedSetup, seed) }); }
      catch (e) { return dispatch({ type: 'RUN_FAIL', error: { message: String(e?.message ?? e) } }); }
    },

    // extra: instrument-derived fitter request fields; observations are the stored simulated run, verbatim.
    async fit(extra = {}) {
      dispatch({ type: 'FIT_START', sessionId: newSessionId() });
      if (state.phase !== 'fit.running') return state;
      const r = await call('POST', 'fit', { ...extra, sessionId: state.fit.sessionId, observations: state.run.observations });
      if (r.error) { dispatch({ type: 'FIT_FAIL', error: r.error }); return failWith(r.error); }
      return dispatch({ type: 'FIT_RESULT', body: r.data }); // parseFitReveal gate: invalid body -> fit.failed, no number
    },

    async openReport() {
      if (state.phase !== 'fit.done') return state;
      const r = await call('POST', 'report', { spec: state.spec, fit: state.fit });
      if (r.error) return failWith(r.error);
      if (typeof r.data?.html !== 'string' || !r.data.html) return failWith({ code: 'PROCESSING_FAILED', message: 'Report response failed validation.' });
      patch({ report: { status: r.data.status ?? null, html: r.data.html } });
      return dispatch({ type: 'REPORT_OPEN' });
    },
  };
}
