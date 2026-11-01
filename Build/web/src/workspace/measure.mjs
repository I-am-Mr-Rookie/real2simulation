// N22: pure logic for the live Mode B result (fit curve + 1 sigma band SVG, value +/- u), job status cards and lab scenes from a track.
// Node-testable, no DOM. Every number comes from the N07 result; the curve is an ordinary least-squares refit of the same points
// with the degree the fitter selected, so its acceleration equals the fitter value (checked in tests/workspace/measure.test.mjs).

// Least squares y = sum b_k t^k with covariance s^2 (X'X)^-1, s^2 = RSS / (n - p). Returns null when underdetermined.
export function polyFit(t, y, deg) {
  const p = deg + 1, n = Math.min(t.length, y.length);
  if (n <= p) return null;
  const A = Array.from({ length: p }, () => Array(2 * p).fill(0)), xty = Array(p).fill(0);
  for (let i = 0; i < n; i += 1) for (let r = 0; r < p; r += 1) {
    for (let c = 0; c < p; c += 1) A[r][c] += t[i] ** (r + c);
    xty[r] += y[i] * t[i] ** r;
  }
  for (let r = 0; r < p; r += 1) A[r][p + r] = 1;
  for (let c = 0; c < p; c += 1) { // Gauss-Jordan with partial pivoting on [X'X | I]
    let piv = c; for (let r = c + 1; r < p; r += 1) if (Math.abs(A[r][c]) > Math.abs(A[piv][c])) piv = r;
    if (Math.abs(A[piv][c]) < 1e-12) return null;
    [A[c], A[piv]] = [A[piv], A[c]];
    const d = A[c][c]; for (let k = 0; k < 2 * p; k += 1) A[c][k] /= d;
    for (let r = 0; r < p; r += 1) if (r !== c) { const f = A[r][c]; for (let k = 0; k < 2 * p; k += 1) A[r][k] -= f * A[c][k]; }
  }
  const inv = A.map((row) => row.slice(p));
  const b = inv.map((row) => row.reduce((s, v, k) => s + v * xty[k], 0));
  const at = (x) => b.reduce((s, v, k) => s + v * x ** k, 0);
  let rss = 0; for (let i = 0; i < n; i += 1) rss += (y[i] - at(t[i])) ** 2;
  const s2 = rss / (n - p), cov = inv.map((row) => row.map((v) => v * s2));
  const sd = (x) => { let s = 0; for (let r = 0; r < p; r += 1) for (let c = 0; c < p; c += 1) s += x ** r * cov[r][c] * x ** c; return Math.sqrt(Math.max(0, s)); };
  return { b, cov, at, sd };
}

export const degreeOf = (axisFit) => (axisFit?.model === 'constant_acceleration' ? 2 : 1);

// N24: about n round tick values (1, 2 or 5 x 10^k steps) covering [lo, hi]; label decimals follow the step.
export function niceTicks(lo, hi, n = 5) {
  if (!Number.isFinite(lo) || !Number.isFinite(hi)) return { step: 1, values: [], labels: [] };
  if (hi < lo) [lo, hi] = [hi, lo];
  if (hi === lo) { const d = Math.abs(lo) / 2 || 0.5; lo -= d; hi += d; }
  const raw = (hi - lo) / Math.max(1, n), mag = 10 ** Math.floor(Math.log10(raw)), f = raw / mag;
  const step = (f <= 1 ? 1 : f <= 2 ? 2 : f <= 5 ? 5 : 10) * mag;
  const first = Math.floor(lo / step + 1e-9), last = Math.ceil(hi / step - 1e-9);
  const values = Array.from({ length: last - first + 1 }, (_, i) => +((first + i) * step).toPrecision(12));
  const dec = Math.max(0, -Math.floor(Math.log10(step) + 1e-9));
  return { step, values, labels: values.map((v) => (Object.is(+v.toFixed(dec), -0) ? 0 : v).toFixed(dec)) };
}

