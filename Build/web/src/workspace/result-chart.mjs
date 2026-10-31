// S15aw: owner-clip result chart. Input = jobs.owner_measurement (status 'recorded' + series from evidence/S15aw/build_series.py).
// Every displayed number is an API field verbatim; this module computes only chart GEOMETRY (pixel positions, never shown).
const finite = (x) => typeof x === 'number' && Number.isFinite(x);
const W = 600, H = 280, L = 12, R = 12, T = 12, B = 12;
const f2 = (x) => Math.round(x * 100) / 100; // svg coordinate precision only

export function resultChart(m) {
  const s = m?.series;
  if (m?.status !== 'recorded' || !s || typeof s !== 'object') return null;
  const pts = s.points, mod = s.model, n = s.n_train;
  if (!Array.isArray(pts) || !Array.isArray(mod) || pts.length < 2 || mod.length < 2 || !Number.isInteger(n) || n < 1 || n >= pts.length
    || !pts.every((p) => Number.isInteger(p?.frame) && finite(p.t_s) && finite(p.y_px) && typeof p.held_out === 'boolean')
    || !mod.every((q) => finite(q?.t_s) && finite(q.y_px) && finite(q.band_px) && q.band_px >= 0 && typeof q.prediction === 'boolean'))
    return { error: 'Result chart unavailable: series malformed' };
  const ts = [...pts, ...mod].map((p) => p.t_s), ys = [...pts.map((p) => p.y_px), ...mod.flatMap((q) => [q.y_px - q.band_px, q.y_px + q.band_px])];
  const [t0, t1, y0, y1] = [Math.min(...ts), Math.max(...ts), Math.min(...ys), Math.max(...ys)];
  const sx = (t) => f2(L + (t1 === t0 ? 0.5 : (t - t0) / (t1 - t0)) * (W - L - R));
  const sy = (y) => f2(T + (y1 === y0 ? 0.5 : (y - y0) / (y1 - y0)) * (H - T - B)); // image y grows down, as in svg
  const path = (qs) => qs.map((q, i) => (i ? 'L' : 'M') + sx(q.t_s) + ' ' + sy(q.y_px)).join(' ');
  const k = mod.findIndex((q) => q.prediction), fitPart = k < 0 ? mod : mod.slice(0, k + 1), predPart = k < 0 ? [] : mod.slice(Math.max(0, k - 1));
  const band = mod.map((q, i) => (i ? 'L' : 'M') + sx(q.t_s) + ' ' + sy(q.y_px - q.band_px)).join(' ') + ' '
    + [...mod].reverse().map((q) => 'L' + sx(q.t_s) + ' ' + sy(q.y_px + q.band_px)).join(' ') + ' Z';
  const v = m.v3 ?? {}, verdict = v.verdict === 'PASS' || v.verdict === 'FAIL' ? v.verdict : null;
  const held = pts.filter((p) => p.held_out);
  const check = verdict ? 'Held-out check ' + verdict + ': chi2/dof = ' + v.chi2 + '/' + v.dof + ', p = ' + v.p : 'Held-out check: verdict unavailable';
  const summary = pts.length + ' RECORDED track points (frames ' + pts[0].frame + ' to ' + pts.at(-1).frame + '). SIMULATED quadratic fit to the first '
    + n + ' points; its prediction (dashed) is compared with the ' + held.length + ' held-out points. ' + check
    + (finite(m.held_out_rmse_px) ? '; held-out RMSE ' + m.held_out_rmse_px + ' px' : '') + '. Image pixels; scale unverified.';
  return { error: null, width: W, height: H, verdict, check, summary, label: String(s.label ?? ''), bandNote: String(s.band ?? ''), sigma: s.sigma_px,
    fitPath: path(fitPart), predPath: predPart.length ? path(predPart) : null, bandPath: band,
    points: pts.map((p) => ({ ...p, x: sx(p.t_s), y: sy(p.y_px) })), splitX: sx((pts[n - 1].t_s + pts[n].t_s) / 2) };
}

export function renderResultChart(h, m) {
  const c = resultChart(m);
  if (!c) return null;
  if (c.error) return h('p', { className: 'ws-note', role: 'note' }, c.error);
  return h('figure', { className: 'ws-result-chart', 'data-verdict': c.verdict ?? 'none' },
    h('svg', { viewBox: '0 0 ' + c.width + ' ' + c.height, role: 'img', 'aria-labelledby': 'ws-rc-t ws-rc-d', className: 'ws-rc-svg' },
      h('title', { id: 'ws-rc-t' }, 'Fit and held-out prediction'), h('desc', { id: 'ws-rc-d' }, c.summary),
      h('path', { d: c.bandPath, className: 'ws-rc-band' }),
      h('line', { x1: c.splitX, x2: c.splitX, y1: 0, y2: c.height, className: 'ws-rc-split' }),
      h('path', { d: c.fitPath, className: 'ws-rc-fit' }),
      c.predPath ? h('path', { d: c.predPath, className: 'ws-rc-pred' }) : null,
      ...c.points.map((p) => h('circle', { key: p.frame, cx: p.x, cy: p.y, r: 5, className: p.held_out ? 'ws-rc-pt ws-rc-held' : 'ws-rc-pt' }))),
    // house figcaption style (mono caps) carries the verdict only; legend and notes stay in body text for readability
    h('figcaption', { className: 'ws-rc-verdict', 'data-verdict': c.verdict ?? 'none' }, c.check),
    h('ul', { className: 'ws-rc-legend' },
        h('li', { 'data-key': 'pt' }, 'RECORDED track points (filled: fit prefix; hollow: held out)'),
        h('li', { 'data-key': 'fit' }, 'SIMULATED fit to the prefix (solid)'),
        h('li', { 'data-key': 'pred' }, 'SIMULATED prediction over the held-out points (dashed)'),
        h('li', { 'data-key': 'band' }, c.bandNote + ', sigma ' + c.sigma + ' px')),
    h('p', { className: 'ws-note' }, 'y axis: image y in pixels (down); x axis: time in s. Scale unverified. ' + c.label),
    h('details', { className: 'ws-resid-more' }, h('summary', null, 'Show data table'),
        h('table', { className: 'ws-fit-table' }, h('caption', null, 'Track points (RECORDED)'),
          h('thead', null, h('tr', null, ...['Frame', 't (s)', 'y (px)', 'Role'].map((t) => h('th', { key: t, scope: 'col' }, t)))),
          h('tbody', null, ...c.points.map((p) => h('tr', { key: p.frame }, h('td', null, String(p.frame)), h('td', null, String(p.t_s)), h('td', null, String(p.y_px)),
            h('td', null, p.held_out ? 'held out' : 'fit prefix')))))));
}
