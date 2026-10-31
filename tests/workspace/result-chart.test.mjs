// S15aw: result chart data mapping. Input is the real jobs.owner_measurement shape built from the tracked owner_clips.json.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resultChart, renderResultChart } from '../../Build/web/src/workspace/result-chart.mjs';
import { renderWorkspace } from '../../Build/web/src/workspace/view.mjs';

const clips = JSON.parse(readFileSync(new URL('../../Build/api/workspace/owner_clips.json', import.meta.url), 'utf8')).clips;
const rec = (id) => ({ clip_id: id, status: 'recorded', ...clips[id].measurement, series: clips[id].series });
const h = (type, props, ...children) => ({ type, props: props ?? {}, children: children.flat(Infinity) });
const strings = (n) => (typeof n === 'string' ? [n] : n?.children?.flatMap(strings) ?? []);
const find = (n, f) => (f(n) ? [n] : (n?.children ?? []).flatMap((c) => find(c, f)));

test('OWN05 PASS: points, prefix split and verdict come from the API verbatim', () => {
  const m = rec('OWN05'), c = resultChart(m);
  assert.equal(c.error, null);
  assert.equal(c.verdict, 'PASS');
  assert.equal(c.check, 'Held-out check PASS: chi2/dof = 2.32/3, p = 0.51');
  assert.deepEqual(c.points.map((p) => p.held_out), m.series.points.map((_, i) => i >= m.series.n_train));
  assert.match(c.summary, /RECORDED track points .*SIMULATED quadratic fit .*held-out RMSE 13 px\. Image pixels; scale unverified\.$/);
  for (const p of c.points) assert.ok(p.x >= 0 && p.x <= c.width && p.y >= 0 && p.y <= c.height); // geometry inside the viewBox
  assert.ok(c.predPath.startsWith('M') && c.fitPath.startsWith('M'));
  assert.ok(c.points.every((p, i) => i === 0 || p.y > c.points[i - 1].y)); // falling object: image y grows down, as in svg
});

test('every measured owner clip renders; FAIL verdict is shown, not hidden', () => {
  const ids = Object.keys(clips).filter((k) => clips[k].measurement);
  assert.ok(ids.length >= 1);
  for (const id of ids) assert.equal(resultChart(rec(id)).error, null, id);
  assert.equal(resultChart(rec('OWN01')).verdict, 'FAIL');
});

test('render: accessible svg + table fallback; numbers only from the series', () => {
  const m = rec('OWN05'), tree = renderResultChart(h, m);
  const svg = find(tree, (n) => n?.type === 'svg')[0];
  assert.equal(svg.props.role, 'img');
  assert.equal(find(svg, (n) => n?.type === 'desc').length, 1);
  assert.equal(find(tree, (n) => n?.type === 'tr').length, m.series.points.length + 1);
  const text = strings(tree).join('|');
  for (const p of m.series.points) assert.ok(text.includes(String(p.y_px)) && text.includes(String(p.t_s)));
  for (const w of ['RECORDED', 'SIMULATED', 'Scale unverified', 'Held-out check PASS']) assert.ok(text.includes(w), w);
  assert.doesNotMatch(text, /\u2014/); // no em dash
});

test('abstain or missing series -> no chart; malformed series -> explicit notice, not a guessed chart', () => {
  assert.equal(resultChart({ status: 'abstain' }), null);
  assert.equal(resultChart({ ...rec('OWN05'), series: undefined }), null);
  const bad = rec('OWN05'); bad.series = { ...bad.series, points: bad.series.points.map((p, i) => (i ? p : { ...p, y_px: 'x' })) };
  assert.match(resultChart(bad).error, /malformed/);
  assert.match(resultChart({ ...rec('OWN05'), series: { ...rec('OWN05').series, n_train: 99 } }).error, /malformed/);
});

test('S15ax: axis ticks carry units and take their values from series points (display rounding only)', () => {
  for (const id of ['OWN05', 'OWN01']) {
    const m = rec(id), c = resultChart(m), pts = m.series.points, n = m.series.n_train;
    const at = [pts[0], pts[n - 1], pts.at(-1)];
    assert.deepEqual(c.xTicks.map((t) => t.label), at.map((p) => Number(p.t_s.toFixed(3)) + ' s'), id);
    assert.deepEqual(c.yTicks.map((t) => t.label), at.map((p) => Math.round(p.y_px) + ' px'), id);
    for (const t of c.xTicks) assert.ok(t.x >= c.plot.left && t.x <= c.plot.right);
    for (const t of c.yTicks) assert.ok(t.y >= c.plot.top && t.y <= c.plot.bottom);
    assert.ok(c.splitX > c.plot.left && c.splitX < c.plot.right);
  }
});

test('S15ax: at report.owner the chart is the centre-stage hero; the side card keeps g + caveat text, no second chart', () => {
  const layout = { phase: 'report.owner', stages: [], viewport: { banner: null }, jobStatus: { label: 'Clip result', jobId: 'job_x', surface: null, error: null } };
  const ws = (phase, m) => renderWorkspace(h, { ...layout, phase }, { status: 'empty' }, null, null, undefined, undefined, undefined, undefined, undefined, undefined, undefined, { label: 'RECORDED', measurement: m });
  const slot = (tree, s) => find(tree, (n) => n?.props?.['data-slot'] === s)[0];
  const tree = ws('report.owner', { ...rec('OWN05'), caveat: 'CAVEAT verbatim' }); // caveat is added by jobs.owner_measurement, not owner_clips.json
  const stage = slot(tree, 'viewport'), panel = slot(tree, 'panel');
  assert.equal(stage.props['data-hero'], 'result');
  assert.equal(find(stage, (n) => n?.type === 'svg').length, 1);
  assert.equal(find(panel, (n) => n?.type === 'svg').length, 0);
  assert.equal(find(tree, (n) => n?.props?.id === 'ws-rc-t').length, 1); // svg title id stays unique
  const side = strings(panel).join('|');
  assert.ok(side.includes('g = 8.62 ± 1.28 m/s²') && side.includes('CAVEAT verbatim'), side);
  const fail = strings(slot(ws('report.owner', rec('OWN01')), 'viewport')).join('|');
  assert.match(fail, /Held-out check FAIL/);
  // abstain: no chart, ordinary empty viewport
  assert.equal(slot(ws('report.owner', { clip_id: 'OWN02', status: 'abstain', message: 'x' }), 'viewport').props['data-hero'], undefined);
});
