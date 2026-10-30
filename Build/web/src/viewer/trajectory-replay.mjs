// S09k: replay of a bounded, hashed SIMULATED trajectory trace (DTO per evidence/S18/S18k-TRACE-CONTRACT.md).
// Framework-free; SVG side view (x right, +Y up) so no scene geometry is invented: only the trace, a labelled
// neutral reference axis and the marker. SHA-256 covers the exact body bytes (which lack the sha256 field).
import { ViewerError, abortError, deepFreeze } from './common.mjs';

export const TRACE_LIMITS = Object.freeze({ maxSamples: 4096, maxBodyBytes: 262144, maxAbsM: 1e4 });
export const SIMULATED_BANNER = 'SIMULATED trajectory — simulator output, not a measurement';
const KINDS = ['free-fall', 'projectile', 'pendulum'];
const KEYS = ['kind', 'source', 'inputProvenance', 'dt_s', 'samples', 'sha256', 'label'];
const exactKeys = (o, keys) => o && typeof o === 'object' && !Array.isArray(o) &&
  Object.keys(o).length === keys.length && keys.every((k) => Object.hasOwn(o, k));
const bad = (why) => { throw new ViewerError('INVALID_ARTIFACT', 'Trajectory trace invalid: ' + why); };

export async function sha256Hex(bytes) {
  const d = await globalThis.crypto.subtle.digest('SHA-256', bytes);
  return [...new Uint8Array(d)].map((b) => b.toString(16).padStart(2, '0')).join('');
}

/** Verify exact body bytes against the catalogue SHA, parse, add sha256, then checkTrace. */
export async function traceFromBody(bytes, sha256, limits = TRACE_LIMITS) {
  if (!(bytes instanceof Uint8Array) || bytes.byteLength > limits.maxBodyBytes) bad('body size');
  if (typeof sha256 !== 'string' || await sha256Hex(bytes) !== sha256) bad('sha256 mismatch');
  let body;
  try { body = JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(bytes)); } catch { bad('body is not UTF-8 JSON'); }
  if (!body || typeof body !== 'object' || Object.hasOwn(body, 'sha256')) bad('body fields');
  return checkTrace({ ...body, sha256 }, limits);
}

/** Validate the DTO (shape, labels, bounds, dense steps, time_s === step*dt_s); returns a frozen copy. */
export function checkTrace(trace, limits = TRACE_LIMITS) {
  if (!exactKeys(trace, KEYS)) bad('fields');
  if (!KINDS.includes(trace.kind)) bad('kind');
  if (trace.source !== 'simulated' || trace.inputProvenance !== 'synthetic' || trace.label !== 'SIMULATED') bad('labels must be simulated/synthetic/SIMULATED');
  if (!(Number.isFinite(trace.dt_s) && trace.dt_s > 0)) bad('dt_s');
  if (typeof trace.sha256 !== 'string' || !/^[0-9a-f]{64}$/.test(trace.sha256)) bad('sha256 format');
  const s = trace.samples;
  if (!Array.isArray(s) || s.length < 2 || s.length > limits.maxSamples) bad('sample count');
  s.forEach((x, i) => {
    if (!exactKeys(x, ['step', 'time_s', 'position_m'])) bad('sample fields');
    const p = x.position_m;
    if (!Array.isArray(p) || p.length !== 3 || !p.every((v) => Number.isFinite(v) && Math.abs(v) <= limits.maxAbsM)) bad('position');
    if (x.step !== i || x.time_s !== i * trace.dt_s) bad('steps must be dense from 0 with time_s === step * dt_s');
  });
  return deepFreeze(structuredClone(trace));
}

/** Linear position at time t (clamped). Returns { t, i, position }; i = index of last sample <= t. */
export function sampleTrace(samples, t) {
  const a0 = samples[0], last = samples[samples.length - 1];
  if (!(t > a0.time_s)) return { t: a0.time_s, i: 0, position: [...a0.position_m] };
  if (t >= last.time_s) return { t: last.time_s, i: samples.length - 1, position: [...last.position_m] };
  let lo = 0, hi = samples.length - 1;
  while (hi - lo > 1) { const m = (lo + hi) >> 1; if (samples[m].time_s <= t) lo = m; else hi = m; }
  const a = samples[lo], b = samples[hi], u = (t - a.time_s) / (b.time_s - a.time_s);
  return { t, i: lo, position: a.position_m.map((v, k) => v + (b.position_m[k] - v) * u) };
}

/** Uniform-scale side-view mapping (x,y metres -> SVG units) with padding; y flipped so up is up. */
export function sideViewFit(samples, size = 1000, pad = 60) {
  let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
  for (const { position_m: [x, y] } of samples) { x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y); }
  const span = Math.max(x1 - x0, y1 - y0, 1e-6), k = (size - 2 * pad) / span;
  const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2;
  return { k, min: [x0, y0], map: ([x, y]) => [size / 2 + (x - cx) * k, size / 2 - (y - cy) * k] };
}

const SVGNS = 'http://www.w3.org/2000/svg';

/**
 * Mount a replay into host. Mystery mode is refused before touching the DOM or the trace. Returns { dispose, trace }.
 * opts: { mode: 'inspect'|'lab'|'mystery', signal?: AbortSignal, raf?, caf? }
 */
