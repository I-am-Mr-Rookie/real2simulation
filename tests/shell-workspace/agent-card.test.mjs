// S15ac: interview as a right-panel agent question card. Pure render with a tiny h (same pattern as shell-toggle.test.mjs);
// the reducer/contract is the unchanged S15d interview, so the same Q_* events and the same submitAnswers payload must come out.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { initialInterview, reduceInterview } from '../../Build/web/src/workspace/interview.mjs';
import { renderQuestionCard, renderWaiting, pendingOf, shouldAutoOpen, cardKey } from '../../Build/web/src/shell/agent-card.mjs';
import { renderShell, toolsOf } from '../../Build/web/src/shell/workspace-shell.mjs';
import { routeAction } from '../../Build/web/src/shell/PrivateWorkspace.mjs';

const FX = JSON.parse(readFileSync(new URL('../workspace/fixtures/interview-responses.json', import.meta.url), 'utf8'));
const run = (s, ...ev) => ev.reduce(reduceInterview, s);
const loaded = (name) => run(initialInterview(), { type: 'Q_LOADED', response: FX.responses[name], sceneId: FX.scene_id, toolOutputs: FX.tool_outputs });
const h = (type, props, ...children) => ({ type, props: props ?? {}, children: children.flat(Infinity).filter((c) => c != null && c !== false) });
const find = (n, pred, out = []) => { if (n && typeof n === 'object') { if (pred(n)) out.push(n); n.children?.forEach((c) => find(c, pred, out)); } return out; };
const textOf = (n) => (typeof n === 'string' ? n : n?.children?.map(textOf).join('') ?? '');
const cls = (t, c) => find(t, (n) => n.props.className === c);

test('card: labelled region, n/N, numbered options, Other free text, Continue; no Skip (contract has none)', () => {
  const s = run(loaded('authored-three-kinds'), { type: 'Q_CHIP', chipId: 'ball' }, { type: 'Q_SUBMIT' }, { type: 'Q_TEXT', text: 'hi' }, { type: 'Q_SUBMIT' });
  const sent = [];
  const t = renderQuestionCard(h, s, (a) => sent.push(a));
  assert.equal(t.type, 'section'); assert.equal(t.props['aria-labelledby'], 'r2s-q-h');
  assert.equal(find(t, (n) => n.props.id === 'r2s-q-h').length, 1);
  assert.equal(textOf(cls(t, 'r2s-qcount')[0]), '3/3');
  assert.equal(find(t, (n) => n.props.role === 'status' && n.props['aria-live'] === 'polite').length, 1);
  const opts = cls(t, 'r2s-qopt');
  assert.deepEqual(opts.map((o) => textOf(o)), ['1Table', '2Compare with 9.8 ± 0.1 m/s^2 (simulated)']); // tool-output label verbatim
  assert.match(textOf(cls(t, 'r2s-qother')[0]), /^Other/);
  assert.equal(textOf(cls(t, 'r2s-qsubmit')[0]), 'FinishCtrl+Enter'); // last question keeps the old Finish
  assert.equal(find(t, (n) => n.type === 'button' && /skip/i.test(textOf(n))).length, 0);
  assert.equal(textOf(find(t, (n) => n.type === 'summary')[0]), '2 answered'); // answered questions collapse above
  opts[0].props.onClick();
  const form = find(t, (n) => n.type === 'form')[0];
  assert.ok(form.props['aria-label']);
  form.props.onKeyDown({ key: '2', target: { tagName: 'BUTTON' }, preventDefault() {} });
  form.props.onKeyDown({ key: '2', target: { tagName: 'TEXTAREA' }, preventDefault() {} }); // typing digits is text, not a pick
  form.props.onKeyDown({ key: 'Enter', ctrlKey: true, target: { tagName: 'TEXTAREA' }, preventDefault() {} });
  cls(t, 'r2s-qback')[0].props.onClick();
  assert.deepEqual(sent, [{ type: 'Q_CHIP', chipId: 'table' }, { type: 'Q_CHIP', chipId: s.questions[2].chips[1].id }, { type: 'Q_SUBMIT' }, { type: 'Q_BACK' }]);
  const first = renderQuestionCard(h, loaded('authored-three-kinds'), () => {});
  assert.equal(textOf(cls(first, 'r2s-qsubmit')[0]), 'ContinueCtrl+Enter');
  assert.equal(textOf(cls(first, 'r2s-qcount')[0]), '1/3');
  assert.ok(find(renderQuestionCard(h, s), (n) => n.type === 'button').every((b) => b.props.disabled)); // inert without onAction
});

