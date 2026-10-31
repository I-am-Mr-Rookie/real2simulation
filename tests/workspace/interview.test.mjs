import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { initialInterview, reduceInterview, parseQuestions, interviewAnswers, interviewView, canSubmit, MAX_TEXT } from '../../Build/web/src/workspace/interview.mjs';
import { initialState, reduce } from '../../Build/web/src/workspace/workflow.mjs';
import { deps, jobReady } from '../../Build/web/src/workspace/fixtures.mjs';
import { layoutOf } from '../../Build/web/src/workspace/layout.mjs';
import { renderWorkspace, renderInterview } from '../../Build/web/src/workspace/view.mjs';

// Fixtures: every response was validated by contracts/agent/validate.py (evidence/S15/interview_fixtures.py --check).
const FX = JSON.parse(readFileSync(new URL('./fixtures/interview-responses.json', import.meta.url), 'utf8'));
const ctx = (name, extra = {}) => ({ type: 'Q_LOADED', response: FX.responses[name], sceneId: FX.scene_id, toolOutputs: FX.tool_outputs, ...extra });
const run = (s, ...events) => events.reduce(reduceInterview, s);
const loaded = (name) => run(initialInterview(), ctx(name));
const h = (type, props, ...children) => ({ type, props: props ?? {}, children: children.flat(Infinity) });
const find = (n, pred, out = []) => { if (n && typeof n === 'object') { if (pred(n)) out.push(n); n.children?.forEach((c) => find(c, pred, out)); } return out; };
const strings = (n) => (typeof n === 'string' ? [n] : n?.children?.flatMap(strings) ?? []);

test('every fixture response is a parseable interview round; number chip text comes from the tool output', () => {
  assert.deepEqual(Object.keys(FX.responses).sort(), ['authored-no-questions', 'authored-three-kinds', 'muse-b', 'muse-c', 'muse-d']);
  for (const [name, r] of Object.entries(FX.responses)) {
    const p = parseQuestions(r, { sceneId: FX.scene_id, toolOutputs: FX.tool_outputs });
    assert.ok(p.ok, name + ': ' + p.errors);
    assert.equal(p.questions.length, r.questions.length);
  }
  const q3 = parseQuestions(FX.responses['authored-three-kinds'], { sceneId: FX.scene_id, toolOutputs: FX.tool_outputs }).questions[2];
  assert.equal(q3.chips[1].label, 'Compare with 9.8 ± 0.1 m/s^2 (simulated)');
});

test('walk: chips -> free_text -> chips_and_free_text -> complete, with the answers handed out', () => {
  let s = loaded('authored-three-kinds');
  assert.equal(s.status, 'asking'); assert.equal(interviewView(s).progress, 'Question 1 of 3');
  assert.equal(interviewAnswers(s), null);
  // chips: submit needs a chip; selecting twice toggles; unknown chip ignored; free text ignored for a chips question
  const e = reduceInterview(s, { type: 'Q_SUBMIT' });
  assert.equal(e.index, 0); assert.match(e.error.message, /Choose an option/);
  assert.equal(reduceInterview(s, { type: 'Q_CHIP', chipId: 'nope' }), s);
  assert.equal(reduceInterview(s, { type: 'Q_TEXT', text: 'x' }), s);
  assert.equal(run(s, { type: 'Q_CHIP', chipId: 'ball' }, { type: 'Q_CHIP', chipId: 'ball' }).selected, null);
  s = run(s, { type: 'Q_CHIP', chipId: 'ball' }, { type: 'Q_CHIP', chipId: 'block' });
  assert.equal(s.selected, 'block'); assert.equal(interviewView(s).chips.filter((c) => c.selected).length, 1);
  s = run(s, { type: 'Q_SUBMIT' });
  // free_text: chips ignored, whitespace-only rejected
  assert.equal(s.index, 1); assert.equal(s.selected, null); assert.equal(interviewView(s).chips.length, 0);
  assert.equal(reduceInterview(s, { type: 'Q_CHIP', chipId: 'ball' }), s);
  const blank = run(s, { type: 'Q_TEXT', text: '   ' }, { type: 'Q_SUBMIT' });
  assert.equal(blank.index, 1); assert.match(blank.error.message, /Write an answer/);
  s = run(s, { type: 'Q_TEXT', text: '  dropped from the edge  ' }, { type: 'Q_SUBMIT' });
  // chips_and_free_text: a chip alone, text alone, or both are enough; nothing is not
  assert.equal(s.index, 2); assert.equal(canSubmit(s), false);
  assert.equal(canSubmit(run(s, { type: 'Q_TEXT', text: 'wooden table' })), true);
  s = run(s, { type: 'Q_CHIP', chipId: 'table' }, { type: 'Q_TEXT', text: 'near the wall' }, { type: 'Q_SUBMIT' });
  assert.equal(s.status, 'complete'); assert.equal(interviewView(s).progress, 'All questions answered.');
  assert.deepEqual(interviewAnswers(s), [
    { questionId: 'q-object', chipId: 'block', text: null },
    { questionId: 'q-notes', chipId: null, text: 'dropped from the edge' },
    { questionId: 'q-height', chipId: 'table', text: 'near the wall' }]);
  assert.deepEqual(interviewView(s).answers.map((a) => a.answer), ['Block', 'dropped from the edge', 'Table, near the wall']);
  assert.equal(reduceInterview(s, { type: 'Q_SUBMIT' }), s);
});