export async function mountTrajectoryReplay(host, rawTrace, { mode = 'inspect', signal, raf = globalThis.requestAnimationFrame?.bind(globalThis), caf = globalThis.cancelAnimationFrame?.bind(globalThis) } = {}) {
  if (mode === 'mystery') throw new ViewerError('UNAVAILABLE', 'Mystery mode trajectories are withheld until fit');
  if (!['inspect', 'lab'].includes(mode)) throw new ViewerError('INVALID_REQUEST', 'invalid mode');
  if (signal?.aborted) throw abortError();
  // Byte-hash verification happens in the S18k loader or traceFromBody; here the DTO is re-validated.
  const trace = checkTrace(rawTrace);
  const doc = host.ownerDocument, S = trace.samples, t0 = S[0].time_s, t1 = S[S.length - 1].time_s;
  const el = (ns, tag, attrs = {}, text) => {
    const n = ns ? doc.createElementNS(ns, tag) : doc.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, String(v));
    if (text != null) n.textContent = text;
    return n;
  };
  const fit = sideViewFit(S);
  // myfront: technical home: characterful grotesque + mono readout, hard black offset shadows, ink + one accent.
  const root = el(null, 'section', { class: 'r2s-replay', 'aria-label': 'Simulated trajectory replay', style: "max-width:100%;font:14px/1.45 'Instrument Sans','Hanken Grotesk',system-ui,sans-serif;color:#141414" });
  const banner = el(null, 'p', { role: 'note', style: 'margin:0 0 10px;padding:8px 12px;background:#ffe9a8;border:2px solid #141414;box-shadow:3px 3px 0 #141414;font-weight:700' }, SIMULATED_BANNER);
  const title = el(null, 'p', { style: 'margin:0 0 6px;overflow-wrap:anywhere' }, trace.kind + ' · synthetic inputs · ' + S.length + ' samples, dt ' + trace.dt_s + ' s · sha256 ' + trace.sha256.slice(0, 12) + '…');
  const svg = el(SVGNS, 'svg', { viewBox: '0 0 1000 1000', role: 'img', 'aria-label': 'Side view of simulated path (x right, y up)', style: 'display:block;width:100%;height:auto;max-height:70vh;background:#fbf8f1;border:2px solid #141414' });
  // Neutral reference only: dashed axes at the path's min x / min y, labelled as such (not scene geometry).
  const [ax, ay] = fit.map(fit.min);
  svg.append(el(SVGNS, 'path', { d: 'M40 ' + ay + 'H960M' + ax + ' 960V40', stroke: '#999', 'stroke-dasharray': '8 8', fill: 'none' }),
    el(SVGNS, 'text', { x: 48, y: Math.min(990, ay + 34), fill: '#555', 'font-size': 28 }, 'reference axes (not scene geometry)'));
  const pts = S.map((s) => fit.map(s.position_m).map((v) => v.toFixed(1)).join(','));
  svg.append(el(SVGNS, 'polyline', { points: pts.join(' '), fill: 'none', stroke: '#c8c2b4', 'stroke-width': 4 }));
  const trail = el(SVGNS, 'polyline', { fill: 'none', stroke: '#141414', 'stroke-width': 6 });
  const marker = el(SVGNS, 'circle', { r: 16, fill: '#e4572e', stroke: '#141414', 'stroke-width': 4 });
  svg.append(trail, marker);
  const bar = el(null, 'div', { style: 'display:flex;gap:10px;align-items:center;margin-top:12px;flex-wrap:wrap' });
  const play = el(null, 'button', { type: 'button', 'aria-pressed': 'false', style: 'min-height:44px;min-width:80px;padding:0 16px;font:inherit;font-weight:700;color:#141414;background:#fff;border:2px solid #141414;box-shadow:3px 3px 0 #141414;cursor:pointer' }, 'Play');
  const scrub = el(null, 'input', { type: 'range', min: t0, max: t1, step: 'any', value: t0, 'aria-label': 'Replay time (seconds)', style: 'flex:1 1 160px;min-height:44px;accent-color:#e4572e' });
  const out = el(null, 'output', { style: "font:13px 'Source Code Pro',ui-monospace,monospace;font-variant-numeric:tabular-nums;min-width:12ch" });
  bar.append(play, scrub, out);
  root.append(banner, title, svg, bar);

  let t = t0, playing = false, frame = null, last = null, disposed = false;
  const draw = () => {
    const { position, i } = sampleTrace(S, t);
    const [mx, my] = fit.map(position);
    marker.setAttribute('cx', mx.toFixed(1)); marker.setAttribute('cy', my.toFixed(1));
    trail.setAttribute('points', pts.slice(0, i + 1).concat(mx.toFixed(1) + ',' + my.toFixed(1)).join(' '));
    scrub.value = String(t);
    scrub.setAttribute('aria-valuetext', t.toFixed(3) + ' seconds');
    out.textContent = 't = ' + t.toFixed(3) + ' s';
  };
  const stop = () => { playing = false; if (frame != null) caf?.(frame); frame = null; last = null; play.textContent = 'Play'; play.setAttribute('aria-pressed', 'false'); };
  const tick = (ms) => {
    if (!playing) return;
    if (last != null) t = Math.min(t1, t + (ms - last) / 1000);
    last = ms; draw();
    if (t >= t1) stop(); else frame = raf(tick);
  };
  const onPlay = () => {
    if (playing) return stop();
    if (!raf) return;
    if (t >= t1) t = t0;
    playing = true; play.textContent = 'Pause'; play.setAttribute('aria-pressed', 'true'); frame = raf(tick);
  };
  const onScrub = () => { stop(); const v = Number(scrub.value); t = Number.isFinite(v) ? Math.min(t1, Math.max(t0, v)) : t0; draw(); };
  play.addEventListener('click', onPlay);
  scrub.addEventListener('input', onScrub);
  draw();
  host.append(root);
  const dispose = () => {
    if (disposed) return;
    disposed = true; stop();
    play.removeEventListener('click', onPlay); scrub.removeEventListener('input', onScrub);
    signal?.removeEventListener('abort', dispose);
    root.remove();
  };
  signal?.addEventListener('abort', dispose, { once: true });
  return Object.freeze({ dispose, trace });
}