// y(t) chart for one axis: track points, fitted curve and 1 sigma band, round-number axes with units, in a fixed SVG viewBox.
export function chartGeom(result, axis = 'y', W = 360, H = 230, pad = 44) {
  const tr = result?.trajectory, t = tr?.t_s, v = tr?.[axis];
  if (!Array.isArray(t) || !Array.isArray(v) || t.length < 2) return null;
  // N26: the server curve (fitter coefficients + full covariance) wins; the browser refit only serves results without one (recorded samples).
  // An abstained result (fit null) gets dots only, never a made-up line.
  const sc = result?.curve, N = 48, t0 = Math.min(...t), t1 = Math.max(...t);
  const server = sc?.axis === axis && sc.unit === (tr.unit || 'px') && Array.isArray(sc.t_s) && sc.t_s.length >= 2 && sc.value?.length === sc.t_s.length;
  const fit = server || !result?.fit ? null : polyFit(t, v, degreeOf(result.fit[axis]));
  const ts = server ? sc.t_s : Array.from({ length: N + 1 }, (_, i) => t0 + ((t1 - t0) * i) / N);
  const mid = server ? sc.value : fit ? ts.map(fit.at) : [];
  const sd = server ? (sc.band_1sigma?.length === ts.length ? sc.band_1sigma : null) : fit ? ts.map(fit.sd) : null;
  const hi = sd ? mid.map((m, i) => m + sd[i]) : [], lo = sd ? mid.map((m, i) => m - sd[i]) : [];
  const vmin = Math.min(...v, ...mid, ...lo), vmax = Math.max(...v, ...mid, ...hi), span = vmax - vmin || 1;
  const xt = niceTicks(t0, t1, 5), yt = niceTicks(vmin, vmax, 4);
  const xa = xt.values[0], xb = xt.values.at(-1), ya = yt.values[0], yb = yt.values.at(-1);
  const L = pad + 10, R = W - 12, T = 12, B = H - pad + 6; // plot box; room on the left and bottom for labels
  const X = (x) => L + ((x - xa) / (xb - xa || 1)) * (R - L), Y = (u) => B - ((u - ya) / (yb - ya || span)) * (B - T);
  const path = (xs, us) => xs.map((x, i) => (i ? 'L' : 'M') + X(x).toFixed(1) + ' ' + Y(us[i]).toFixed(1)).join(' ');
  const unit = tr.unit || 'px';
  return {
    W, H, pad, unit, axis, box: { L, R, T, B },
    xLabel: 'time (s)', yLabel: axis + ' position (' + unit + ')',
    xTicks: xt.values.map((x, i) => ({ x: +X(x).toFixed(1), label: xt.labels[i] })),
    yTicks: yt.values.map((u, i) => ({ y: +Y(u).toFixed(1), label: yt.labels[i] })),
    points: t.map((x, i) => ({ cx: +X(x).toFixed(1), cy: +Y(v[i]).toFixed(1) })),
    curve: mid.length ? path(ts, mid) : null,
    band: sd ? path(ts, hi) + ' ' + path([...ts].reverse(), [...lo].reverse()).replace(/^M/, 'L') + ' Z' : null,
    ticks: { t0: +t0.toFixed(3), t1: +t1.toFixed(3), vmin: +vmin.toPrecision(3), vmax: +vmax.toPrecision(3) },
  };
}

// N26: the scale tag of a result card. A typed size is "scale assumed (user size)" (never MEASURED); only a MEASURED label gets the green tag.
export function scaleTag(result) {
  const l = result?.quantity?.label ?? result?.label ?? '';
  if (/^scale assumed \(user size\)/.test(l)) return { text: 'scale assumed (user size)', tone: 'warn' };
  return /MEASURED/.test(l) ? { text: 'MEASURED', tone: 'ok' } : { text: 'scale unverified', tone: 'warn' };
}

// N26: label lines of a result card. The abstain label repeats its "No fit" reason (shown in the card text), and a short label that
// the longer one extends ("scale assumed (user size)" vs "...: ball diameter 6 cm") is shown once, in its longer form.
export function labelsOf(result) {
  const all = [...new Set([result?.quantity?.label, result?.reason ? result.label?.split('. No fit: ')[0] : result?.label, result?.clock, result?.track?.label].filter(Boolean))];
  return all.filter((l) => !all.some((o) => o !== l && o.startsWith(l + ':')));
}

// value +/- u with u at 2 significant figures and the value at the same decimal place.
export function fmtPm(value, u) {
  if (!Number.isFinite(value)) return 'no value';
  if (!(u > 0)) return String(+value.toPrecision(4));
  const d = 1 - Math.floor(Math.log10(u)), q = 10 ** -d;
  const f = (x) => (d >= 0 ? x.toFixed(d) : String(Math.round(x / q) * q));
  return f(value) + ' +/- ' + f(u);
}

