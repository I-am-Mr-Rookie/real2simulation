import { randomUUID } from 'node:crypto';
import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { resolve, sep } from 'node:path';
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
function expireOnly() { const now = Date.now(); for (const [id, s] of sessions) if (s.expiresAt <= now) sessions.delete(id); }
function insert(s) { expireOnly(); while (sessions.size >= MAX_SESSIONS) sessions.delete(sessions.keys().next().value); sessions.set(s.id, s); }
function bridge(request, signal) { return new Promise((resolve, reject) => {
  if (signal?.aborted) return reject(new Error('aborted')); const ROOT = localRoot(); if (activeBridges >= 4) return reject(new Error('lab_busy')); activeBridges += 1;
  const child = spawn(process.env.PYTHON || 'python', [ROOT + 'Build/lab/session-bridge.py'], { cwd: ROOT, detached: process.platform !== 'win32', windowsHide: true, env: { PATH: process.env.PATH || '', SystemRoot: process.env.SystemRoot || '', PYTHONPATH: ROOT, PYTHONIOENCODING: 'utf-8' }, stdio: ['pipe', 'pipe', 'ignore'] });
  const stopTree = () => {
    if (!child.pid) return;
    if (process.platform === 'win32') {
      const killer = spawn('taskkill', ['/PID', String(child.pid), '/T', '/F'], { windowsHide: true, stdio: 'ignore' });
      killer.on('error', () => child.kill());
      killer.on('exit', (code) => { if (code) child.kill(); });
    } else { try { process.kill(-child.pid, 'SIGKILL'); } catch { child.kill(); } }
  };
  let out = '', settled = false; const abort = stopTree; const timer = setTimeout(stopTree, 30000);
  const finish = (fn, value) => { if (settled) return; settled = true; activeBridges -= 1; clearTimeout(timer); signal?.removeEventListener('abort', abort); fn(value); };
  signal?.addEventListener('abort', abort, { once: true }); if (signal?.aborted) abort(); child.stdin.on('error', () => { stopTree(); finish(reject, new Error('bridge_stdin_failed')); }); child.stdout.on('data', (b) => { out += b; if (out.length > MAX_BODY) stopTree(); });
  child.on('error', (e) => finish(reject, e)); child.on('close', (code) => { if (code !== 0 || out.length > MAX_BODY) return finish(reject, new Error('bridge_failed')); try { finish(resolve, JSON.parse(out)); } catch { finish(reject, new Error('bridge_invalid_response')); } }); child.stdin.end(JSON.stringify(request));
}); }
export async function handleLab(request, { signal } = {}) {
  try {
    if (!request || typeof request !== 'object' || Array.isArray(request) || typeof request.action !== 'string') return fail('invalid_request'); expireOnly();
    if (request.action === 'start') {
      if (Object.keys(request).some((k) => !['action', 'template', 'mystery'].includes(k)) || !templates.has(request.template) || typeof request.mystery !== 'boolean') return fail('invalid_start_request');
      if (request.mystery && !['free_fall', 'projectile'].includes(request.template)) return fail('mystery_supported_for_ballistic_templates_only');
      const result = await bridge({ action: 'start', template: request.template, mystery: request.mystery }, signal); if (result.status !== 'ok' || !cleanObs(result.observations)) return fail('lab_start_failed');
      const id = randomUUID(), observationHash = await stableHash(result.observations), session = { id, template: request.template, mystery: request.mystery, observations: result.observations, observationHash, private: result.private, expiresAt: Date.now() + TTL_MS };
      if (request.mystery) session.mysterySession = await createMysteryGSession({ seed: result.private.seed, gravity_m_s2: result.private.gravity_m_s2, privateSetup: result.private.setup, observations: result.observations });
      insert(session); const response = { status: 'ok', sessionId: id, template: request.template, mode: request.mystery ? 'mystery-g' : 'normal', observations: result.observations, observationHash, source: 'simulated', units: { time: 's', position: 'm' }, limitations: result.limitations }; if (!request.mystery && result.gravity) response.gravity = result.gravity; return response;
    }
    if (request.action === 'fit') {
      if (Object.keys(request).some((k) => !['action', 'sessionId'].includes(k)) || typeof request.sessionId !== 'string') return fail('invalid_fit_request');
      const session = sessions.get(request.sessionId); if (!session || session.expiresAt <= Date.now()) return fail('session_not_found_or_expired'); if (!['free_fall', 'projectile'].includes(session.template)) return fail('fit_supported_for_ballistic_templates_only'); if (session.result) return session.result;
      if (!session.inFlightPromise) session.inFlightPromise = (async () => { const fit = await bridge({ action: 'fit', observations: session.observations }, signal); if (Date.now() >= session.expiresAt) return fail('session_expired_during_fit'); if (fit.status !== 'ok' || !fit.gravity) return fail('fit_unavailable'); const handoff = await createTrustedFitterHandoff(fit, session.observations); const reveal = session.mysterySession ? session.mysterySession.revealFit(handoff).reveal : { gravity: fit.gravity.value, uncertainty: fit.gravity.uncertainty, unit: fit.gravity.unit, source: 'simulated', fitStatus: 'ok' }; session.result = { status: 'ok', sessionId: session.id, fit, reveal }; return session.result; })();
      try { return await session.inFlightPromise; } finally { if (!session.result) session.inFlightPromise = null; }
    }
    return fail('unsupported_action');
  } catch (e) { return fail(['session_not_found_or_expired', 'fit_supported_for_ballistic_templates_only', 'session_expired_during_fit'].includes(e?.message) ? e.message : 'lab_request_failed'); }
}
export const _sessionTest = { sessions, expireOnly, getActiveBridges: () => activeBridges };
