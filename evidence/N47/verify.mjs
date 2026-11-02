// Offline checks of captured DEV outputs. No network, inference or application changes.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
const dir = new URL('.', import.meta.url);
const read = name => JSON.parse(fs.readFileSync(new URL(name, dir), 'utf8').replace(/^\uFEFF/, ''));
const text = name => fs.readFileSync(new URL(name, dir), 'utf8');
const checks = [];
const check = (name, fn) => { fn(); checks.push({ name, passed: true }); };
const oldRoom = read('old-room-after-shell.json');
const freshRoom = read('new-room-result.json');
const status = read('new-room-status.json').job;
const originalDrops = [
  ['f1-centre-drop-traces.json', 'room-object-1', 0.44235],
  ['f1-table3-traces.json', 'room-object-3', 0.45985],
].map(([file, table, expected_y]) => ({ file, table, expected_y, trace: read(file).traces[0] }));
const targets = read('f1-refreshed-rest-targets.json');
const refreshed = read('f1-refreshed-tables-traces.json').traces;
const drops = [...originalDrops, ...targets.map(t => ({ file: 'f1-refreshed-tables-traces.json', table: t.table,
  expected_y: t.expectedRestY, trace: refreshed.find(x => x.object_id === t.ball_id) }))];
check('F1 original and regenerated SF3D table centres retain dropped balls', () => {
  for (const d of drops) {
    const samples = d.trace.samples, last = samples.at(-1), prior = samples.find(s => s.t >= last.t - 1);
    assert(last.t >= 4);
    assert(Math.abs(last.p[1] - d.expected_y) < 0.001);
    assert(Math.hypot(...last.p.map((v, i) => v - prior.p[i])) < 0.001);
  }
});
check('F2 saved and newly built rooms report unobserved walls and no openings', () => {
  for (const r of [oldRoom, freshRoom]) {
    assert(r.room.shell.walls.every(w => w.status === 'not observed'));
    assert.equal(r.room.shell.openings.length, 0);
    assert(!r.scene.objects.some(o => o.id.startsWith('wall-')));
  }
});
const turns = read('r3-results.json').responses.filter(r => r.path.endsWith('/turn')).map(r => JSON.parse(r.body));
const openAnswer = turns.find(t => !t.tool_calls.length);
check('F3 saved Muse Open and disclosed answering model agree', () => {
  assert.match(text('16-saved-muse-open.txt'), /Standard: Muse Open/);
  assert.equal(openAnswer.model, 'meta-models/muse-spark-open-1026');
  assert.match(text('r3-17-F3-open-answer-model.txt'), /Answered by meta-models\/muse-spark-open-1026/);
});
const files = read('new-files-final.json').files, projects = read('new-projects-final.json').projects;
const file = files.find(f => f.id === status.file_id);
check('F4 upload and room retain the selected new Room project', () => {
  assert(status.project_id);
  assert.equal(file.project_id, status.project_id);
  assert(projects.some(p => p.id === status.project_id && p.mode === 'room'));
});
const edits = read('mode-a-delete-undo.json');
check('Mode A deletes only the created ball and Undo restores the same object set', () => {
  assert(edits.before.includes(edits.created_object_id));
  assert(!edits.deleted.includes(edits.created_object_id));
  assert.deepEqual(edits.deleted, edits.before.filter(id => id !== edits.created_object_id));
  assert.deepEqual(edits.undone, edits.before);
});
const agent = read('mode-a-agent-turn.json');
check('Mode A agent ran the simulated experiment with tool-produced uncertainty', () => {
  const run = agent.tool_calls.find(t => t.name === 'lab_run').output;
  assert.equal(run.status, 'ok');
  assert.equal(run.label, 'SIMULATED');
  assert(run.results[0].g.uncertainty > 0);
});
const experiment = read('mode-b-result.json').experiment;
check('Mode B completed hosted tracking and a fit with uncertainty', () => {
  assert.equal(experiment.status, 'done');
  assert(experiment.result.trajectory.t_s.length > 0);
  assert(experiment.result.quantity.uncertainty > 0);
  assert.match(text('29-mobile-mode-b-fit.txt'), /scale unverified/);
});
const baseline = read('mode-b-replay-baseline-traces.json').traces[0];
const redo = read('mode-b-redo-traces.json').traces[0];
check('Mode B redo changes simulated gravity while preserving measured source', () => {
  assert.notDeepEqual(baseline.gravity, redo.gravity);
  assert.deepEqual(read('mode-b-replay-scene-before.json').objects, read('mode-b-redo-scene.json').objects);
  const i = baseline.samples.findIndex(s => s.t >= 0.2);
  assert(Math.abs(baseline.samples[i].p[1] - redo.samples[i].p[1]) > 0.01);
});
const ledger = read('runtime-ledger-window.json');
const spend = ledger.reduce((sum, r) => sum + r.actual, 0) / 1e8;
check('All captured paid calls settled below the task cap, including failed SF3D', () => {
  assert(ledger.every(r => Number.isInteger(r.actual)));
  assert(spend <= 1.5);
  assert.equal(ledger.filter(r => r.label === 'N31 sf3d').length, 6);
  assert.equal(ledger.filter(r => r.label.includes('N39 sam-3.1')).length, 144);
});
const domain = read('custom-domain.json');
check('Custom-domain signed-in room API matches the primary domain', () => {
  assert.equal(domain.room_api_status, 200);
  assert.equal(domain.same_json, true);
  assert.equal(domain.tls_ignore_errors, false);
});
const screenshots = fs.readdirSync(dir).filter(n => n.endsWith('.png')).sort().map(name => ({ name,
  sha256: crypto.createHash('sha256').update(fs.readFileSync(new URL(name, dir))).digest('hex') }));