test('cardKey: 1..N only for existing options, modifiers ignored, Cmd+Enter submits', () => {
  const v = { chips: [{ id: 'a' }, { id: 'b' }] };
  assert.deepEqual(cardKey({ key: '1', target: {} }, v), { type: 'Q_CHIP', chipId: 'a' });
  assert.equal(cardKey({ key: '3', target: {} }, v), null);
  assert.equal(cardKey({ key: '1', altKey: true, target: {} }, v), null);
  assert.deepEqual(cardKey({ key: 'Enter', metaKey: true, target: {} }, v), { type: 'Q_SUBMIT' });
  assert.equal(cardKey({ key: 'Enter', target: {} }, v), null);
});

test('known-size free text (owner flow) is answerable in the card and Finish reaches submitAnswers exactly as before', async () => {
  let local = { interview: loaded('authored-three-kinds'), instruments: null };
  const calls = [];
  const ctl = { submitAnswers: async (a) => calls.push(a) };
  for (const a of [{ type: 'Q_CHIP', chipId: 'ball' }, { type: 'Q_SUBMIT' }]) local = await routeAction(ctl, local, a);
  const t = renderQuestionCard(h, local.interview, () => {});
  const ta = find(t, (n) => n.type === 'textarea')[0];
  assert.ok(ta); assert.equal(textOf(cls(t, 'r2s-qother')[0]), 'Your answer'); // free_text-only question: no "Other" wording
  for (const a of [{ type: 'Q_TEXT', text: 'book cover horizontal edge 20.28 cm' }, { type: 'Q_SUBMIT' }, { type: 'Q_CHIP', chipId: 'table' }, { type: 'Q_SUBMIT' }]) local = await routeAction(ctl, local, a);
  assert.equal(calls.length, 1);
  assert.deepEqual(calls[0].map((x) => x.text), [null, 'book cover horizontal edge 20.28 cm', null]);
  assert.equal(local.interview.status, 'complete');
  assert.equal(find(renderQuestionCard(h, local.interview, () => {}), (n) => n.type === 'form').length, 0);
});

test('centre waiting state, pending count on the Agent tool, badge only while the panel is closed', () => {
  const s = loaded('authored-three-kinds');
  assert.equal(pendingOf(s), 3); assert.equal(pendingOf(null), 0); assert.equal(pendingOf(initialInterview()), 0);
  let opened = 0;
  const w = renderWaiting(h, s, () => opened++);
  assert.equal(w.props.role, 'status'); assert.equal(w.props['aria-live'], 'polite');
  assert.match(textOf(w), /^Agent needs your answer\. Question 1 of 3: /);
  find(w, (n) => n.props['data-open'] === 'agent-card')[0].props.onClick(); assert.equal(opened, 1);
  assert.equal(renderWaiting(h, null, () => {}).children.length, 0); // live region stays mounted, empty
  const tools = toolsOf({ live: true, phase: 'interview.active', owner: true, jobId: 'j', uploadStatus: null, hasReport: false, pending: 3 });
  assert.match(tools[0].status, /^3 questions waiting\. Owner clip: no scene \(reconstruction not run\); interview in progress \(not a measurement\)$/);
  assert.equal(tools[0].target, 'r2s-q-h');
  const badge = (right) => find(renderShell(h, { title: 'T', left: true, right, tools, pending: 3, agent: renderQuestionCard(h, s, () => {}) }), (n) => n.props.className === 'r2s-badge');
  assert.equal(badge(false).length, 1); assert.equal(textOf(badge(false)[0]), '3 questions waiting');
  assert.equal(badge(true).length, 0);
  const open = renderShell(h, { title: 'T', left: true, right: true, tools, pending: 3, agent: renderQuestionCard(h, s, () => {}) });
  const panel = find(open, (n) => n.props.id === 'r2s-right')[0];
  assert.equal(cls(panel, 'r2s-qcard').length, 1);
});

test('auto-open: once per new round, never after the user closed it with questions pending', () => {
  assert.equal(shouldAutoOpen({ asking: true, newRound: true, userClosed: false }), true);
  assert.equal(shouldAutoOpen({ asking: true, newRound: true, userClosed: true }), false);
  assert.equal(shouldAutoOpen({ asking: true, newRound: false, userClosed: false }), false);
  assert.equal(shouldAutoOpen({ asking: false, newRound: true, userClosed: false }), false);
});

