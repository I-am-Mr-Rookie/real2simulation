// N09: pure logic for the live product workspace (agent mode, new project, quota, GPU dot, voice WAV). Node-testable, no DOM.

export const AGENT_MODE_KEY = 'r2s.agent.mode';
// shortcut: the agent mode is stored per browser AND per user (localStorage key + server-verified scene id) and sent with every turn; move to a per-user API field if users switch devices often.
// N26: undefined = user not known yet (decide nothing, never default to Standard), null = this user never chose (show the choice card once).
// The old global key is ignored on purpose: it cannot be attributed to a user, so a new account in the same browser still sees the card.
export const readAgentMode = (s, userKey) => {
  if (!userKey) return undefined;
  try { const v = s?.getItem(AGENT_MODE_KEY + '.' + userKey); return v === 'standard' || v === 'open' || v === 'contributor' ? v : null; } catch { return null; }
};
export const writeAgentMode = (s, mode, userKey) => { if (!userKey) return false; try { s?.setItem(AGENT_MODE_KEY + '.' + userKey, mode); return true; } catch { return false; } };
// N36: stored mode 'standard' | 'open' | 'contributor'; 'open' is the Standard tier on Muse Open. The fallback model is never a choice.
export const STANDARD_MODELS = Object.freeze([{ id: 'standard', label: 'Muse Spark 1.3' }, { id: 'open', label: 'Muse Open (hosted on Baseten)' }]);
export const agentTier = (mode) => ({ contributor: mode === 'contributor', tier: mode === 'open' ? 'open' : 'spark' });
export const modeLabel = (mode) => (mode === 'contributor' ? 'Contributor mode' : mode === 'open' ? 'Standard: Muse Open' : 'Standard mode');
export const AGENT_MODES = Object.freeze([
  { id: 'standard', title: 'Standard', model: 'Muse Spark 1.3 or Muse Open, your pick',
    pros: ['Your prompts are not used to train Meta models', 'Same physics tools and answers'], cons: ['Costs more per message, so the daily budget runs out sooner'] },
  { id: 'contributor', title: 'Contributor', model: 'Muse Spark 1.3 contributor',
    pros: ['Much cheaper per message, so more turns fit in the daily budget', 'Same physics tools and answers'],
    cons: ['Meta may train on your prompts and the agent replies', 'Do not type anything private'] },
]);

export const UPLOAD_QUESTION = Object.freeze({ question: 'What are you uploading?', options: [
  { label: 'My experiment', mode: 'experiment', recommended: true, hint: 'Measure it: tracking, fit with uncertainty, 3D replay' },
  { label: 'Room video', mode: 'room', recommended: false, hint: 'Build a virtual lab with physics' }] });
export const LIMITS = 'mp4, mov or webm; up to 200 MB and 120 s.';
export const TIPS = Object.freeze({
  experiment: ['Fix the phone on a stand or table; do not pan or zoom.', 'Keep the whole motion in frame against a plain background.',
    'Use bright, even light; 60 fps if your phone offers it.', 'Put an object of known size (A4 sheet or ruler) in the plane of the motion for scale.',
    'Record 5 to 30 s: a second or two still, then the motion.'],
  room: ['Walk slowly around the room for 20 to 60 s, holding the phone steady.', 'Keep the floor in view most of the time.',
    'Use even light; avoid pointing at bright windows.', 'Lay an A4 sheet flat on the floor for scale; without it, scale is MODEL-ESTIMATED.',
    'Move the camera sideways, not only by turning on the spot.'],
});
export const projectTitle = (mode, now = new Date()) => (mode === 'room' ? 'Room ' : 'Experiment ') + now.toISOString().slice(0, 16).replace('T', ' ');

const UNITS = ['B', 'KB', 'MB', 'GB'];
export function fmtBytes(n) {
  let v = Math.max(0, Number(n) || 0), i = 0;
  while (v >= 1024 && i < UNITS.length - 1) { v /= 1024; i += 1; }
  return (i && v < 10 ? v.toFixed(1) : Math.round(v)) + ' ' + UNITS[i];
}
// N03 quota -> bar value (0..100) and one line of text; null when the API gave no quota.
export function quotaView(q) {
  if (!q || !(q.storage_bytes_limit > 0)) return null;
  const pct = Math.min(100, Math.round((q.storage_bytes_used / q.storage_bytes_limit) * 100));
  return { pct, full: q.storage_bytes_remaining <= 0 || q.uploads_remaining_today <= 0,
    text: fmtBytes(q.storage_bytes_used) + ' of ' + fmtBytes(q.storage_bytes_limit) + ' used. ' + q.uploads_remaining_today + ' of ' + q.uploads_daily_limit + ' uploads left today.' };
}

