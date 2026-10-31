// S15y: owner clip upload -> no_scene job (not a failure) -> scene-free known-size interview -> result stage with stored g ± u.
// Real controller/reducers/view; fetch replies mirror Build/api/workspace jobs.py + analysis.py (tests/api-workspace pins those).
import test from 'node:test';
import assert from 'node:assert/strict';
import { createController } from '../../Build/web/src/workspace/controller.mjs';
import { initialInterview, reduceInterview, interviewAnswers } from '../../Build/web/src/workspace/interview.mjs';
import { layoutOf } from '../../Build/web/src/workspace/layout.mjs';
import { renderWorkspace } from '../../Build/web/src/workspace/view.mjs';

const JOB = 'job_' + 'a'.repeat(32);
const KNOWN_SIZE = { id: 'known_size', kind: 'free_text', chips: [], prompt: [{ type: 'text', text: 'Name one object of known size in the fall plane and its length with units, e.g. book cover edge in cm.' }] };
const OWN01 = { clip_id: 'OWN01', input_label: 'OWNER_RECORDED / RECORDED', status: 'recorded', label: 'RECORDED replay of a MEASURED result',
  g: 10.96, u: 0.77, unit: 'm/s^2', measured_label: 'MEASURED (owner clip OWN01)', source: 'evidence/S07/S07i/result-own01.json',
  caveat: 'Held-out prediction FAILS: held-out RMSE 23.0 px exceeds the 6 px pass threshold (S07h: 3 x the declared 2 px).',
  scale: { reference: 'book cover horizontal edge in fall plane', value_m: 0.2028, label: 'user-declared, not verified' } };
const OWN02 = { clip_id: 'OWN02', input_label: 'OWNER_RECORDED / RECORDED', status: 'abstain', label: 'UNCERTAIN: no measurement', message: 'g is not reported (abstain, not an error).' };
const h = (type, props, ...children) => ({ type, props: props ?? {}, children: children.flat(Infinity) });
const strings = (n) => (typeof n === 'string' ? [n] : n?.children?.flatMap(strings) ?? []);

async function ownerWalk(measurement, sizeText) {
  const calls = [];
  const routes = [
    [/uploads$/, { upload_id: 'up1', chunk_bytes: 1024, committed_bytes: 0 }],
    [/chunks\/\d+$/, { committed_bytes: 4 }],
    [/complete$/, { upload: { sha256: 'f'.repeat(64), job_id: JOB }, job: { job_id: JOB, status: 'no_scene', label: 'no scene: owner clip, scene reconstruction not run' },
      provenance: { executor: 'none', label: 'no scene: owner clip, scene reconstruction not run', live: false, recorded_stages: [], stage_labels: {}, measurement } }],
    [/questions$/, { schema_version: 'agent-response/1.0.0', scene_id: JOB, questions: [KNOWN_SIZE] }],
    [/spec$/, { ok: true, owner_clip: true, measurement, user_scale: sizeText ? { status: 'declared', object: sizeText, length_m: 0.2028, label: 'user-declared, not verified' }
      : { status: 'abstain', label: 'UNCERTAIN: no usable known size; metric scale unknown' } }],
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
  iv = reduceInterview(reduceInterview(iv, { type: 'Q_TEXT', text: sizeText ?? 'none' }), { type: 'Q_SUBMIT' });
  await ctl.submitAnswers(interviewAnswers(iv));
  assert.deepEqual(calls.at(-1).body, { answers: { known_size: { text: sizeText ?? 'none' } } });
  assert.equal(ctl.state.phase, 'report.owner');
  const layout = layoutOf(ctl.state, { audience: 'signed-in' });
  const tree = renderWorkspace(h, layout, { status: 'empty', error: null }, null, undefined, undefined, undefined, undefined, undefined, undefined,
    undefined, undefined, ctl.snapshot().provenance);
  const all = strings(tree).join('|');
  assert.doesNotMatch(all, /Upload failed|DEPENDENCY_UNAVAILABLE|needs attention|Start a new upload/);
  assert.deepEqual(layout.stages.map((s) => s.status), ['done', 'done', 'skipped', 'skipped', 'current']);
  const count = (n) => (n?.props?.className === 'ws-measurement' ? 1 : 0) + (n?.children?.reduce?.((a, c) => a + count(c), 0) ?? 0);
  assert.equal(count(tree), 1); // S15z: result card once, not in both panels
  const panel = strings(tree.children.find((c) => c?.props['data-slot'] === 'panel')).join('|');
  return { panel, all };
}

test('owner clip OWN01: no-scene job, known-size interview, stored g ± u as the result stage', async () => {
  const { panel, all } = await ownerWalk(OWN01, 'book cover edge, 20.28 cm');
  assert.match(panel, /Clip result \(owner clip; no scene, run or fit\)/);
  assert.match(panel, /g = 10\.96 ± 0\.77 m\/s\^2/);
  assert.match(panel, /held-out RMSE 23\.0 px exceeds the 6 px pass threshold/);
  assert.match(panel, /Your known size: book cover edge, 20\.28 cm = 0\.2028 m \(user-declared, not verified\)/);
  assert.match(all, /no scene: owner clip, scene reconstruction not run/);
});

test('owner clip OWN02: abstain result, missing size is an abstain not an error', async () => {
  const { panel } = await ownerWalk(OWN02, null);
  assert.match(panel, /UNCERTAIN: no measurement/);
  assert.match(panel, /UNCERTAIN: no usable known size/);
  assert.doesNotMatch(panel, /g = /);
});