test('back restores the previous answer; reload only between rounds; later rounds append; reset clears', () => {
  let s = run(loaded('authored-three-kinds'), { type: 'Q_CHIP', chipId: 'ball' }, { type: 'Q_SUBMIT' }, { type: 'Q_TEXT', text: 'abc' }, { type: 'Q_SUBMIT' });
  s = run(s, { type: 'Q_BACK' });
  assert.equal(s.index, 1); assert.equal(s.text, 'abc'); assert.equal(s.answers.length, 1);
  s = run(s, { type: 'Q_BACK' });
  assert.equal(s.selected, 'ball'); assert.equal(s.answers.length, 0);
  assert.equal(reduceInterview(s, { type: 'Q_BACK' }), s);               // nothing before question 1
  assert.equal(reduceInterview(s, ctx('muse-b')), s);                      // agent cannot swap a question mid-answer
  let one = run(loaded('muse-b'), { type: 'Q_CHIP', chipId: 'drop-object' }, { type: 'Q_SUBMIT' });
  assert.equal(one.status, 'complete');
  assert.equal(run(one, { type: 'Q_BACK' }).selected, 'drop-object');       // complete -> reopen last
  const r2 = run(one, ctx('muse-c'), { type: 'Q_CHIP', chipId: 'ball' }, { type: 'Q_SUBMIT' });
  assert.deepEqual(interviewAnswers(r2).map((a) => a.questionId), ['q-object', 'object-choice']);
  const round2 = run(one, ctx('muse-c'));
  assert.equal(reduceInterview(round2, { type: 'Q_BACK' }), round2);        // back never crosses into a finished round
  assert.equal(run(loaded('authored-no-questions')).status, 'complete');
  assert.equal(run(r2, { type: 'Q_RESET' }).status, 'idle');
});

test('free text is capped, stripped of control characters and kept as plain text', () => {
  let s = run(loaded('authored-three-kinds'), { type: 'Q_CHIP', chipId: 'ball' }, { type: 'Q_SUBMIT' });
  s = run(s, { type: 'Q_TEXT', text: 'a\u0000b\u0007' + 'x'.repeat(MAX_TEXT + 50) });
  assert.equal(s.text.length, MAX_TEXT); assert.ok(s.text.startsWith('abx'));
  assert.equal(reduceInterview(s, { type: 'Q_TEXT', text: 5 }), s);
  assert.equal(run(s, { type: 'Q_TEXT', text: '<b>hi</b>' }, { type: 'Q_SUBMIT' }).answers[1].text, '<b>hi</b>'); // escaping is the renderer's job
});

test('malformed or untraced questions are rejected and leave the interview where it was', () => {
  const base = FX.responses['authored-three-kinds'];
  const mut = (f) => { const r = structuredClone(base); f(r); return r; };
  const bad = {
    'wrong scene': mut((r) => { r.scene_id = 'other-scene'; }),
    'digit in prompt': mut((r) => { r.questions[0].prompt[0].text = 'Drop from 2 m?'; }),
    'number word-free but unknown ref': mut((r) => { r.questions[2].chips[1].label[1].ref.quantity = 'mass'; }),
    'unknown tool output': mut((r) => { r.questions[2].chips[1].label[1].ref.tool_output_id = 'fit-missing'; }),
    'free_text with chips': mut((r) => { r.questions[1].chips = [{ id: 'x', label: [{ type: 'text', text: 'X' }] }]; }),
    'chips without chips': mut((r) => { r.questions[0].chips = []; }),
    'four questions': mut((r) => { r.questions.push(...structuredClone(r.questions), structuredClone(r.questions[0])); r.questions.forEach((q, i) => { q.id = 'q' + i; }); }),
    'seven chips': mut((r) => { r.questions[0].chips = 'abcdefg'.split('').map((c) => ({ id: c, label: [{ type: 'text', text: c }] })); }),
    'extra key': mut((r) => { r.questions[0].extra = 1; }),
    'bad kind': mut((r) => { r.questions[0].kind = 'radio'; }),
    'duplicate chip id': mut((r) => { r.questions[0].chips[1].id = 'ball'; }),
    'duplicate question id': mut((r) => { r.questions[1].id = 'q-object'; }),
    'bad id': mut((r) => { r.questions[0].id = '../x'; }),
    'empty prompt': mut((r) => { r.questions[0].prompt = []; }),
    'not a response': null,
  };
  for (const [why, r] of Object.entries(bad)) {
    const p = parseQuestions(r, { sceneId: FX.scene_id, toolOutputs: FX.tool_outputs });
    assert.equal(p.ok, false, why);
    const s0 = initialInterview(), s1 = run(s0, ctx('x', { response: r }));
    assert.equal(s1.status, 'idle', why); assert.equal(s1.error.code, 'INVALID_INPUT', why);
  }
  // an unlabelled quantity cannot back a number
  const outs = structuredClone(FX.tool_outputs); delete outs[0].quantities.gravity.source.label;
  assert.equal(parseQuestions(base, { sceneId: FX.scene_id, toolOutputs: outs }).ok, false);
  // a good load after a bad one clears the error
  assert.equal(run(run(initialInterview(), ctx('x', { response: null })), ctx('muse-b')).error, null);
});

