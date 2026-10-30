// S15h: fit table + residual chart. Input is { times, output }: the request's time quantities and the Build/fitter handle() output.
// Every displayed number is a parsed fitter/instrument field (toPrecision(10) strips binary noise only); this module computes none
// except chart GEOMETRY (pixel positions, never shown as values). Labels come from the fitter's own source.label and are never upgraded.
const LABELS = ['simulated', 'measured'];
const finite = (x) => typeof x === 'number' && Number.isFinite(x);
const num = (x) => String(Number(x.toPrecision(10)));
const lab = (s) => (LABELS.includes(s?.label) ? s.label : null);
const bad = (m) => { throw new Error(m); };
// UI-e display only: the exact fitter text stays in .text/.residual/.time (and the cell title); nothing here changes a value.
const sup = (u) => u.replace(/\^2\b/g, '\u00b2').replace(/\^3\b/g, '\u00b3');
const sig = (x) => String(Number(x.toPrecision(4)));
// Value rounded to the uncertainty's 2 significant figures (1.887124302 ± 0.1415784327 -> 1.89 ± 0.14); u<=0 keeps raw text.
export const pm = (v, u, unit) => {
  const d = u > 0 ? Math.max(0, 1 - Math.floor(Math.log10(u))) : -1;
  // d > 8: uncertainty is at fitter-noise level; fixed decimals would print binary noise, so use 10 sig figs and exponent form
  return (d < 0 ? num(v) + ' \u00b1 ' + num(u) : d > 8 ? num(v) + ' \u00b1 ' + u.toExponential(1) : v.toFixed(d) + ' \u00b1 ' + u.toFixed(d)) + ' ' + sup(unit);
};
const HEAD = 10;

export function parseFit(input) {
  const o = input?.output, times = input?.times, f = o?.fit;
  if (o?.status !== 'ok' || !f) bad('fit output not ok');
  const lf = lab(f.source) ?? bad('fit source label missing');
  if (!Array.isArray(f.residuals) || !f.residuals.length || !f.residuals.every(finite)) bad('residuals must be finite numbers');
  if (!Array.isArray(times) || times.length !== f.residuals.length || !times.every((t) => finite(t?.value) && finite(t?.uncertainty) && typeof t.unit === 'string' && lab(t.source)))
    bad('times must match residuals');
  for (const k of ['rss', 'rmse']) if (!finite(f[k])) bad(k + ' must be finite');
  if (![f.degree, f.dof, f.n].every(Number.isInteger)) bad('degree/dof/n must be integers');
  const g = o.gravity, ms = o.model_selection;
  if (g && !(finite(g.value) && finite(g.uncertainty) && g.unit === 'm/s^2' && lab(g.source))) bad('gravity malformed');
  if (ms && !(Number.isInteger(ms.selected_degree) && typeof ms.criterion === 'string' && lab(ms.source))) bad('model selection malformed');
  return { o, f, g, ms, lf, times, unit: f.units?.position ?? 'm' };
}

const row = (name, text, label, evidence, display = text) => ({ name, text, label, evidence, display });

export function fitView(state, input, whatIf) {
  if (!input || !['fit.done', 'report.open'].includes(state.phase)) return { show: false };
  let p;
  try { p = parseFit(input); } catch (e) { return { show: true, error: 'Fit display rejected: ' + String(e.message).slice(0, 160) }; }
  const { f, g, ms, lf, times, unit } = p, ev = f.source.evidence;
  const rows = [
    // what-if of a recorded scene: the fitter's 'synthetic virtual-lab fit' note would be untrue there, so show the what-if label
    g ? row('Gravity', num(g.value) + ' \u00b1 ' + num(g.uncertainty) + ' ' + g.unit, lab(g.source), typeof whatIf === 'string' && whatIf ? whatIf : g.source.evidence, pm(g.value, g.uncertainty, g.unit)) : row('Gravity', 'unavailable (covariance invalid)', lf, ev),
    row('Polynomial degree', String(f.degree), lf, ev), row('Residual RMSE', num(f.rmse) + ' ' + unit, lf, ev, sig(f.rmse) + ' ' + sup(unit)),
    row('Residual sum of squares', num(f.rss) + ' ' + unit + '\u00b2', lf, ev, sig(f.rss) + ' ' + sup(unit) + '\u00b2'), row('Observations', String(f.n), lf, ev), row('Residual degrees of freedom', String(f.dof), lf, ev),
  ];
  if (ms) rows.push(row('Selected degree (' + ms.criterion + ')', String(ms.selected_degree), lab(ms.source), ms.source.evidence));
  const residuals = f.residuals.map((r, i) => ({ n: i + 1, time: num(times[i].value) + ' \u00b1 ' + num(times[i].uncertainty) + ' ' + times[i].unit, timeValue: times[i].value,
    timeDisplay: pm(times[i].value, times[i].uncertainty, times[i].unit), residual: num(r) + ' ' + unit, residualDisplay: sig(r) + ' ' + sup(unit), value: r, label: lf }));
  const tv = times.map((t) => t.value), span = Math.max(...f.residuals.map(Math.abs));
  const [t0, t1] = [Math.min(...tv), Math.max(...tv)], W = 592, H = 160, X = 24;
  const points = residuals.map((r) => ({ n: r.n, x: X + (t1 === t0 ? W / 2 : ((r.timeValue - t0) / (t1 - t0)) * W), y: span ? H / 2 - (r.value / span) * (H / 2 - 8) : H / 2 }));
  return { show: true, error: null, rows, residuals, label: lf, unit, source: ev,
    chart: { width: W + 2 * X, height: H, zeroY: H / 2, points, desc: 'Residuals (observed minus fitted position, ' + unit + ') against time, ' + lf + '. ' + residuals.length + ' points, from ' + num(Math.min(...f.residuals)) + ' to ' + num(Math.max(...f.residuals)) + ' ' + unit + '.' },
    notice: 'Fit values and residuals are fitter output on ' + lf + ' observations. They are not gate, real-scene or physical evidence.' };
}

