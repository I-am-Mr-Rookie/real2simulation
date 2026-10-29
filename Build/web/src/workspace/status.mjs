// S15c: upload status + failure surfaces. Pure functions over S15a state; no DOM/React/viewer imports.
// - reduceLogged: wraps the S15a reducer and keeps a bounded, visible job-stage event log (applied AND ignored events).
// - statusSurface: upload job timeline, failure/cancel guidance, retry action, partial-state (kept/lost) messaging.
// Retry reuses existing graph edges only (UPLOAD_STARTED / RUN_START / FIT_START); this module never mutates state itself.
import { reduce, initialState, availableEvents } from './workflow.mjs';

export const LOG_MAX = 50;
const JOB_STATUS = ['queued', 'running', 'ready', 'failed', 'cancelled'];

export const initialLogged = () => ({ state: initialState(), log: [], seq: 0 });

// Entry fields come from the event TYPE and from state transitions, never from raw payload text (job status is allow-listed).
export function reduceLogged(m, event, deps = {}) {
  const state = reduce(m.state, event, deps);
  const applied = state !== m.state;
  const s = event?.job?.status;
  const entry = { seq: m.seq + 1, type: typeof event?.type === 'string' ? event.type.slice(0, 32) : 'UNKNOWN', outcome: applied ? 'applied' : 'ignored',
    from: m.state.phase, to: state.phase, jobStatus: JOB_STATUS.includes(s) ? s : null,
    revision: Number.isInteger(event?.job?.revision) ? event.job.revision : null };
  return { state, seq: entry.seq, log: [...m.log, entry].slice(-LOG_MAX) };
}

export const eventText = (e) => {
  const what = e.type === 'JOB_UPDATE' && e.jobStatus ? 'Job update' + (e.revision !== null ? ' r' + e.revision : '') + ': ' + e.jobStatus : e.type;
  return '#' + e.seq + ' ' + what + (e.outcome === 'applied' ? (e.from !== e.to ? ' (' + e.from + ' -> ' + e.to + ')' : '') : ' (ignored: stale or not allowed now)');
};

const STEPS = [['queued', 'Queued'], ['running', 'Processing'], ['ready', 'Scene ready']];
const sinceStart = (log) => { const i = log.map((e) => e.type === 'UPLOAD_STARTED' && e.outcome === 'applied').lastIndexOf(true); return i < 0 ? log : log.slice(i); };

// Upload job timeline. Only phases that belong to the upload job; failed/cancelled adds a terminal marker after the furthest step reached.
export function jobTimeline(state, log = []) {
  const p = state.phase, stage = p.split('.')[0];
  if (p === 'upload.idle') return [];
  const terminal = p === 'upload.failed' || p === 'upload.cancelled';
  let level = p === 'upload.queued' ? 0 : p === 'upload.running' ? 1 : terminal ? 0 : 2;
  if (terminal && sinceStart(log).some((e) => e.outcome === 'applied' && e.jobStatus === 'running')) level = 1;
  const steps = STEPS.map(([id, label], i) => ({ id, label, status: terminal ? (i <= level ? 'done' : 'todo') : i < level || stage !== 'upload' ? 'done' : i === level ? 'current' : 'todo' }));
  return terminal ? [...steps.filter((s) => s.status === 'done'), { id: p.split('.')[1], label: p === 'upload.failed' ? 'Failed' : 'Cancelled', status: 'failed' }] : steps;
}

// retry blocked by cause: more attempts cannot help until the user/owner changes something.
const BLOCKED = { SPEND_PAUSED: 'Processing is paused by a spend limit. Retrying will not help until it is lifted.', UNAUTHORIZED: 'You are not signed in or not allowed. Sign in, then start again.' };
const ADVICE = {
  INVALID_INPUT: 'The input was rejected. Choose a different file or change the input before retrying.',
  NOT_FOUND: 'The job or scene no longer exists. Start a new upload.',
  DEPENDENCY_UNAVAILABLE: 'A required service is unavailable. Retrying later may work.',
  PROCESSING_FAILED: 'Processing failed. A retry starts fresh; it may fail again.',
};
const RETRY = { upload: ['UPLOAD_STARTED', 'Start a new upload'], run: ['RUN_START', 'Run again'], fit: ['FIT_START', 'Retry fit'] };

// Partial state: say exactly what still exists and what does not (derived from state, not assumed).
export function partialState(state) {
  const kept = [], lost = [];
  const f = state.phase.split('.')[0];
  (state.scene ? kept : lost).push(state.scene ? 'Scene (viewport stays available)' : 'Scene: none was created, nothing to view');
  if (f !== 'upload') {
    if (state.spec) kept.push('Interview spec');
    if (state.run?.observations) kept.push('Run observations (simulated)'); else if (f === 'run' || f === 'fit') lost.push('Run result: none stored');
    if (f === 'fit' || f === 'report') lost.push('Fit value: none shown (no number without a validated fit)');
  }
  return { kept, lost };
}

export function failureSurface(state) {
  const m = /^(upload|run|fit)\.(failed|cancelled)$/.exec(state.phase);
  if (!m) return null;
  const [, stage, kind] = m, code = state.error?.code ?? null;
  const blocked = kind === 'failed' ? BLOCKED[code] ?? null : null;
  const [event, label] = RETRY[stage];
  const retry = !blocked && availableEvents(state).includes(event) ? { event, label: kind === 'cancelled' ? 'Start a new upload' : label } : null;
  return { stage, kind, code, title: kind === 'cancelled' ? 'Upload cancelled' : stage[0].toUpperCase() + stage.slice(1) + ' failed',
    advice: kind === 'cancelled' ? 'The job was cancelled before a scene was produced.' : blocked ?? ADVICE[code] ?? 'Something went wrong.',
    retry, ...partialState(state) };
}

const IN_FLIGHT = { 'upload.queued': 'Waiting for a worker. No scene yet; the viewport stays empty.', 'upload.running': 'Processing your upload. No scene yet; the viewport stays empty until it is ready.' };

export function statusSurface(state, log = []) {
  return { timeline: jobTimeline(state, log), events: sinceStart(log).slice(-8).map(eventText), allEvents: log.length, inFlight: IN_FLIGHT[state.phase] ?? null, failure: failureSurface(state) };
}