test('markup: toggle chips, labelled textarea, actions report plain events; controls disabled without onAction', () => {
  const sent = [];
  let s = run(loaded('authored-three-kinds'), { type: 'Q_CHIP', chipId: 'ball' }, { type: 'Q_SUBMIT' }, { type: 'Q_TEXT', text: 'hi' }, { type: 'Q_SUBMIT' });
  const t = renderInterview(h, interviewView(s), (a) => sent.push(a));
  const chips = find(t, (n) => n.type === 'button' && n.props.className === 'ws-chip');
  assert.deepEqual(chips.map((c) => [c.children[0], c.props['aria-pressed']]), [['Table', false], ['Compare with 9.8 ± 0.1 m/s^2 (simulated)', false]]);
  chips[0].props.onClick();
  const ta = find(t, (n) => n.type === 'textarea')[0];
  assert.equal(ta.props.maxLength, MAX_TEXT); ta.props.onChange({ target: { value: 'v' } });
  const form = find(t, (n) => n.type === 'form')[0];
  let prevented = 0; form.props.onSubmit({ preventDefault: () => prevented++ });
  find(t, (n) => n.props.className === 'ws-back')[0].props.onClick();
  assert.deepEqual(sent, [{ type: 'Q_CHIP', chipId: 'table' }, { type: 'Q_TEXT', text: 'v' }, { type: 'Q_SUBMIT' }, { type: 'Q_BACK' }]);
  assert.equal(prevented, 1);
  assert.deepEqual(strings(find(t, (n) => n.type === 'legend')[0]), ['Release surface?']);
  assert.equal(find(t, (n) => n.props.className === 'ws-submit')[0].children[0], 'Finish');
  assert.equal(find(t, (n) => n.props.dangerouslySetInnerHTML).length, 0);
  assert.equal(find(t, (n) => n.type === 'li').length, 2);                 // two answers so far
  const inert = renderInterview(h, interviewView(s));
  assert.ok(find(inert, (n) => n.type === 'button').every((b) => b.props.disabled));
  s = run(s, { type: 'Q_CHIP', chipId: 'table' }, { type: 'Q_SUBMIT' });
  const done = renderInterview(h, interviewView(s), () => {});
  assert.equal(find(done, (n) => n.type === 'form').length, 0);
  assert.equal(find(done, (n) => n.props.className === 'ws-back').length, 1);
  assert.deepEqual(strings(find(done, (n) => n.props.className === 'ws-progress')[0]), ['All questions answered.']);
  const err = renderInterview(h, interviewView(run(loaded('muse-b'), { type: 'Q_SUBMIT' })), () => {});
  assert.equal(find(err, (n) => n.props.role === 'alert').length, 1);
});

test('panel: shown only in interview.active and only when an interview state is supplied', () => {
  const ready = reduce(reduce(initialState(), { type: 'UPLOAD_STARTED', jobId: 'synthetic-job-v1' }, deps), { type: 'JOB_UPDATE', job: jobReady(1) }, deps);
  assert.equal(ready.phase, 'interview.active');
  const draw = (state, iv) => renderWorkspace(h, layoutOf(state), { status: 'empty', error: null }, null, () => {}, iv);
  const panel = (t) => find(t, (n) => n.props['data-slot'] === 'panel')[0];
  assert.equal(find(panel(draw(ready, loaded('muse-d'))), (n) => n.props.className === 'ws-interview').length, 1);
  assert.equal(find(draw(ready), (n) => n.props.className === 'ws-interview').length, 0);
  assert.equal(find(draw(initialState(), loaded('muse-d')), (n) => n.props.className === 'ws-interview').length, 0);
  // the interview never advances the workspace graph; only a validated spec does
  assert.equal(reduce(ready, { type: 'INTERVIEW_SPEC', spec: {} }, deps).phase, 'interview.active');
});

test('interview.mjs stays pure: no imports, no DOM, network or model access', () => {
  const src = readFileSync(new URL('../../Build/web/src/workspace/interview.mjs', import.meta.url), 'utf8');
  assert.doesNotMatch(src, /^\s*import\s|\brequire\(|\bfetch\(|document\.|window\./m);
});
