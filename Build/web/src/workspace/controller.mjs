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
  const base = typeof e?.message === 'string' && e.message ? e.message : typeof e === 'string' && e ? e : `Workspace API ${status || 'unreachable'}`;
  const message = Array.isArray(e?.errors) && e.errors.length ? `${base}: ${e.errors.map(String).join('; ')}` : base; // S15q: say which field failed
  return { code, message: message.slice(0, 240) };
}

// S15q: interview.answers_to_spec takes {question id: {chip: id} | {text: str}} (exactly one key); interviewAnswers() emits
// [{questionId, chipId, text}]. Sending that array verbatim was the live 422. A chosen chip wins over typed text.
export const specAnswers = (list) => Object.fromEntries(list.map((a) => [a.questionId, a.chipId ? { chip: a.chipId } : { text: a.text ?? '' }]));

export async function sha256Hex(bytes) {
  const d = await globalThis.crypto.subtle.digest('SHA-256', bytes);
  return [...new Uint8Array(d)].map((b) => b.toString(16).padStart(2, '0')).join('');
}

const ACTIVE = new Set(['upload.queued', 'upload.running']);

// S15p: browser simulator dep. The API validated_setup is passed verbatim as the NORMAL payload; runBrowserSimulation
// itself rejects anything that is not a trusted S10 validated artifact (missing field -> thrown, honest RUN_FAIL).
// Samples map to the lab's existing observation shape (BrowserSimulation.jsx): world-Y position vs time.
// S15r (Q20=A): an API what-if artifact selects the simulator's explicit labelled what-if mode; the simulator re-checks it.
export const browserSimulate = (runSim) => async (validatedSetup) =>
  runSim({ mode: validatedSetup?.what_if === true ? 'what-if' : 'normal', validatedSetup }).samples.map((s) => ({ time_s: s.time_s, position_m: s.position_m[1] }));

// API /fit (fitter.api.fit_observations) takes quantity lists. Engine samples are exact simulated values: uncertainty 0 is
// their declared sigma, not a measurement; the fitter floors variance with residual RSS.
const EVIDENCE = 'browser RK4 simulator sample (exact simulated value, no measurement uncertainty)';
const q = (value, unit) => ({ value, unit, uncertainty: 0, source: { label: 'simulated', evidence: EVIDENCE } });
// S15t: degree 2 + AIC selection, as the S15 fit fixture; /report renders model_selection and 422s without it.
export const fitRequest = (obs) => ({ times: obs.map((o) => q(o.time_s, 's')), positions: obs.map((o) => q(o.position_m, 'm')), degree: 2, select_model: true });
// Re-envelope the API result for the parseFitReveal gate; numbers are copied by reference, never recomputed.
export const revealBody = (d, sessionId) => (d?.status === 'ok' && d.gravity
  ? { status: 'ok', sessionId, fit: { status: 'ok', gravity: d.gravity, uncertainty: d.uncertainty } } : null);

