import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { fitView, renderFit, parseFit, pm } from '../../Build/web/src/workspace/fit-view.mjs';

// REAL Build/fitter.handle output on observations from the REAL Build/instruments (evidence/S15/fit_fixtures.py); SYNTHETIC settings.
const FIX = JSON.parse(readFileSync(new URL('./fixtures/fit-output.json', import.meta.url), 'utf8'));
const input = { times: FIX.request.times, output: FIX.output };

test('UI-e display rounding: value to uncertainty 2 sig figs, unit superscript; raw text untouched', () => {
  assert.equal(pm(1.887124302, 0.1415784327, 'm/s^2'), '1.89 \u00b1 0.14 m/s\u00b2');
  assert.equal(pm(0.5, 0.001, 's'), '0.5000 \u00b1 0.0010 s');
  assert.equal(pm(123.456, 25, 'm'), '123 \u00b1 25 m');
  assert.equal(pm(2, 0, 'm'), '2 \u00b1 0 m');
  const v = fitView({ phase: 'fit.done' }, input), g = FIX.output.gravity;
  assert.equal(v.rows[0].display, pm(g.value, g.uncertainty, g.unit));
  assert.ok(renderFit(html, v).includes('title="' + v.rows[0].text + '"'));
  const out = renderFit(html, v); // provenance kept: common source once in caption, every other source still printed
  assert.ok(out.includes('Source: ' + v.source + ' unless noted'));
  for (const r of v.rows) assert.ok(out.includes(r.evidence));
});
const html = (tag, props, ...kids) => '<' + tag + Object.entries(props ?? {}).map(([k, v]) => ' ' + k + '="' + v + '"').join('') + '>' + kids.flat().join('') + '</' + tag + '>';
const num = (x) => String(Number(x.toPrecision(10)));
const done = { phase: 'fit.done' };
const clone = (o) => JSON.parse(JSON.stringify(o));

test('fixture is current real fitter output', () => {
  const r = spawnSync('python', ['evidence/S15/fit_fixtures.py', '--check'], { encoding: 'utf8' });
  if (r.error) return; // python unavailable here; the generator --check is the authority
  assert.equal(r.status, 0, r.stderr);
});

test('every table/residual value equals fitter output; labels persist', () => {
  const v = fitView(done, input), f = FIX.output.fit, g = FIX.output.gravity;
  assert.equal(v.error, null);
  const txt = Object.fromEntries(v.rows.map((r) => [r.name, r.text]));
  assert.equal(txt.Gravity, num(g.value) + ' \u00b1 ' + num(g.uncertainty) + ' ' + g.unit);
  assert.equal(txt['Residual RMSE'], num(f.rmse) + ' m');
  assert.equal(txt['Residual sum of squares'], num(f.rss) + ' m\u00b2');
  assert.equal(txt['Selected degree (AIC)'], String(FIX.output.model_selection.selected_degree));
  assert.equal(v.residuals.length, f.residuals.length);
  v.residuals.forEach((r, i) => { assert.equal(r.residual, num(f.residuals[i]) + ' m'); assert.equal(r.value, f.residuals[i]); assert.equal(r.timeValue, FIX.request.times[i].value); });
  assert.ok(v.rows.every((r) => r.label === 'simulated') && v.residuals.every((r) => r.label === 'simulated'));
  const out = renderFit(html, v);
  for (const r of f.residuals) assert.ok(out.includes(num(r) + ' m'));
  assert.equal(out.split('data-label="simulated"').length - 1, v.rows.length + v.residuals.length);
  assert.match(out, /Residuals vs time \(simulated\)/); assert.match(out, /Residual chart \(simulated\)/);
  assert.match(out, /<svg[^>]*role="img"/); assert.match(out, /scope="col"/);
  assert.equal(out.split('<circle').length - 1, f.residuals.length);
});

