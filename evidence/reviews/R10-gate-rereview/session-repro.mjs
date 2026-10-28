// R10-gate-rereview: real-process session guard repros (no mocks).
import { handleLab, _sessionTest } from '../../../Build/lab/session-service.mjs';
const log = (o) => console.log(JSON.stringify(o));
process.env.PYTHON = 'definitely-missing-python-r10';
const missing = await Promise.all([0, 1, 2, 3, 4, 5].map(() => handleLab({ action: 'start', template: 'free_fall', mystery: true })));
log({ name: 'real async ENOENT x6', codes: missing.map((x) => x.error?.code), activeAfter: _sessionTest.getActiveBridges(), sessions: _sessionTest.sessions.size });
delete process.env.PYTHON;
const s = await handleLab({ action: 'start', template: 'free_fall', mystery: true });
log({ name: 'mystery start redacted', status: s.status, leaksPrivate: /gravity|seed|setup/.test(JSON.stringify(s)) });
const ac = new AbortController(); const p = handleLab({ action: 'fit', sessionId: s.sessionId }, { signal: ac.signal }); setTimeout(() => ac.abort(), 50);
log({ name: 'real abort during fit', result: (await p).error?.code, cached: Boolean(_sessionTest.sessions.get(s.sessionId).result), activeAfter: _sessionTest.getActiveBridges() });
const live = _sessionTest.sessions.get(s.sessionId); const f = handleLab({ action: 'fit', sessionId: s.sessionId }); setTimeout(() => { live.expiresAt = Date.now() - 1; }, 50);
log({ name: 'real TTL expiry during fit', result: (await f).error?.code, cached: Boolean(live.result) });
const s2 = await handleLab({ action: 'start', template: 'free_fall', mystery: true });
const ok = await handleLab({ action: 'fit', sessionId: s2.sessionId });
log({ name: 'real mystery fit', status: ok.status, model: ok.fit?.uncertainty?.model, revealEqualsFit: ok.reveal?.gravity === ok.fit?.gravity?.value, revealU: ok.reveal?.uncertainty, activeAfter: _sessionTest.getActiveBridges() });