export function renderFit(h, v) {
  if (!v.show) return null;
  if (v.error) return h('section', { className: 'ws-fit', 'aria-label': 'Fit results' }, h('p', { className: 'ws-error', role: 'alert' }, v.error));
  const c = v.chart;
  const tag = (l) => h('span', { className: 'ws-tag', 'data-label': l }, l);
  const head = v.residuals.slice(0, HEAD), rest = v.residuals.slice(HEAD);
  const resTable = (cap, rs) => h('table', { className: 'ws-fit-table' }, h('caption', null, cap),
    h('thead', null, h('tr', null, ...['#', 'Time', 'Residual', 'Label'].map((t) => h('th', { key: t, scope: 'col' }, t)))),
    h('tbody', null, ...rs.map((r) => h('tr', { key: r.n }, h('td', null, r.n), h('td', { className: 'ws-qval', title: r.time }, r.timeDisplay), h('td', { className: 'ws-qval', title: r.residual }, r.residualDisplay), h('td', null, tag(r.label))))));
  return h('section', { className: 'ws-fit', 'aria-label': 'Fit results' },
    // Provenance stated once in the caption; the Source cell repeats it only for rows from a different source.
    h('table', { className: 'ws-fit-table' }, h('caption', null, 'Fit summary', h('span', { className: 'ws-src' }, 'Source: ' + v.source + ' unless noted')),
      h('thead', null, h('tr', null, ...['Quantity', 'Value', 'Label', 'Source'].map((t) => h('th', { key: t, scope: 'col' }, t)))),
      h('tbody', null, ...v.rows.map((r) => h('tr', { key: r.name }, h('th', { scope: 'row' }, r.name), h('td', { className: 'ws-qval', title: r.text }, r.display), h('td', null, tag(r.label)), h('td', { className: 'ws-src' }, r.evidence === v.source ? '\u2014' : r.evidence))))),
    h('figure', { className: 'ws-resid' },
      h('svg', { viewBox: '0 0 ' + c.width + ' ' + (c.height + 8), role: 'img', 'aria-labelledby': 'ws-resid-t ws-resid-d', className: 'ws-resid-svg' },
        h('title', { id: 'ws-resid-t' }, 'Residual chart (' + v.label + ')'), h('desc', { id: 'ws-resid-d' }, c.desc),
        h('line', { x1: 0, x2: c.width, y1: c.zeroY, y2: c.zeroY, className: 'ws-resid-zero' }),
        ...c.points.map((p) => h('circle', { key: p.n, cx: p.x, cy: p.y, r: 4, className: 'ws-resid-pt' }))),
      h('figcaption', null, 'Residuals vs time (' + v.label + '). Values are in the table below; hover a value for the exact fitter output.')),
    resTable('Residuals' + (rest.length ? ' (first ' + HEAD + ' of ' + v.residuals.length + ')' : ''), head),
    rest.length ? h('details', { className: 'ws-resid-more' }, h('summary', null, 'Show remaining ' + rest.length + ' residuals'), resTable('Remaining residuals', rest)) : null,
    h('p', { className: 'ws-hint' }, v.notice));
}