// N04 GET /gpu/status -> dot. Anything unexpected is "unknown", never a guessed colour.
const GPU_LABEL = { red: 'GPU sleeping', yellow: 'GPU starting', green: 'GPU running' };
export function gpuDot(s) {
  if (!s || !GPU_LABEL[s.state]) return { tone: 'unknown', label: 'GPU status unavailable', detail: '' };
  const n = Number(s.queue_length) || 0;
  const detail = s.your_position ? 'Your job: ' + s.your_position + ' of ' + n + ' in queue' : n ? n + (n === 1 ? ' job' : ' jobs') + ' in queue' : 'Queue empty';
  // N26: green with an empty queue is the warm-idle window; the API sends no idle time, so no minutes are shown.
  return { tone: s.state, label: s.state === 'green' && !n && !s.your_position ? 'GPU on, idle' : GPU_LABEL[s.state], detail };
}
export const GPU_POLL_MS = 10_000;
export const shouldPoll = (doc) => (doc?.visibilityState ?? 'visible') === 'visible';

// N26: API errors are { detail: { code, message, reason?, reset_at? } } (FastAPI) or { error: { message } }. An ISO reset_at inside the message is shown in local time.
const localTime = (iso) => new Date(iso).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', timeZoneName: 'short' });
export function apiErrorText(r, fallback, fmt = localTime) {
  const msg = r?.body?.error?.message || r?.body?.detail?.message || r?.body?.detail?.error?.message;
  if (!msg) return fallback + ' (' + (r?.status ?? 'network') + ').';
  const at = r?.body?.detail?.reset_at;
  return at && !Number.isNaN(new Date(at).getTime()) ? msg.split(at).join(fmt(at)) : msg;
}

// N07/N08 job lists: 404 means the endpoint is not deployed yet, 405 means the server has no list route (N08 rooms); never an error or an empty success.
export function jobsState(status, body, key) {
  if (status === 404 || status === 405) return { state: 'unavailable', items: [] };
  if (status < 200 || status >= 300) return { state: 'error', items: [], message: apiErrorText({ status, body }, 'Request failed') };
  const items = Array.isArray(body?.[key]) ? body[key] : Array.isArray(body?.jobs) ? body.jobs : Array.isArray(body) ? body : [];
  return { state: 'ok', items };
}

// Agent chat: history sent to /agent/turn is the last 20 user/assistant texts (core.MAX_HISTORY).
export const historyOf = (msgs) => msgs.filter((m) => (m.role === 'user' || m.role === 'assistant') && m.text).slice(-20).map((m) => ({ role: m.role, content: m.text }));
export const questionAnswer = (q, picked, other) => (other?.trim() ? other.trim() : q?.options?.[picked]?.label ?? '');
export const recommendedIndex = (q) => Math.max(0, q?.options?.findIndex((o) => o.recommended) ?? 0);

// Voice: mono PCM16 WAV (core.transcribe accepts 16 or 24 kHz, <= 60 s, <= 4 MB).
export const VOICE_RATE = 16000;
export const VOICE_MAX_S = 60;
export function encodeWav(samples, rate = VOICE_RATE) {
  const n = samples.length, buf = new ArrayBuffer(44 + n * 2), v = new DataView(buf);
  const str = (o, s) => { for (let i = 0; i < s.length; i += 1) v.setUint8(o + i, s.charCodeAt(i)); };
  str(0, 'RIFF'); v.setUint32(4, 36 + n * 2, true); str(8, 'WAVE'); str(12, 'fmt ');
  v.setUint32(16, 16, true); v.setUint16(20, 1, true); v.setUint16(22, 1, true); v.setUint32(24, rate, true);
  v.setUint32(28, rate * 2, true); v.setUint16(32, 2, true); v.setUint16(34, 16, true); str(36, 'data'); v.setUint32(40, n * 2, true);
  for (let i = 0; i < n; i += 1) { const x = Math.max(-1, Math.min(1, samples[i] || 0)); v.setInt16(44 + i * 2, x < 0 ? x * 0x8000 : x * 0x7fff, true); }
  return new Uint8Array(buf);
}
// Browser: any recorded clip (webm/ogg/mp4) -> decode -> OfflineAudioContext mono 16 kHz (downmix + resample) -> WAV bytes.
export async function toWav16k(bytes, AC = globalThis.AudioContext ?? globalThis.webkitAudioContext, OAC = globalThis.OfflineAudioContext) {
  const ctx = new AC();
  let decoded;
  try { decoded = await ctx.decodeAudioData(bytes); } finally { ctx.close?.(); }
  const seconds = Math.min(decoded.duration, VOICE_MAX_S);
  const off = new OAC(1, Math.max(1, Math.ceil(seconds * VOICE_RATE)), VOICE_RATE);
  const src = off.createBufferSource();
  src.buffer = decoded; src.connect(off.destination); src.start(0);
  const out = await off.startRendering();
  return encodeWav(out.getChannelData(0), VOICE_RATE);
}