test('chart geometry stays in bounds and the zero line is the residual 0', () => {
  const c = fitView(done, input).chart;
  for (const p of c.points) { assert.ok(p.x >= 24 && p.x <= c.width - 24 + 0.001); assert.ok(p.y >= 0 && p.y <= c.height); }
  FIX.output.fit.residuals.forEach((r, i) => assert.equal(Math.sign(c.zeroY - c.points[i].y), Math.sign(r)));
});

test('a measured label from the fitter is retained, never upgraded or downgraded', () => {
  const m = clone(input); m.output.fit.source.label = 'measured'; m.output.gravity.source.label = 'measured';
  const v = fitView(done, m);
  assert.equal(v.rows[0].label, 'measured'); assert.ok(v.residuals.every((r) => r.label === 'measured'));
  assert.match(renderFit(html, v), /Residuals vs time \(measured\)/);
});

test('invalid fitter output is rejected, never displayed as numbers', () => {
  const mut = (fn) => { const m = clone(input); fn(m); return fitView(done, m); };
  for (const fn of [(m) => { m.output.status = 'error'; }, (m) => { m.output.fit.residuals.pop(); }, (m) => { m.output.fit.residuals[0] = null; },
    (m) => { m.output.fit.source.label = 'real'; }, (m) => { m.output.gravity.value = 'x'; }, (m) => { m.times[0].value = NaN; }]) {
    const v = mut(fn); assert.ok(v.error && !v.rows); assert.match(renderFit(html, v), /role="alert"/);
  }
  assert.throws(() => parseFit({}));
  assert.equal(fitView({ phase: 'run.done' }, input).show, false);
  assert.equal(fitView(done, null).show, false);
  assert.equal(renderFit(html, fitView({ phase: 'upload.idle' }, input)), null);
});

test('S15u: tiny uncertainty gets sensible figures, exact value stays in title', () => {
  assert.equal(pm(-9.809999999999958, 2e-15, 'm/s^2'), '-9.81 \u00b1 2.0e-15 m/s\u00b2');
  const m = clone(input); m.output.gravity.value = -9.809999999999958; m.output.gravity.uncertainty = 2e-15;
  const v = fitView(done, m), out = renderFit(html, v);
  assert.ok(!v.rows[0].display.includes('9999999'));
  assert.ok(out.includes('title="' + v.rows[0].text + '"'));
});

test('S15u: what-if replaces the gravity source note; default path keeps the fitter note', () => {
  const L = 'SIMULATED what-if of your described setup; scale unverified; not measured from the clip';
  assert.equal(fitView(done, input, L).rows[0].evidence, L);
  assert.ok(!renderFit(html, fitView(done, input, L)).includes('synthetic virtual-lab fit'));
  assert.equal(fitView(done, input).rows[0].evidence, FIX.output.gravity.source.evidence);
});

test('S15u: residuals show a 10-row head and a native details expand with the rest', () => {
  const m = clone(input), r = m.output.fit.residuals, t = m.times;
  while (r.length < 25) { r.push(r[0]); t.push(t[0]); }
  const v = fitView(done, m), out = renderFit(html, v);
  assert.equal(out.split('<details').length - 1, 1); assert.match(out, /<summary>Show remaining 15 residuals<\/summary>/);
  assert.match(out, /first 10 of 25/);
  assert.equal(out.split('data-label="simulated"').length - 1, v.rows.length + 25); // every row still rendered (head + collapsed rest)
  assert.equal(renderFit(html, fitView(done, input)).includes('<details'), FIX.output.fit.residuals.length > 10);
});

test('S15u: 375px CSS lets long numbers wrap and grid children shrink', () => {
  const css = readFileSync(new URL('../../Build/web/src/workspace/workspace.css', import.meta.url), 'utf8');
  assert.match(css, /@media \(max-width: 520px\)[^@]*\.ws-fit-table th, \.ws-fit-table td \{ overflow-wrap: anywhere/);
  assert.match(css, /\.ws-fit > \* \{ min-width: 0; \}/);
});

test('null gravity (invalid covariance) shows unavailable, no invented number', () => {
  const m = clone(input); m.output.gravity = null;
  assert.match(fitView(done, m).rows[0].text, /unavailable/);
});
