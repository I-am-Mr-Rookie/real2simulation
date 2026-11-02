// Offline checks of actual DEV receipts, not a substitute for browser QA.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
const D = fileURLToPath(new URL('.', import.meta.url));
const read = n => JSON.parse(fs.readFileSync(D + n, 'utf8'));
const before = read('room-result-before.json'), after = read('room-result-after-a4.json');
assert.equal(before.room.shell.kept.length, 7);
assert.equal(before.room.shell.dropped, 97);
assert.equal(before.scene.objects.filter(o => o.shape?.type === 'mesh').length, 3);
assert(before.scene.objects.every(o => after.scene.objects.some(x => x.id === o.id)));
assert(after.room.shell && after.room.shell.rescaled_by !== 1);
assert.equal(after.room.scale.status, 'MEASURED'); // QA wiring reference, NOT physical calibration.
assert.equal(read('quota-21.json').status, 429);
assert.equal(read('sol-rejected.json').status, 422);
assert.deepEqual(read('history-confirmed.json'), { start: 20, undo: 21, redo: 20 });
assert(read('mobile.json').every(m => m.scrollWidth <= m.clientWidth));
assert(read('visible-copy.json').every(m => !m.emDashLines.length));
const table = before.scene.objects.find(o => o.id === 'room-object-1');
const restY = table.position[1] + table.size[1] / 2 + 0.025;
const drops = ['table-drop-traces.json', 'table-drop-repeat-traces.json'].map(n => {
  const t = read(n).traces.find(t => t.object_id === 'ball-1');
  return { file: n, last: t.samples.at(-1), expected_rest_y: restY,
    rests_on_table: Math.abs(t.samples.at(-1).p[1] - restY) < 0.01 };
});
assert(drops.every(d => !d.rests_on_table)); // Confirmed regression, not a passing table-rest acceptance.
const sh = before.room.shell, yaw = sh.yaw_deg * Math.PI / 180;
const c = Math.cos(yaw), s = Math.sin(yaw);
const bounds = [0, 1].map(a => sh.walls.filter(w => w.axis === a).map(w => w.plane).sort((a, b) => a - b));
const furniture = before.scene.objects.filter(o => o.id.startsWith('room-object-')).map(o => {
  const [x, , z] = o.position, p = [x * c - z * s, x * s + z * c];
  return { id: o.id, wall_frame_position: p, inside_wall_envelope: p.every((v, i) => v >= bounds[i][0] && v <= bounds[i][1]) };
});
const openings = sh.openings.map(h => {
  const w = sh.walls[h.wall];
  return { ...h, intersects_wall_rectangle: Math.min(h.along[1], w.span[1]) > Math.max(h.along[0], w.span[0]) &&
    Math.min(h.y[1], w.height) > Math.max(h.y[0], 0) };
});
const geometry = { wall_frame_bounds: bounds, wall_height: sh.walls[0].height,
  furniture_inside_count: furniture.filter(x => x.inside_wall_envelope).length, furniture,
  openings_intersecting_count: openings.filter(x => x.intersects_wall_rectangle).length, openings };
fs.writeFileSync(D + 'geometry-summary.json', JSON.stringify(geometry, null, 2));
const receipts = [...read('results.json').responses, ...read('lab-results.json').responses];
const turns = receipts.filter(r => r.path.endsWith('/turn') && r.status === 200).map(r => ({ utc: r.utc, ...JSON.parse(r.body) }));
assert(turns.some(t => t.model === 'meta-models/muse-spark-open-1026'));
assert(turns.some(t => t.model === 'muse-spark-1.3'));
const rows = [
  { utc_interval: ['2026-11-02T01:59:52Z', '2026-11-02T02:03:54Z'], model: 'MapAnything / L4', units: 'failed capacity wait, 240.351 s + idle estimate', estimated_usd: 0.32353896 },
  { utc_interval: ['2026-11-02T02:03:54Z', '2026-11-02T02:04:23Z'], model: 'MapAnything / A10G', units: '29.513 s + idle estimate', estimated_usd: 0.34179889 },
  { utc_interval: ['2026-11-02T02:04:23Z', sh.created_at], model: 'sam-3.1 image', units: sh.sam_calls + ' image calls', estimated_usd: sh.sam_cost_usd },
  ...sh.kept.filter(k => k.sf3d).map(k => ({ utc_interval: ['2026-11-02T02:04:23Z', sh.created_at], model: 'Stable Fast 3D / ' + k.sf3d.gpu,
    units: k.id + ', wall ' + k.sf3d.wall_s + ' s + idle estimate', estimated_usd: k.sf3d.estimated_usd })),
  { utc_interval: ['2026-11-02T02:06:09Z', '2026-11-02T02:06:19Z'], model: 'sam-3.1 video', units: read('mode-b-result.json').experiment.result.video_frames_processed + ' frames',
    estimated_usd: read('mode-b-result.json').experiment.result.cost_usd },
  ...turns.map(t => { const [a, b] = t.model === 'meta-models/muse-spark-open-1026' ? [1.25e-6, 4.25e-6] : [1e-6, 5e-6];
    return { receipt_utc: t.utc, model: t.model, units: t.usage, estimated_usd: Number((t.usage.input_tokens * a + t.usage.output_tokens * b).toFixed(8)) }; })
];
const total = Number(rows.reduce((s, r) => s + r.estimated_usd, 0).toFixed(8));
assert(total < 2);
fs.writeFileSync(D + 'paid-ledger.json', JSON.stringify({ basis: 'API job estimates and aggregate token usage at Build/agent/core.py rates; not provider billing. Shell sub-call exact UTC timestamps unavailable: intervals enclose the calls. Do not insert duplicate rows into the runtime ledger.', cap_usd: 2, total_estimated_usd: total, rows }, null, 2));
console.log(JSON.stringify({ evidence_checks: 'PASS', table_rest_acceptance: 'FAIL (2/2)', furniture_inside: geometry.furniture_inside_count,
  openings_intersecting: geometry.openings_intersecting_count, estimated_usd: total, agent_turns: turns.length }, null, 2));
