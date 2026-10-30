// S15f: run / pause / seeded-replay controls. Pure model + view-model; no DOM, timers, React or simulator imports.
// Simulator contract (Build/simulator/replay.mjs, s10-replay-v1): runner(parameters, seed, version) -> dense trace; the record binds
// seed+parameters+trace by SHA-256. Seed is replay IDENTITY, not trajectory randomization. The trace is computed once up front, so
// pause/resume only move a playback cursor and can never change the trace. The simulator API is injected (createReplayRecord, replayRecord).
// Host loop: dispatch every event to reduceLogged (S15c) AND reduceRun; run a timer that sends R_TICK; send completionEvent() when non-null.
export const RUN_VERSION = 's10-replay-v1';
export const initialRun = () => ({ record: null, cursor: 0, replay: null });
const CLEARS = ['RUN_START', 'RUN_CANCEL', 'EDIT_SPEC', 'RESET'];
const hasRecord = (state, m) => state.run && m.record && m.record.seed === state.run.seed;

// Runs the injected runner once and returns the frozen replay record. Throws (host sends RUN_FAIL) on runner/record errors.
export async function prepareRun({ createReplayRecord, runner, parameters, seed }) {
  return createReplayRecord({ seed, version: RUN_VERSION, parameters, trace: runner(structuredClone(parameters), seed, RUN_VERSION) });
}

// Re-executes the runner against the record. Never throws: a tampered record or differing output is a visible 'mismatch'.
export async function verifyReplay({ replayRecord, record, runner }) {
  try { const r = await replayRecord(record, runner); return { status: 'verified', replayHash: r.replayHash, traceHash: r.traceHash }; }
  catch (e) { return { status: 'mismatch', message: String(e?.message ?? e).slice(0, 160) }; }
}

// Playback model. Unchanged state returns the SAME reference (ticks while paused/idle are no-ops).
export function reduceRun(m, event, state) {
  const t = event?.type;
  if (CLEARS.includes(t)) return m.record || m.cursor || m.replay ? initialRun() : m;
  if (t === 'R_LOAD') return state.phase === 'run.running' && event.record?.seed === state.run?.seed && Array.isArray(event.record.trace)
    ? { record: event.record, cursor: 0, replay: null } : m;
  if (t === 'R_TICK') return state.phase === 'run.running' && hasRecord(state, m) && m.cursor < m.record.trace.length ? { ...m, cursor: m.cursor + 1 } : m;
  if (t === 'R_REPLAY_START') return state.phase === 'run.done' && hasRecord(state, m) && m.replay?.status !== 'checking' ? { ...m, replay: { status: 'checking' } } : m;
  if (t === 'R_REPLAY_RESULT') return m.replay?.status === 'checking' && ['verified', 'mismatch'].includes(event.result?.status) ? { ...m, replay: event.result } : m;
  return m;
}

// RUN_COMPLETE only after the whole trace was played while running; observations are the simulator trace verbatim.
export const completionEvent = (state, m) =>
  state.phase === 'run.running' && hasRecord(state, m) && m.cursor >= m.record.trace.length
    ? { type: 'RUN_COMPLETE', seed: m.record.seed, observations: m.record.trace } : null;

const STATUS = { 'run.ready': 'Ready to run.', 'run.running': 'Playing simulated run.', 'run.paused': 'Paused. Playback is frozen; the trace is unchanged.',
  'run.done': 'Run finished (simulated).', 'run.failed': 'Run failed.' };
const REPLAY = { checking: 'Replaying with the same seed...', verified: 'Replay matched: identical trace and hashes.',
  mismatch: 'Replay did NOT match the recorded run.' };
const short = (h) => (typeof h === 'string' ? h.slice(0, 12) : null);
// S15s: forward step after a finished run/fit; reuses the existing graph edges run.done -FIT_START-> and fit.done -REPORT_OPEN->.
const NEXT = { 'run.done': { event: 'FIT_START', label: 'Fit' }, 'fit.done': { event: 'REPORT_OPEN', label: 'Open report' } };

export function runView(state, m) {
  const p = state.phase, rec = hasRecord(state, m) ? m.record : null, total = rec?.trace.length ?? 0;
  const live = ['run.running', 'run.paused', 'run.done'].includes(p) && rec;
  const n = Math.min(m.cursor, total);
  return {
    show: p.startsWith('run.'), phase: p, status: STATUS[p] ?? '',
    canRun: ['run.ready', 'run.done', 'run.failed'].includes(p), runLabel: p === 'run.ready' ? 'Run' : 'Run again',
    canPause: p === 'run.running', canResume: p === 'run.paused', canCancel: p === 'run.running' || p === 'run.paused',
    canReplay: p === 'run.done' && !!rec && m.replay?.status !== 'checking',
    seed: state.run?.seed ?? null,
    progress: live ? { frame: n, total } : null,
    frame: live && n > 0 ? rec.trace[n - 1] : null,
    traceHash: short(rec?.traceHash), replayHash: short(rec?.replayHash),
    replay: m.replay ? { status: m.replay.status, text: m.replay.message ? REPLAY[m.replay.status] + ' ' + m.replay.message : REPLAY[m.replay.status] } : null,
    label: 'simulated',
    next: NEXT[p] ?? null,
  };
}
