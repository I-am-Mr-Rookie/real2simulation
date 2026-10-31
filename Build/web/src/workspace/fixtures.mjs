// VISIBLY SYNTHETIC fixtures for S15a tests/UI states only. Values are inert structural placeholders
// (deliberately non-physical), NOT fitter/simulator output and NOT gate, real-scene or physical evidence.
export const SYNTHETIC_NOTICE = 'SYNTHETIC fixture: not reconstruction, fit or physics evidence';
const scene = { scene_id: 'synthetic-room-v1', scene_version: '1.0.0', access: 'private', evidence: 'synthetic' };
export const job = (revision, status, extra = {}) => ({ contract_version: '1.0.0', kind: 'job', job_id: 'synthetic-job-v1', revision, status, result: null, error: null, ...extra });
export const jobReady = (revision) => job(revision, 'ready', { result: scene });
export const jobFailed = (revision) => job(revision, 'failed', { error: { code: 'PROCESSING_FAILED', message: 'SYNTHETIC failure fixture' } });
export const validSpec = { synthetic: true, template: 'free-fall' };
export const deps = { validateSpec: (s) => (s?.synthetic === true ? { ok: true } : { ok: false, errors: ['SYNTHETIC validator: spec rejected'] }) };
export const observations = [{ time_s: 0, position_m: 0 }, { time_s: 1, position_m: 1 }, { time_s: 2, position_m: 4 }];
// S15f: deterministic fixture runner (replay contract: runner(parameters, seed, version) -> trace; seed is identity only).
// Deliberately non-physical (a = 2 m/s^2 stand-in, dyadic values so the trace is exact); NOT simulator output or physics evidence.
export const runParameters = { synthetic: true, template: 'free-fall', steps: 8, accel: 2 };
export const fixtureRunner = (p) => Array.from({ length: p.steps }, (_, i) => ({ time_s: (i + 1) / 4, position_m: 0.5 * p.accel * ((i + 1) / 4) ** 2 }));
export const fitBody = (sessionId) => ({ status: 'ok', sessionId, fit: { status: 'ok',
  gravity: { value: 1.25, uncertainty: 0.5, unit: 'm/s^2', source: { label: 'simulated', evidence: SYNTHETIC_NOTICE } },
  uncertainty: { model: 'SYNTHETIC placeholder model', assumptions: ['SYNTHETIC'] } } });

