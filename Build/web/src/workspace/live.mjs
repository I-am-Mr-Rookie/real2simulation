// N09: pure logic for the live product workspace (agent mode, new project, quota, GPU dot, voice WAV). Node-testable, no DOM.

export const AGENT_MODE_KEY = 'r2s.agent.mode';
// shortcut: the agent mode is stored per browser AND per user (localStorage key + server-verified scene id) and sent with every turn; move to a per-user API field if users switch devices often.
// N26: undefined = user not known yet (decide nothing, never default to Standard), null = this user never chose (show the choice card once).
// The old global key is ignored on purpose: it cannot be attributed to a user, so a new account in the same browser still sees the card.
export const readAgentMode = (s, userKey) => {
  if (!userKey) return undefined;
  try { const v = s?.getItem(AGENT_MODE_KEY + '.' + userKey); return v === 'standard' || v === 'open' || v === 'contributor' || v === 'wonder' ? v : null; } catch { return null; }
};
export const writeAgentMode = (s, mode, userKey) => { if (!userKey) return false; try { s?.setItem(AGENT_MODE_KEY + '.' + userKey, mode); return true; } catch { return false; } };
// Standard privacy choices; the hidden fallback model is never a choice.
export const STANDARD_MODELS = Object.freeze([{ id: 'standard', label: 'Muse Spark 1.3' }, { id: 'open', label: 'Muse Open (hosted on Baseten)' }, { id: 'wonder', label: 'Muse Wonder' }]);
export const agentTier = (mode) => ({ contributor: mode === 'contributor', tier: mode === 'open' || mode === 'wonder' ? mode : 'spark' });
export const modeLabel = (mode) => (mode === 'contributor' ? 'Contributor mode' : mode === 'open' ? 'Standard: Muse Open' : mode === 'wonder' ? 'Standard: Muse Wonder' : 'Standard mode');
export const AGENT_MODES = Object.freeze([
  { id: 'standard', title: 'Standard', model: 'Muse Spark, Muse Open or Muse Wonder, your pick',
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
// N55: content names, not timestamps. Mode only until a clip arrives; then the clip name ("apple_drop.mp4" -> "Apple drop").
export const projectTitle = (mode) => (mode === 'room' ? 'Room lab' : 'New experiment');
export function contentTitle(mode, fileName) {
  const base = String(fileName ?? '').replace(/\.[a-z0-9]+$/i, '').replace(/[_\-.]+/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 60);
  const name = /[a-z]{2}/i.test(base) ? base[0].toUpperCase() + base.slice(1).toLowerCase() : '';
  if (mode === 'room') return name ? (/\blab$/i.test(name) ? name : name + ' lab') : 'Room lab';
  return name || 'New experiment';
}
export const isDefaultTitle = (title) => /^(Room lab|New experiment|(Room|Experiment) \d{4}-\d\d-\d\d \d\d:\d\d)$/.test(String(title ?? ''));

// N55 model picker: relative bars only (1..3, no numbers: real cost and speed depend on the task). id = the saved agent mode.
export const MODEL_CHOICES = Object.freeze([
  { id: 'standard', name: 'Muse Spark 1.3', sub: 'Standard', tag: 'Recommended', bars: { Intelligence: 2, Speed: 2, Cost: 2 },
    pro: 'Strong answers; prompts are not used for training', con: 'Costs more than Contributor mode' },
  { id: 'contributor', name: 'Muse Spark 1.3', sub: 'Contributor', tag: 'Cheapest', bars: { Intelligence: 2, Speed: 2, Cost: 1 },
    pro: 'Same model at a much lower cost per message', con: 'Meta trains on your prompts' },
  { id: 'open', name: 'Muse Open', sub: 'Hosted on Baseten', tag: 'Fastest', bars: { Intelligence: 1, Speed: 3, Cost: 2 },
    pro: 'Quick replies', con: 'Smaller open model; weaker on hard questions' },
  { id: 'wonder', name: 'Muse Wonder', sub: 'Standard', tag: 'Smartest', bars: { Intelligence: 3, Speed: 1, Cost: 3 },
    pro: 'Highest intelligence; prompts are not used for training', con: 'Slower and costlier than Muse Spark' },
]);

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
    text: fmtBytes(q.storage_bytes_used) + ' of ' + fmtBytes(q.storage_bytes_limit) + ' used. ' + q.uploads_remaining_today + ' of ' + q.uploads_daily_limit + ' uploads left today.'
      + (q.storage_bytes_public > 0 ? ' Public samples not counted' : '') };
}

// N04 GET /gpu/status -> dot. Anything unexpected is "unknown", never a guessed colour.
const GPU_LABEL = { red: 'GPU sleeping', yellow: 'GPU starting', green: 'GPU running' };
export function gpuDot(s, elapsedSeconds = 0) {
  if (!s || !GPU_LABEL[s.state]) return { tone: 'unknown', label: 'GPU status unavailable', detail: '' };
  const n = Number(s.queue_length) || 0;
  const detail = s.your_position ? 'Your job: ' + s.your_position + ' of ' + n + ' in queue' : n ? n + (n === 1 ? ' job' : ' jobs') + ' in queue' : 'Queue empty';
  if (s.state === 'green' && Number.isFinite(s.idle_seconds_remaining) && s.idle_seconds_remaining >= 0) {
    // An active job cannot sleep yet; the 15-minute idle window starts when it finishes.
    const seconds = Math.max(0, Math.ceil(s.idle_seconds_remaining - (n ? 0 : Math.max(0, elapsedSeconds))));
    const clock = Math.floor(seconds / 60) + ':' + String(seconds % 60).padStart(2, '0');
    return { tone: 'green', label: 'GPU on, sleeps in ' + clock + (n ? ' after job' : ''),
      detail: n ? detail : seconds ? (s.source === 'jobs' ? 'Estimated idle window' : 'Queue empty') : 'Waiting for GPU to sleep' };
  }
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