const results = {
  run_id: 'N47-orch292', status: 'DONE', qa_acceptance: 'FAIL: caption overlap remains',
  checked_at: new Date().toISOString(), browser: { engine: 'Playwright Chromium', headed: true, version: domain.chromium,
    viewports: [{ width: 1280, height: 900 }, { width: 375, height: 812 }] },
  hosts: [domain.primary, domain.custom],
  account_ids: ['user_3LWziQJxcsdCLbV2bCKATtu7KMg', domain.authenticated_account_id],
  rechecks: { F1: 'FIXED', F2: 'FIXED', F3: 'FIXED', F4: 'FIXED', F5: 'STILL OPEN' },
  findings: [
    { id: 'N47-1', priority: 'P2', title: 'SF3D furniture remains visibly distorted', receipt: 'r3-22-mode-a-agent-experiment.png' },
    { id: 'N47-2', priority: 'P2', title: 'Fresh room took over eleven minutes, with one SF3D timeout and box fallback', receipt: 'new-room-result.json' },
    { id: 'N47-3', priority: 'P3', title: 'F5 captions are larger but overlap at 375 px', receipt: 'r3-23-F5-mobile-room-captions.png' },
  ],
  F1: drops.map(d => ({ table: d.table, receipt: d.file, expected_y: d.expected_y, last: d.trace.samples.at(-1) })),
  F2: { old_shell: oldRoom.room.shell, new_shell: freshRoom.room.shell },
  F3: { saved_mode: 'open', answering_model: openAnswer.model },
  F4: { project_id: status.project_id, file_id: file.id, job_id: status.job_id, file_project_id: file.project_id },
  mode_a: { completed: true, room_job_id: status.job_id,
    duration_s: (Date.parse(status.updated_at) - Date.parse(status.created_at)) / 1000,
    agent_result: agent.tool_calls[0].output, delete_undo: edits },
  mode_b: { completed: true, experiment_id: experiment.id, result: experiment.result.quantity,
    scale: experiment.result.scale, baseline_gravity: baseline.gravity, redo_gravity: redo.gravity },
  paid: { total_settled_estimate_usd: spend, cap_usd: 1.5, calls: ledger.length,
    receipt: 'runtime-ledger-window.json', provider_invoice_verified: false },
  custom_domain: domain, checks,
  limitations: ['No physical calibration or ground-truth accuracy claim', 'Phone-experiment workflow used an approved Pexels surrogate, not an owner phone recording',
    'Screenshots retained locally, not committed', 'Transient recorder resets recovered without rerunning paid jobs',
    'One health-request recorder timeout was not diagnosed as a product failure'],
};
fs.writeFileSync(new URL('results.json', dir), JSON.stringify(results, null, 2) + '\n');
fs.writeFileSync(new URL('screenshots.json', dir), JSON.stringify(screenshots, null, 2) + '\n');
console.log(JSON.stringify({ checks: checks.length, passed: true, paid_usd: spend, screenshots: screenshots.length }));
