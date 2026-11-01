// S15y: owner clip upload -> no_scene job (not a failure) -> scene-free known-size interview -> result stage with stored g ± u.
// Real controller/reducers/view; fetch replies mirror Build/api/workspace jobs.py + analysis.py (tests/api-workspace pins those).
import test from 'node:test';
import assert from 'node:assert/strict';
import { createController } from '../../Build/web/src/workspace/controller.mjs';
import { initialInterview, reduceInterview, interviewAnswers } from '../../Build/web/src/workspace/interview.mjs';
import { layoutOf } from '../../Build/web/src/workspace/layout.mjs';
import { renderWorkspace } from '../../Build/web/src/workspace/view.mjs';
import { readFileSync } from 'node:fs';

// S15az: real analysis.owner_live_fit output (fitter run on OWN05 stored points with two different answers)
const LIVE = JSON.parse(readFileSync(new URL('./fixtures/live-fit-own05.json', import.meta.url), 'utf8'));

const JOB = 'job_' + 'a'.repeat(32);
const KNOWN_SIZE = { id: 'known_size', kind: 'chips_and_free_text', prompt: [{ type: 'text', text: 'Name one object of known size in the fall plane and its length with units, e.g. book cover edge in cm.' }],
  chips: [{ id: 'owner_recorded', label: [{ type: 'text', text: 'the length recorded with this clip (owner-declared)' }] },
    { id: 'a4_short_edge', label: [{ type: 'text', text: 'A four paper, short edge' }] }, { id: 'card_long_edge', label: [{ type: 'text', text: 'Bank card, long edge' }] }] };
const OWN01 = { clip_id: 'OWN01', input_label: 'OWNER_RECORDED / RECORDED', status: 'recorded', label: 'RECORDED replay of a MEASURED result',
  g: 10.96, u: 0.77, unit: 'm/s^2', measured_label: 'MEASURED (owner clip OWN01)', source: 'evidence/S07/S07i/result-own01.json',
  caveat: 'Held-out prediction FAILS: held-out RMSE 23.0 px exceeds the 6 px pass threshold (S07h: 3 x the declared 2 px).',
  scale: { reference: 'book cover horizontal edge in fall plane', value_m: 0.2028, label: 'user-declared, not verified' } };
const OWN02 = { clip_id: 'OWN02', input_label: 'OWNER_RECORDED / RECORDED', status: 'abstain', label: 'UNCERTAIN: no measurement', message: 'g is not reported (abstain, not an error).' };
const h = (type, props, ...children) => ({ type, props: props ?? {}, children: children.flat(Infinity) });
const strings = (n) => (typeof n === 'string' ? [n] : n?.children?.flatMap(strings) ?? []);

