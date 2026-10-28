import { randomUUID, createHash } from 'node:crypto';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { createTrustedFitterHandoff, createMysteryGSession } from '../simulator/mystery-g.mjs';
import { stableHash } from '../simulator/replay.mjs';

const ROOT = fileURLToPath(new URL('../../', import.meta.url));
const TTL_MS = 10 * 60 * 1000, MAX_SESSIONS = 64, MAX_BODY = 1_000_000, MAX_SAMPLES = 2000;
const templates = new Set(['free_fall', 'projectile', 'ramp', 'pendulum']);
const sessions = new Map(); let activeBridges = 0;
const fail = (code) => ({ status: 'error', error: { code } });
const cleanObs = (v) => Array.isArray(v) && v.length > 0 && v.length <= MAX_SAMPLES && v.every((x) => x && Object.keys(x).length === 2 && Number.isFinite(x.time_s) && Number.isFinite(x.position_m));
function prune() { const now = Date.now(); for (const [id, s] of sessions) if (s.expiresAt <= now) sessions.delete(id); while (sessions.size >= MAX_SESSIONS) sessions.delete(sessions.keys().next().value); }
function hash(value) { return createHash('sha256').update(JSON.stringify(value)).digest('hex'); }
function bridge(request, signal) { return new Promise((resolve, reject) => { if (activeBridges >= 4) return reject(new Error('lab_busy')); activeBridges += 1; const child = spawn(process.env.PYTHON || 'python', [ROOT + 'Build/lab/session-bridge.py'], { cwd: ROOT, env: { PATH: process.env.PATH || '', SystemRoot: process.env.SystemRoot || '', PYTHONPATH: ROOT, PYTHONIOENCODING: 'utf-8' }, stdio: ['pipe','pipe','ignore'] }); let out = ''; const timer = setTimeout(() => child.kill(), 30000); signal?.addEventListener('abort', () => child.kill(), { once: true }); child.stdout.on('data', (b) => { out += b; if (out.length > MAX_BODY) child.kill(); }); const done = () => { activeBridges -= 1; clearTimeout(timer); }; child.on('error', () => { done(); reject(new Error('bridge_unavailable')); }); child.on('close', (code) => { done(); if (code !== 0 || out.length > MAX_BODY) return reject(new Error('bridge_failed')); try { resolve(JSON.parse(out)); } catch { reject(new Error('bridge_invalid_response')); } }); child.stdin.end(JSON.stringify(request)); }); }
export async function handleLab(request, { signal } = {}) {
  try {
    if (!request || typeof request !== 'object' || Array.isArray(request) || typeof request.action !== 'string') return fail('invalid_request');
    prune();
    if (request.action === 'start') {
      if (Object.keys(request).some((k) => !['action','template','mystery'].includes(k)) || !templates.has(request.template) || typeof request.mystery !== 'boolean') return fail('invalid_start_request');
      const result = await bridge({ action: 'start', template: request.template }, signal);
      if (result.status !== 'ok' || !cleanObs(result.observations)) return fail('lab_start_failed');
      const id = randomUUID(), observationHash = await stableHash(result.observations);
      const session = { id, template: request.template, mystery: request.mystery, observations: result.observations, observationHash, expiresAt: Date.now() + TTL_MS };
      if (request.mystery) session.mysterySession = await createMysteryGSession({ seed: 42, gravity_m_s2: 9.81, privateSetup: { template: request.template, source: 'synthetic' }, observations: result.observations });
      sessions.set(id, session);
      const response = { status: 'ok', sessionId: id, template: request.template, mode: request.mystery ? 'mystery-g' : 'normal', observations: result.observations, observationHash, source: 'simulated', units: { time: 's', position: 'm' }, limitations: result.limitations };
      if (!request.mystery && result.gravity) response.gravity = result.gravity;
      return response;
    }
    if (request.action === 'fit') {
      if (Object.keys(request).some((k) => !['action','sessionId'].includes(k)) || typeof request.sessionId !== 'string') return fail('invalid_fit_request');
      const session = sessions.get(request.sessionId); if (!session || session.expiresAt <= Date.now()) return fail('session_not_found_or_expired');
      if (!['free_fall', 'projectile'].includes(session.template)) return fail('fit_supported_for_ballistic_templates_only');
      if (session.result) return session.result;
      const fit = await bridge({ action: 'fit', observations: session.observations }, signal);
      if (fit.status !== 'ok' || !fit.gravity) return fail('fit_unavailable');
      const handoff = await createTrustedFitterHandoff(fit, session.observations);
      const reveal = session.mysterySession ? session.mysterySession.revealFit(handoff).reveal : { gravity: fit.gravity.value, uncertainty: fit.gravity.uncertainty, unit: fit.gravity.unit, source: 'simulated', fitStatus: 'ok' };
      session.result = { status: 'ok', fit, reveal, session: { sessionId: session.id, template: session.template, mode: session.mystery ? 'mystery-g' : 'normal', observationHash: session.observationHash, source: 'simulated' } };
      return session.result;
    }
    return fail('unsupported_action');
  } catch (e) { return fail(e?.message === 'session_not_found_or_expired' ? e.message : 'lab_request_failed'); }
}
export const _sessionTest = { sessions, prune };
