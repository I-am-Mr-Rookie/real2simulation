// S15a: workspace state graph (upload -> interview -> run -> fit -> report). Pure reducer, no DOM/React.
// Consumes: shell job DTO (integration.schema.json), S11 fit reveal (lab/fit-contract.mjs), injected S08 spec validator.
// Never invents numbers: fit values exist only as parseFitReveal output; observations are stored verbatim, labelled 'simulated'.
import { parseFitReveal } from '../lab/fit-contract.mjs';

const finite = (v) => typeof v === 'number' && Number.isFinite(v);
const ID = /^[a-zA-Z0-9][a-zA-Z0-9_-]{0,95}$/;
const JOB_STATUS = ['queued', 'running', 'ready', 'failed', 'cancelled'];
const ERROR_CODES = ['INVALID_INPUT', 'UNAUTHORIZED', 'NOT_FOUND', 'DEPENDENCY_UNAVAILABLE', 'SPEND_PAUSED', 'PROCESSING_FAILED'];

export const PHASES = [
  'upload.idle', 'upload.queued', 'upload.running', 'upload.failed', 'upload.cancelled',
  'interview.active',
  'run.ready', 'run.running', 'run.paused', 'run.done', 'run.failed',
  'fit.running', 'fit.done', 'fit.failed',
  'report.open',
];

// The graph: phase -> event -> handler. Missing entry = illegal transition (state returned unchanged, same reference).
const G = {};
const edge = (phases, event, fn) => { for (const p of phases) (G[p] ??= {})[event] = fn; };

export const initialState = () => ({ phase: 'upload.idle', job: null, scene: null, spec: null, run: null, fit: null, error: null });
const to = (s, phase, patch = {}) => ({ ...s, error: null, ...patch, phase });
const fail = (s, phase, code, message) => ({ ...s, phase, error: { code, message: String(message).slice(0, 240) } });

export function parseJob(j) {
  const closed = (o, n) => Object.keys(o).length === n; // schema is additionalProperties:false; required keys are checked below
  const sceneOk = (x) => x && x.scene_version === '1.0.0' && ID.test(x.scene_id ?? '') &&
    ['public-library', 'private'].includes(x.access) && ['synthetic', 'reconstructed'].includes(x.evidence) && closed(x, 4);
  const errOk = (e) => e && ERROR_CODES.includes(e.code) && typeof e.message === 'string' && e.message.length >= 1 && e.message.length <= 240 && closed(e, 2);
  if (!j || !closed(j, 7) || j.contract_version !== '1.0.0' || j.kind !== 'job' || !ID.test(j.job_id ?? '') || !Number.isInteger(j.revision) ||
      j.revision < 0 || !JOB_STATUS.includes(j.status)) return null;
  const ready = j.status === 'ready', failed = j.status === 'failed';
  if (ready ? !sceneOk(j.result) : j.result !== null) return null;
  if (failed ? !errOk(j.error) : j.error !== null) return null;
  return j;
}

// upload: a new job id per attempt; terminal jobs never transition; stale/equal revisions ignored.
edge(['upload.idle', 'upload.failed', 'upload.cancelled'], 'UPLOAD_STARTED', (s, { jobId }) =>
  ID.test(jobId ?? '') ? to(s, 'upload.queued', { job: { id: jobId, revision: -1 }, scene: null }) : null);
edge(['upload.queued', 'upload.running'], 'JOB_UPDATE', (s, { job }) => {
  const j = parseJob(job);
  if (!j || j.job_id !== s.job.id || j.revision <= s.job.revision) return null;
  if (j.status === 'queued' && s.phase === 'upload.running') return null;
  const next = { ...s, job: { id: j.job_id, revision: j.revision } };
  if (j.status === 'ready') return to(next, 'interview.active', { scene: j.result }); // ready = artifact, not accuracy/gate
  if (j.status === 'failed') return fail(next, 'upload.failed', j.error.code, j.error.message);
  return to(next, `upload.${j.status}`);
});