// Known size from the form -> the N07 text field ("ball diameter 6.5 cm"); null when not given or not a positive number.
export const SIZE_UNITS = ['mm', 'cm', 'm'];
export function knownSizeText(value, unit, what) {
  const v = Number(value);
  if (value === '' || value == null || !(v > 0) || !SIZE_UNITS.includes(unit)) return null;
  return ((String(what || '').trim() || 'object size') + ' ' + v + ' ' + unit).slice(0, 200);
}
// Click on a scaled media element -> integer pixel in its natural size (video frame or view PNG).
export function naturalPoint(offsetX, offsetY, clientW, clientH, naturalW, naturalH) {
  if (!(clientW > 0 && clientH > 0 && naturalW > 0 && naturalH > 0)) return null;
  const x = Math.round((offsetX / clientW) * naturalW), y = Math.round((offsetY / clientH) * naturalH);
  return { x: Math.min(naturalW - 1, Math.max(0, x)), y: Math.min(naturalH - 1, Math.max(0, y)) };
}
// N07 POST body: exactly one of point or target_text (a click wins over a typed name).
export function experimentBody(fileId, { point, name, size, unit, what }, projectId) {
  const body = { file_id: fileId };
  if (point) body.point = { x: point.x, y: point.y }; else if (String(name || '').trim()) body.target_text = String(name).trim().slice(0, 80); else return null;
  const k = knownSizeText(size, unit, what); if (k) body.known_size = k;
  if (projectId) body.project_id = projectId;
  return body;
}

// N07 GET /experiments/{id} and N08 GET /rooms/{id} -> one card shape.
const STEP = { queued: 'Queued', running: 'Tracking with hosted SAM 3.1', sampling: 'Sampling frames', reconstructing: 'Reconstructing on the GPU', done: 'Done', failed: 'Failed' };
export function jobView(kind, body) {
  const j = kind === 'experiment' ? body?.experiment : body?.job;
  if (!j) return { state: 'unknown', step: 'Status unavailable', terminal: false, error: null, gpu: null, result: null };
  const state = String(j.status ?? j.state ?? 'unknown');
  const err = j.error && typeof j.error === 'object' ? j.error.message : j.error;
  return { state, step: STEP[state] ?? state, terminal: state === 'done' || state === 'failed', error: state === 'failed' ? String(err || j.code || 'Job failed.') : null,
    gpu: j.gpu ?? null, result: kind === 'experiment' ? j.result ?? null : null,
    labels: kind === 'room' ? [j.scale, j.gravity && 'gravity ' + j.gravity].filter(Boolean) : [] };
}
export const POLL_MS = 3000;
// Agent tool calls that started a job -> cards to track.
export function jobsFromToolCalls(calls) {
  const out = [];
  for (const c of Array.isArray(calls) ? calls : []) {
    if (c?.name === 'start_experiment_track' && c.output?.trajectory_id) out.push({ kind: 'experiment', id: String(c.output.trajectory_id) });
    if (c?.name === 'start_room_build' && c.output?.room_job_id) out.push({ kind: 'room', id: String(c.output.room_job_id) });
  }
  return out;
}
// Only metric results can be shared (N16 refuses px results).
export const shareable = (result) => result?.quantity?.unit === 'm/s^2';

// "Redo with changes": the measured track as a lab-scene-v1 ball (SIMULATED what-if) plus the track polyline to draw.
// shortcut: px tracks are drawn at a nominal 1 px = 1 mm and labelled scale unverified; upgrade when a MODEL-ESTIMATED scale exists.
export function trajectoryScene(result) {
  const tr = result?.trajectory;
  if (!tr || !Array.isArray(tr.t_s) || tr.t_s.length < 3) return null;
  const metric = tr.unit === 'm', s = metric ? 1 : 0.001;
  const lift = -Math.min(...tr.y) * s + 0.05;
  const r4 = (v) => Math.max(-1e4, Math.min(1e4, +v.toFixed(4)));
  const track = tr.t_s.map((_, i) => [r4(tr.x[i] * s), r4(tr.y[i] * s + lift), 0]);
  const vel = (axis) => { const f = polyFit(tr.t_s, tr[axis], degreeOf(result.fit?.[axis])); return f ? r4(f.b[1] * s) : 0; };
  const ball = { id: 'ball-1', kind: 'ball', position: track[0], rotation: [0, 0, 0, 1], size: [0.05, 0.05, 0.05], velocity: [vel('x'), vel('y'), 0],
    mass: 1, friction: 0.5, restitution: 0.3, fixed: false, sensor: true, params: {} };
  return { scene: { version: 'lab-scene-v1', label: 'SIMULATED', units: 'm', gravity: [0, -9.81, 0], room: { kind: 'plane', floor_y: 0 }, objects: [ball] },
    track, metric, note: metric ? 'Track MEASURED in metres from your known size. The ball is SIMULATED: edit it and press Play to redo with changes.'
      : 'Scale unverified: the track is in pixels, drawn as 1 px = 1 mm. The ball is SIMULATED (what-if): edit it and press Play.' };
}
