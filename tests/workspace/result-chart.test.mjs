// S15aw: result chart data mapping. Input is the real jobs.owner_measurement shape built from the tracked owner_clips.json.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resultChart, renderResultChart } from '../../Build/web/src/workspace/result-chart.mjs';

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
