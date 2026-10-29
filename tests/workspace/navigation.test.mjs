import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { sidebarOf, parseReport, reportView, renderSidebar, renderReport } from '../../Build/web/src/workspace/navigation.mjs';
import { initialInterview, reduceInterview } from '../../Build/web/src/workspace/interview.mjs';
import { initialState, reduce, PHASES } from '../../Build/web/src/workspace/workflow.mjs';
import { STAGES } from '../../Build/web/src/workspace/layout.mjs';
import { renderWorkspace } from '../../Build/web/src/workspace/view.mjs';
import { layoutOf } from '../../Build/web/src/workspace/layout.mjs';

const fx = (n) => JSON.parse(readFileSync(new URL('./fixtures/' + n, import.meta.url), 'utf8'));
const REPORT = fx('report-output.json').report, AGENT = fx('interview-responses.json');
const clone = (o) => JSON.parse(JSON.stringify(o));
const h = (type, props, ...children) => ({ type, props: props ?? {}, children: children.flat(Infinity) });
const find = (n, pred, out = []) => { if (n && typeof n === 'object') { if (pred(n)) out.push(n); n.children?.forEach((c) => find(c, pred, out)); } return out; };
const strings = (n) => (typeof n === 'string' ? [n] : n?.children?.flatMap(strings) ?? []);
const at = (phase) => ({ ...initialState(), phase });
const item = (items, id) => items.find((i) => i.id === id);

test('fixture report is current Build.reports output (public interface)', () => {
  const r = spawnSync('python', ['evidence/S15/report_fixtures.py', '--check'], { encoding: 'utf8' });
  if (r.error) return; // python unavailable; generator --check is the authority
  assert.equal(r.status, 0, r.stderr);
});

test('sidebar: one entry per stage, exactly one current, every event is reducer-legal in that phase', () => {
  for (const p of PHASES) {
    const s = at(p), items = sidebarOf(s, { report: REPORT });
    assert.deepEqual(items.map((i) => i.id), STAGES);
    assert.equal(items.filter((i) => i.current).length, 1, p);
    for (const i of items) if (i.event) assert.notEqual(reduce(s, i.event, {}), s, p + ' -> ' + i.id);
  }
});

test('sidebar: navigation moves fit <-> report and back to interview; run/fit are never directly reachable', () => {
  let s = at('fit.done');
  assert.deepEqual(item(sidebarOf(s, { report: REPORT }), 'report').event, { type: 'REPORT_OPEN' });
  assert.equal(item(sidebarOf(s, { report: REPORT }), 'run').event, null);
  s = reduce(s, item(sidebarOf(s, { report: REPORT }), 'report').event, {});
  assert.equal(s.phase, 'report.open');
  assert.deepEqual(item(sidebarOf(s, { report: REPORT }), 'fit').event, { type: 'REPORT_CLOSE' });
  const back = item(sidebarOf(s, { report: REPORT }), 'interview');
  assert.ok(back.destructive && /clears/.test(back.note));
  assert.equal(reduce(s, back.event, {}).phase, 'interview.active');
  assert.equal(reduce(s, { type: 'REPORT_CLOSE' }, {}).phase, 'fit.done');
});

test('sidebar: report is gated by fit.done and by having a report; never from earlier phases', () => {
  assert.equal(item(sidebarOf(at('fit.done'), {}), 'report').event, null);
  assert.match(item(sidebarOf(at('fit.done'), {}), 'report').note, /not received/i);
  for (const p of ['upload.idle', 'interview.active', 'run.done', 'fit.running']) assert.equal(item(sidebarOf(at(p), { report: REPORT }), 'report').event, null, p);
});

test('agent wiring: interview progress from the agent contract shows on the sidebar entry', () => {
  const m = reduceInterview(initialInterview(), { type: 'Q_LOADED', response: AGENT.responses['authored-three-kinds'], sceneId: AGENT.scene_id, toolOutputs: AGENT.tool_outputs });
  const it = item(sidebarOf(at('interview.active'), { interview: m }), 'interview');
  assert.match(it.detail, /1 of 3/);
  assert.equal(item(sidebarOf(at('interview.active'), {}), 'interview').detail, null);
});

test('report: parses fixture; numbers rendered with unit, uncertainty and label; placeholders resolved', () => {
  const v = reportView(at('report.open'), REPORT), g = REPORT.numbers.gravity;
  assert.equal(v.error, null);
  const all = v.sections.flatMap((s) => s.text).join(' ');
  assert.ok(all.includes(g.value + ' \u00b1 ' + g.uncertainty + ' m/s^2 (simulated)'));
  assert.ok(!/\{\{/.test(all) && !/\{\{/.test(v.title));
  assert.deepEqual(v.labels, ['simulated']);
  assert.ok(all.includes('from 8 (simulated) observations'), 'dimensionless unit "1" is not printed');
  assert.equal(reportView(at('fit.done'), REPORT).show, false);
});

test('report: rejects bare numbers, unknown placeholders, bad labels, extra keys, bad schema; shows an error, not a partial report', () => {
  const bad = (f) => { const r = clone(REPORT); f(r); return r; };
  const cases = [bad((r) => { r.sections[0].text[0] += ' about 9.8'; }), bad((r) => { r.sections[0].text[0] = '{{nope}}'; }),
    bad((r) => { r.numbers.rmse.label = 'measured-ish'; }), bad((r) => { r.extra = 1; }), bad((r) => { r.schema = 'r2s.report/2'; }),
    bad((r) => { delete r.numbers.gravity.uncertainty; }), bad((r) => { r.numbers.rmse.value = Infinity; })];
  for (const r of cases) { assert.throws(() => parseReport(r)); const v = reportView(at('report.open'), r); assert.match(v.error, /rejected/); assert.equal(v.sections, undefined); }
  assert.match(reportView(at('report.open'), null).error, /No report/);
});

test('view: sidebar and report render; buttons report events; absent when not injected', () => {
  const s = at('report.open'), l = layoutOf(s), sent = [];
  const tree = renderWorkspace(h, l, { status: 'ready', error: null }, null, (a) => sent.push(a), null, null, null, null, null, sidebarOf(s, { report: REPORT }), reportView(s, REPORT));
  const nav = find(tree, (n) => n.props['data-nav'] === 'sidebar');
  assert.equal(nav.length, 1);
  const btn = find(nav[0], (n) => n.type === 'button' && n.children.includes('Fit'))[0];
  btn.props.onClick(); assert.deepEqual(sent, [{ type: 'REPORT_CLOSE' }]);
  assert.ok(find(tree, (n) => n.props.className === 'ws-report').length === 1);
  const plain = renderWorkspace(h, l, { status: 'ready', error: null }, null, null);
  assert.equal(find(plain, (n) => n.props['data-nav'] === 'sidebar').length, 0);
  assert.ok(find(nav[0], (n) => n.type === 'button').every((b) => b.props.disabled === true || b.props.disabled === false));
});

test('boundary: new modules import only workspace siblings (agent/report reached via contracts, not imports)', () => {
  const dir = 'Build/web/src/workspace/';
  const imports = [...readFileSync(dir + 'navigation.mjs', 'utf8').matchAll(/^import .* from '([^']+)'/gm)].map((m) => m[1]);
  for (const i of imports) assert.match(i, /^\.\//, i);
  for (const f of readdirSync(dir).filter((x) => x.endsWith('.mjs'))) for (const m of readFileSync(dir + f, 'utf8').matchAll(/^import .* from '([^']+)'/gm)) assert.doesNotMatch(m[1], /agent|reports/, f);
});