// deps: fetch (BFF, same-origin cookies), simulate(validatedSetup, seed) -> observations (runBrowserSimulation wrapper),
// sleep(ms), onChange(snapshot). Missing simulate = honest DEPENDENCY_UNAVAILABLE, never fixture output.
export function createController({ fetch: f = globalThis.fetch, base = API_BASE, simulate, sleep = (ms) => new Promise((r) => setTimeout(r, ms)),
  pollMs = 1000, maxPolls = 900, onChange, newSessionId = () => 'fit-' + Date.now().toString(36) } = {}) {
  let state = initialState();
  const meta = { busy: false, upload: null, events: [], questions: null, validatedSetup: null, specLabel: null, whatIfLabel: null, fitRaw: null, fitInput: null, report: null, provenance: null };
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
        if (job?.status === 'no_scene') return dispatch({ type: 'OWNER_CLIP', jobId: job.job_id }); // S15y: nothing to poll
        dispatch({ type: 'UPLOAD_STARTED', jobId: job?.job_id });
        if (state.phase !== 'upload.queued') return failWith({ code: 'PROCESSING_FAILED', message: 'Job response failed validation.' });
        dispatch({ type: 'JOB_UPDATE', job });
        return await poll(job.job_id);
      } finally { patch({ busy: false }); }
    },

    async loadQuestions() {
      if (state.phase !== 'interview.active') return null;
      const r = await call('GET', `scenes/${encodeURIComponent(state.scene?.scene_id ?? state.owner?.jobId ?? '')}/questions`);
      if (r.error) return failWith(r.error);
      patch({ questions: r.data });
      return r.data;
    },

    // The API (S08 validate_setup) is the validator; the reducer accepts only the exact spec object it returned.
    async submitAnswers(answers) {
      if (state.phase !== 'interview.active') return state;
      const body = { answers: Array.isArray(answers) ? specAnswers(answers) : answers };
      const r = await call('POST', `scenes/${encodeURIComponent(state.scene?.scene_id ?? state.owner?.jobId ?? '')}/spec`, body);
      if (r.error) return failWith(r.error);
      const d = r.data;
      if (state.owner && d?.owner_clip === true) { // S15y: result stage = stored g ± u (or abstain) + the declared scale
        // S15az: live_fit = fitter run now on the stored track points with this answer's scale (Gate D D1/D6)
        const measurement = d.measurement && typeof d.measurement === 'object' ? { ...d.measurement, user_scale: d.user_scale ?? null, live_fit: d.live_fit ?? null } : null;
        patch({ provenance: meta.provenance && measurement ? { ...meta.provenance, measurement } : meta.provenance });
        return dispatch({ type: 'OWNER_RESULT', measurement });
      }
      const ok = d?.ok === true && !!d.spec && !!d.validated_setup;
      // S14j: recorded scenes carry a verbatim label (e.g. 'scale unverified, not setup-validated'); shown through run/fit/report.
      // S15v: known-size answer comes back as user_scale (declared or abstain); it travels in the same verbatim label.
      const us = d?.user_scale;
      const scale = us?.status === 'declared' ? 'scale ' + us.object + ' = ' + us.length_m + ' m (' + us.label + ')' : typeof us?.label === 'string' ? us.label : null;
      const label = [[d?.label, d?.validated_setup?.label].find((x) => typeof x === 'string' && x), scale].filter(Boolean).join('; ') || null;
      const whatIfLabel = d?.validated_setup?.what_if === true && typeof d.validated_setup.label === 'string' ? d.validated_setup.label : null;
      if (ok) patch({ validatedSetup: d.validated_setup, specLabel: label, whatIfLabel });
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
      const req = { ...extra, ...fitRequest(state.run.observations) };
      const r = await call('POST', 'fit', req);
      if (r.error) { dispatch({ type: 'FIT_FAIL', error: r.error }); return failWith(r.error); }
      patch({ fitRaw: r.data, fitInput: { times: req.times, output: r.data } }); // fitInput = fit-view parseFit's { times, output }
      return dispatch({ type: 'FIT_RESULT', body: revealBody(r.data, state.fit.sessionId) }); // parseFitReveal gate: invalid -> fit.failed
    },

    async openReport() {
      if (state.phase !== 'fit.done') return state;
      // API needs the raw fitter result; a what-if run passes its label so the report carries it too
      const r = await call('POST', 'report', { spec: state.spec, fit: meta.fitRaw, ...(meta.whatIfLabel ? { label: meta.whatIfLabel } : {}) });
      if (r.error) return failWith(r.error);
      if (typeof r.data?.html !== 'string' || !r.data.html) return failWith({ code: 'PROCESSING_FAILED', message: 'Report response failed validation.' });
      patch({ report: { status: r.data.status ?? null, html: r.data.html, labels: Array.isArray(r.data.labels) ? r.data.labels : [], specLabel: meta.specLabel } });
      return dispatch({ type: 'REPORT_OPEN' });
    },
  };
}