async function ownerWalk(measurement, sizeText, liveFit, { chip = null, noSpec = false } = {}) {
  const calls = [];
  const spec = noSpec ? {} : { spec: { kind: 'owner_clip_scale', object: sizeText ?? 'A4 paper short edge', length_m: 0.2028, unit: 'm', label: 'user-declared, not verified' },
    setup_validated: false, label: 'scale user-declared, not verified; not setup-validated' };
  const routes = [
    [/uploads$/, { upload_id: 'up1', chunk_bytes: 1024, committed_bytes: 0 }],
    [/chunks\/\d+$/, { committed_bytes: 4 }],
    [/complete$/, { upload: { sha256: 'f'.repeat(64), job_id: JOB }, job: { job_id: JOB, status: 'no_scene', label: 'no scene: owner clip, scene reconstruction not run' },
      provenance: { executor: 'none', label: 'no scene: owner clip, scene reconstruction not run', live: false, recorded_stages: [], stage_labels: {}, measurement } }],
    [/questions$/, { schema_version: 'agent-response/1.0.0', scene_id: JOB, questions: [KNOWN_SIZE] }],
    [/spec$/, { ok: true, owner_clip: true, ...spec, measurement, user_scale: { status: 'declared', object: sizeText ?? 'A4 paper short edge', length_m: 0.2028, label: 'user-declared, not verified' },
      ...(liveFit ? { live_fit: liveFit } : {}) }],
  ];
  const f = async (url, init) => {
    calls.push({ url, method: init.method, body: typeof init.body === 'string' ? JSON.parse(init.body) : null });
    const data = routes.find(([re]) => re.test(url))?.[1];
    return { ok: !!data, status: data ? 200 : 404, json: async () => data ?? { code: 'NOT_FOUND', message: 'x' } };
  };
  const ctl = createController({ fetch: f, onChange: () => {} });
  await ctl.upload(new File([new Uint8Array([1, 2, 3, 4])], 'own.mp4', { type: 'video/mp4' }));
  assert.equal(ctl.state.phase, 'interview.active'); // not upload.failed
  assert.equal(ctl.state.error, null);
  assert.equal(ctl.state.scene, null); // no fake scene
  assert.ok(!calls.some((c) => /\/jobs\//.test(c.url))); // nothing to poll
  assert.match(layoutOf(ctl.state).jobStatus.label, /^Owner clip: no scene \(reconstruction not run\)/);
  let iv = reduceInterview(initialInterview(), { type: 'Q_LOADED', response: await ctl.loadQuestions(), sceneId: ctl.state.owner.jobId });
  assert.deepEqual(iv.questions.map((q) => q.id), ['known_size']);
  assert.equal(iv.questions[0].chips.length, 3); // S15bf: chips plus free text
  iv = reduceInterview(reduceInterview(iv, chip ? { type: 'Q_CHIP', chipId: chip } : { type: 'Q_TEXT', text: sizeText }), { type: 'Q_SUBMIT' });
  await ctl.submitAnswers(interviewAnswers(iv));
  assert.deepEqual(calls.at(-1).body, { answers: { known_size: chip ? { chip } : { text: sizeText } } });
  if (noSpec) return { phase: ctl.state.phase };
  assert.equal(ctl.state.phase, 'report.owner');
  const layout = layoutOf(ctl.state, { audience: 'signed-in' });
  const tree = renderWorkspace(h, layout, { status: 'empty', error: null }, null, undefined, undefined, undefined, undefined, undefined, undefined,
    undefined, undefined, ctl.snapshot().provenance);
  const all = strings(tree).join('|');
  assert.doesNotMatch(all, /Upload failed|DEPENDENCY_UNAVAILABLE|needs attention|Start a new upload/);
  const tree0 = tree.children.find((c) => c?.props['data-slot'] === 'stage-nav');
  const navStatus = tree0.children[0].children.map((li) => li.props['data-status']);
  assert.deepEqual(navStatus, liveFit?.status === 'ok' ? ['done', 'done', 'done', 'done', 'current'] : ['done', 'done', 'skipped', 'skipped', 'current']);
  const count = (n) => (n?.props?.className === 'ws-measurement' ? 1 : 0) + (n?.children?.reduce?.((a, c) => a + count(c), 0) ?? 0);
  assert.equal(count(tree), 1); // S15z: result card once, not in both panels
  const panel = strings(tree.children.find((c) => c?.props['data-slot'] === 'panel')).join('|');
  return { panel, all };
}

test('owner clip OWN01: no-scene job, known-size interview, stored g ± u as the result stage', async () => {
  const { panel, all } = await ownerWalk(OWN01, 'book cover edge, 20.28 cm');
  assert.match(panel, /Clip result \(owner clip; no scene; fit not run\)/);
  assert.match(panel, /g = 10\.96 ± 0\.77 m\/s²/);
  assert.match(panel, /held-out RMSE 23\.0 px exceeds the 6 px pass threshold/);
  assert.match(panel, /Your known size: book cover edge, 20\.28 cm = 0\.2028 m \(user-declared, not verified\)/);
  assert.match(all, /no scene: owner clip, scene reconstruction not run/);
});

test('owner clip OWN02: abstain result, missing size is an abstain not an error', async () => {
  const { panel } = await ownerWalk(OWN02, null, undefined, { chip: 'a4_short_edge' }); // S15bf: a chip answer, sent as the chip id only
  assert.match(panel, /UNCERTAIN: no measurement/);
  assert.match(panel, /A4 paper short edge/);
  assert.doesNotMatch(panel, /g = /);
});

test('S15bf R-D F1: an owner reply without a validated spec never reaches the owner result stage', async () => {
  const { phase } = await ownerWalk(OWN01, 'book cover edge, 20.28 cm', undefined, { noSpec: true });
  assert.notEqual(phase, 'report.owner');
});

test('S15az owner clip OWN05: live fitter result after the answer; a different answer changes scale and g; missing points abstain', async () => {
  const [a, b] = Object.values(LIVE.answers);
  assert.notEqual(a.g, b.g);
  for (const f of [a, b]) {
    const { panel, all } = await ownerWalk(LIVE.measurement, 'book cover edge, 20.28 cm', f);
    assert.ok(panel.includes('g = ' + f.g.toFixed(2) + ' \u00b1 ' + f.u.toFixed(2) + ' m/s\u00b2')); // display rounding of the fitter output only
    assert.match(panel, /SIMULATED fit \(fitter, run now\) to RECORDED MEASURED SAM 3\.1 track points/);
    assert.match(panel, /Fit: done \(run now on the server\)/);
    assert.ok(panel.includes('rmse = ' + f.rmse_px.toFixed(2) + ' px; dof = ' + f.dof));
    assert.ok(panel.includes('Held-out residuals (px, ' + f.n_held_out + ' points not fitted): ' + f.held_out_residuals_px.map((v) => v.toFixed(1)).join(', ')));
    assert.ok(panel.includes('Scale: ' + f.scale.label));
    assert.match(panel, /Recorded reference \(precomputed, S07m\): \|g = 8\.62 ± 1\.28/);
    assert.match(all, /Track: RECORDED \(precomputed SAM 3\.1, not run live\)/);
    assert.doesNotMatch(all, /\u2014/); // no em dashes in visible text
  }
  const { panel } = await ownerWalk(LIVE.measurement, 'book cover edge, 20.28 cm', LIVE.missing);
  assert.match(panel, /Live fit not run: No stored track points/);
  assert.doesNotMatch(panel, /SIMULATED fit/);
});

test('S15bb OWN05 live fit: headline u is the recorded S07m budget plus fit scatter, never the fit-only u; breakdown shown', async () => {
  const a = LIVE.answers['book cover edge, 20.28 cm'];
  assert.ok(a.u >= LIVE.measurement.u, a.u + ' < recorded ' + LIVE.measurement.u); // 1.29 >= 1.28 (fit-only was 0.15)
  assert.ok(a.u > a.u_fit);
  assert.ok(Math.abs(Math.hypot(...Object.values(a.u_terms)) - a.u) < 1e-12); // terms sum in quadrature to the headline
  const { panel, all } = await ownerWalk(LIVE.measurement, 'book cover edge, 20.28 cm', a);
  assert.ok(panel.includes('g = ' + a.g.toFixed(2) + ' \u00b1 ' + a.u.toFixed(2) + ' m/s\u00b2'));
  assert.ok(panel.includes('Uncertainty: fit ' + a.u_terms.fit.toFixed(2) + ', detection ' + a.u_terms.detection.toFixed(2)));
  assert.match(panel, /centroid vs box \d\.\d\d, scale \d\.\d\d \(quadrature\); fit scatter combined in quadrature with the recorded S07m budget terms/);
  assert.match(panel, /scale unverified/i);
  assert.match(panel, /held-out residuals are a check, not an uncertainty term/);
  assert.doesNotMatch(all, /\u2014/);
});

test('S15bb D7: owner clip (no scene) renders no empty 3D viewport placeholder; a scene job (RM04) keeps its viewport', () => {
  const vp = (t) => t.children.find((c) => c?.props?.id === 'ws-viewport');
  const blank = { status: 'empty', error: null };
  const own = { phase: 'interview.active', stages: [], viewport: { request: null, key: null, banner: null }, jobStatus: { label: 'Owner clip', error: null } };
  for (const m of [LIVE.measurement, OWN02]) {
    const t = renderWorkspace(h, own, blank, null, undefined, undefined, undefined, undefined, undefined, undefined, undefined, undefined, { measurement: m });
    assert.equal(vp(t), undefined);
    assert.doesNotMatch(strings(t).join('|'), /No scene yet/);
  }
  const rm04 = { ...own, viewport: { request: { kind: 'viewer', scene: { id: 'RM04' } }, key: 'RM04|inspect|signed-in', banner: null } };
  const t = renderWorkspace(h, rm04, blank, null, undefined, undefined, undefined, undefined, undefined, undefined, undefined, undefined, { executor: 'recorded' });
  assert.equal(vp(t)?.props['data-slot'], 'viewport');
});
