import { randomUUID } from 'node:crypto';
import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { resolve, sep } from 'node:path';
import { StringDecoder } from 'node:string_decoder';
import { createTrustedFitterHandoff, createMysteryGSession } from '../simulator/mystery-g.mjs';
import { stableHash } from '../simulator/replay.mjs';
// Resolve from the local launch directory; bundlers treat import.meta URLs as assets.
function localRoot() {
  const root = [process.cwd(), resolve(process.cwd(), '../..')].find((candidate) =>
    existsSync(resolve(candidate, 'Build/lab/session-bridge.py')));
  if (!root) throw new Error('local_lab_root_not_found');
  return root + sep;
}
const TTL_MS = 10 * 60 * 1000, MAX_SESSIONS = 64, MAX_BODY = 1_000_000, MAX_SAMPLES = 2000;
const templates = new Set(['free_fall', 'projectile', 'ramp', 'pendulum']); const sessions = new Map(); let activeBridges = 0;
const fail = (code) => ({ status: 'error', error: { code } });
const cleanObs = (v) => Array.isArray(v) && v.length > 0 && v.length <= MAX_SAMPLES && v.every((x) => x && Object.keys(x).length === 2 && Number.isFinite(x.time_s) && Number.isFinite(x.position_m));
// Only the fixed local Python bridge produces setups; these labels are checks, not producer authentication.
// shortcut: normal seed 42/g 9.81 are fixed; revisit only for an approved normal-setup editor.
function normalBrowserSetup(dto, template) {
  const artifact = dto?.validatedSetup, spec = artifact?.spec, scene = artifact?.scene;
  const duration = spec?.simulation?.duration?.value, dt = spec?.simulation?.time_step?.value;
  const steps = duration / dt, nearest = Math.round(steps);
  return dto?.mode === 'normal' && Object.keys(dto).length === 2 &&
    artifact?.artifact_version === 's10-validated-setup-v1' && artifact.validation === 'validate_setup' &&
    artifact.producer === 'contracts/experiment/validate_experiment.py' && Object.keys(artifact).length === 5 &&
    spec?.template === template && scene?.synthetic === true && scene.provenance?.method === 'synthetic' &&
    spec.scene?.scene_id === scene.id && spec.scene?.schema_version === scene.schema_version &&
    spec.simulation.seed === 42 && spec.environment?.gravity?.source?.label === 'synthetic' &&
    spec.environment.gravity.value === 9.81 && scene.gravity?.magnitude_m_s2 === 9.81 &&
    Number.isFinite(duration) && duration >= 0 && Number.isFinite(dt) && dt > 0 &&
    Number.isSafeInteger(nearest) && nearest >= 0 && nearest < MAX_SAMPLES &&
    Math.abs(steps - nearest) <= Number.EPSILON * Math.max(1, Math.abs(steps));
}
function expireOnly() { const now = Date.now(); for (const [id, s] of sessions) if (s.expiresAt <= now) sessions.delete(id); }
function insert(s) { expireOnly(); while (sessions.size >= MAX_SESSIONS) sessions.delete(sessions.keys().next().value); sessions.set(s.id, s); }
function assertCurrent(session, signal) {
  if (signal?.aborted) throw new Error('aborted');
  if (sessions.get(session.id) !== session) throw new Error('session_not_found_or_expired');
  if (Date.now() >= session.expiresAt) throw new Error('session_expired_during_fit');
}
function bridge(request, signal) { return new Promise((resolve, reject) => {
  if (signal?.aborted) return reject(new Error('aborted')); const ROOT = localRoot(); if (activeBridges >= 4) return reject(new Error('lab_busy'));
  const child = spawn(process.env.PYTHON || 'python', [ROOT + 'Build/lab/session-bridge.py'], { cwd: ROOT, detached: process.platform !== 'win32', windowsHide: true, env: { PATH: process.env.PATH || '', SystemRoot: process.env.SystemRoot || '', PYTHONPATH: ROOT, PYTHONIOENCODING: 'utf-8' }, stdio: ['pipe', 'pipe', 'ignore'] });
  activeBridges += 1;
  const stopTree = () => {
    if (!child.pid) return;
    if (process.platform === 'win32') {
      const killer = spawn('taskkill', ['/PID', String(child.pid), '/T', '/F'], { windowsHide: true, stdio: 'ignore' });
      killer.on('error', () => child.kill());
      killer.on('exit', (code) => { if (code) child.kill(); });
    } else { try { process.kill(-child.pid, 'SIGKILL'); } catch { child.kill(); } }
  };
  const decoder = new StringDecoder('utf8');
  let out = '', outBytes = 0, settled = false, stopped = false;
  const abort = () => { stopped = true; stopTree(); }; const timer = setTimeout(abort, 30000);
  const finish = (fn, value) => { if (settled) return; settled = true; activeBridges -= 1; clearTimeout(timer); signal?.removeEventListener('abort', abort); fn(value); };
  signal?.addEventListener('abort', abort, { once: true }); if (signal?.aborted) abort(); child.stdin.on('error', abort); child.stdout.on('data', (b) => { if (stopped) return; outBytes += b.length; if (outBytes > MAX_BODY) return abort(); out += decoder.write(b); });
  // Keep the slot until close; an I/O error alone does not prove process exit.
  child.on('error', () => { stopped = true; }); child.on('close', (code) => { if (stopped || code !== 0 || outBytes > MAX_BODY) return finish(reject, new Error('bridge_failed')); try { finish(resolve, JSON.parse(out + decoder.end())); } catch { finish(reject, new Error('bridge_invalid_response')); } }); child.stdin.end(JSON.stringify(request));
}); }
// Production web containers ship no Python: the API service runs the same session-bridge.py behind the internal token.
async function remoteBridge(request, signal) {
  const base = process.env.WORKSPACE_API_URL, token = process.env.WORKSPACE_INTERNAL_TOKEN;
  if (!base || !token) throw new Error('lab_unavailable');
  if (activeBridges >= 4) throw new Error('lab_busy');
  activeBridges += 1;
  try {
    const timeout = AbortSignal.timeout(30000), stop = signal ? AbortSignal.any([signal, timeout]) : timeout;
    const response = await fetch(base.replace(/\/+$/, '') + '/internal/lab/bridge', { method: 'POST', headers: { 'content-type': 'application/json', 'x-workspace-token': token }, body: JSON.stringify(request), cache: 'no-store', redirect: 'manual', signal: stop });
    const text = await response.text();
    if (!response.ok || text.length > MAX_BODY) throw new Error('bridge_failed');
    return JSON.parse(text);
  } finally { activeBridges -= 1; }
}
const callBridge = (request, signal) => (process.env.NODE_ENV === 'production' ? remoteBridge : bridge)(request, signal);
export async function handleLab(request, { signal } = {}) {
  try {
    if (signal?.aborted) return fail('lab_request_failed');
    if (!request || typeof request !== 'object' || Array.isArray(request) || typeof request.action !== 'string') return fail('invalid_request'); expireOnly();
    if (request.action === 'start') {
      if (Object.keys(request).some((k) => !['action', 'template', 'mystery'].includes(k)) || !templates.has(request.template) || typeof request.mystery !== 'boolean') return fail('invalid_start_request');
      if (request.mystery && !['free_fall', 'projectile'].includes(request.template)) return fail('mystery_supported_for_ballistic_templates_only');
      const result = await callBridge({ action: 'start', template: request.template, mystery: request.mystery }, signal); if (result.status !== 'ok' || !cleanObs(result.observations)) return fail('lab_start_failed');
      if (!request.mystery && (result.source !== 'simulated' || !normalBrowserSetup(result.browserSimulation, request.template))) return fail('lab_start_failed');
      const id = randomUUID(), observationHash = await stableHash(result.observations), session = { id, template: request.template, mystery: request.mystery, observations: result.observations, observationHash, private: result.private, expiresAt: Date.now() + TTL_MS };
      if (request.mystery) session.mysterySession = await createMysteryGSession({ seed: result.private.seed, gravity_m_s2: result.private.gravity_m_s2, privateSetup: result.private.setup, observations: result.observations });
      if (signal?.aborted) return fail('lab_request_failed');
      insert(session); const response = { status: 'ok', sessionId: id, template: request.template, mode: request.mystery ? 'mystery-g' : 'normal', observations: result.observations, observationHash, source: 'simulated', units: { time: 's', position: 'm' }, limitations: result.limitations };
      if (!request.mystery) {
        response.browserSimulation = result.browserSimulation;
        if (result.gravity) response.gravity = result.gravity;
      }
      return response;
    }
    if (request.action === 'fit') {
      if (Object.keys(request).some((k) => !['action', 'sessionId'].includes(k)) || typeof request.sessionId !== 'string') return fail('invalid_fit_request');
      const session = sessions.get(request.sessionId); if (!session || session.expiresAt <= Date.now()) return fail('session_not_found_or_expired'); if (!['free_fall', 'projectile'].includes(session.template)) return fail('fit_supported_for_ballistic_templates_only'); if (session.result) return session.result;
      if (!session.inFlightPromise) session.inFlightPromise = (async () => {
        const fit = await callBridge({ action: 'fit', observations: session.observations }, signal);
        assertCurrent(session, signal);
        if (fit.status !== 'ok' || !fit.gravity) return fail('fit_unavailable');
        const handoff = await createTrustedFitterHandoff(fit, session.observations);
        assertCurrent(session, signal);
        const reveal = session.mysterySession ? session.mysterySession.revealFit(handoff).reveal : { gravity: fit.gravity.value, uncertainty: fit.gravity.uncertainty, unit: fit.gravity.unit, source: 'simulated', fitStatus: 'ok' };
        session.result = { status: 'ok', sessionId: session.id, fit, reveal }; return session.result;
      })();
      try { const result = await session.inFlightPromise; return signal?.aborted ? fail('lab_request_failed') : result; } finally { if (!session.result) session.inFlightPromise = null; }
    }
    return fail('unsupported_action');
  } catch (e) { return fail(['session_not_found_or_expired', 'fit_supported_for_ballistic_templates_only', 'session_expired_during_fit'].includes(e?.message) ? e.message : 'lab_request_failed'); }
}
export const _sessionTest = { sessions, expireOnly, getActiveBridges: () => activeBridges };