// interview: spec accepted only if the injected S08 validator says ok.
edge(['interview.active'], 'INTERVIEW_SPEC', (s, { spec }, deps) => {
  const v = deps.validateSpec?.(spec);
  if (!v?.ok) return fail(s, 'interview.active', 'INVALID_INPUT', (v?.errors ?? ['spec rejected']).join('; '));
  return to(s, 'run.ready', { spec });
});

// run: seeded trials; completion must match the seed; mystery-g keys are rejected before a fit exists.
edge(['run.ready', 'run.done', 'run.failed'], 'RUN_START', (s, { seed }) =>
  Number.isSafeInteger(seed) ? to(s, 'run.running', { run: { seed, observations: null }, fit: null }) : null);
edge(['run.running'], 'RUN_PAUSE', (s) => to(s, 'run.paused'));
edge(['run.paused'], 'RUN_RESUME', (s) => to(s, 'run.running'));
edge(['run.running', 'run.paused'], 'RUN_CANCEL', (s) => to(s, 'run.ready', { run: null }));
const leaks = (v) => v && typeof v === 'object' && Object.entries(v).some(([k, x]) => /gravity|hidden_?g|mystery/i.test(k) || leaks(x));
edge(['run.running'], 'RUN_COMPLETE', (s, { seed, observations }) => {
  if (seed !== s.run.seed) return null;
  const ok = Array.isArray(observations) && observations.length > 0 && observations.every((o) => finite(o?.time_s) && finite(o?.position_m));
  if (!ok || leaks(observations)) return fail(s, 'run.failed', 'PROCESSING_FAILED', 'Run output rejected: malformed or reveals hidden physics.');
  return to(s, 'run.done', { run: { seed, observations, label: 'simulated' } });
});
edge(['run.running', 'run.paused'], 'RUN_FAIL', (s, { error }) => fail(s, 'run.failed', 'PROCESSING_FAILED', error?.message ?? 'Run failed.'));

// fit: numbers exist only via parseFitReveal for the expected session.
edge(['run.done', 'fit.failed'], 'FIT_START', (s, { sessionId }) =>
  ID.test(sessionId ?? '') ? to(s, 'fit.running', { fit: { sessionId } }) : null);
edge(['fit.running'], 'FIT_CANCEL', (s) => to(s, 'run.done', { fit: null }));
edge(['fit.running'], 'FIT_RESULT', (s, { body }) => {
  const f = parseFitReveal(body, s.fit.sessionId);
  return f ? to(s, 'fit.done', { fit: { sessionId: s.fit.sessionId, ...f } }) : fail({ ...s, fit: null }, 'fit.failed', 'PROCESSING_FAILED', 'Fit response failed validation; no value shown.');
});
edge(['fit.running'], 'FIT_FAIL', (s, { error }) => fail({ ...s, fit: null }, 'fit.failed', 'PROCESSING_FAILED', error?.message ?? 'Fit failed.'));

// report
edge(['fit.done'], 'REPORT_OPEN', (s) => to(s, 'report.open'));
edge(['report.open'], 'REPORT_CLOSE', (s) => to(s, 'fit.done'));

// editing the spec invalidates every downstream result; RESET abandons the scene (never cancels a server job).
edge(['run.ready', 'run.done', 'run.failed', 'fit.done', 'fit.failed', 'report.open'], 'EDIT_SPEC', (s) => to(s, 'interview.active', { spec: null, run: null, fit: null }));
for (const p of PHASES) edge([p], 'RESET', () => initialState());

export const EVENTS = [...new Set(Object.values(G).flatMap(Object.keys))];
export const availableEvents = (state) => Object.keys(G[state.phase] ?? {});
export const stageOf = (state) => state.phase.split('.')[0];

// deps: { validateSpec(spec) -> { ok, errors? } } (S08 validator, injected; missing = fail closed)
export function reduce(state, event, deps = {}) {
  const h = G[state.phase]?.[event?.type];
  return (h && h(state, event, deps)) || state;
}

