// S15ac: the interview as a right-panel agent question card (Q21: P4 card, O2 in-context questions, P1 waiting state).
// Pure render over the unchanged S15d reducer view (interviewView); events are the same Q_* actions routeAction already handles.
// No Skip: the interview contract has no skip event, so none is offered. Back stays (Q_BACK exists).
import { interviewView } from '../workspace/interview.mjs';

// Questions still unanswered in the current round (0 when not asking).
export const pendingOf = (s) => (s?.status === 'asking' ? s.questions.length - s.index : 0);

// Auto-open the panel once per new round of questions, unless the user closed it while questions were pending.
export const shouldAutoOpen = ({ asking, newRound, userClosed }) => asking && newRound && !userClosed;

// Keys inside the card: 1..9 pick an option (not while typing), Ctrl/Cmd+Enter continues. Returns a Q_* action or null.
export function cardKey(e, v) {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') return { type: 'Q_SUBMIT' };
  const typing = /^(TEXTAREA|INPUT)$/.test(e.target?.tagName ?? '');
  if (typing || e.ctrlKey || e.metaKey || e.altKey || !/^[1-9]$/.test(e.key)) return null;
  const c = v.chips[Number(e.key) - 1];
  return c ? { type: 'Q_CHIP', chipId: c.id } : null;
}

// s = interview state; refs.cardHead receives focus when the panel opens on a pending question.
export function renderQuestionCard(h, s, onAction, refs = {}) {
  const v = interviewView(s);
  const send = (a) => onAction?.(a);
  const asking = v.status === 'asking';
  const n = asking ? s.index + 1 + '/' + s.questions.length : null;
  return h('section', { className: 'r2s-qcard', 'data-status': v.status, 'data-qid': asking ? s.questions[s.index]?.id : undefined, 'aria-labelledby': 'r2s-q-h' },
    h('div', { className: 'r2s-qcard-head' },
      h('h3', { id: 'r2s-q-h', ref: refs.cardHead, tabIndex: -1 }, 'Agent question'),
      n ? h('span', { className: 'r2s-qcount', 'aria-hidden': true }, n) : null),
    v.answers.length ? h('details', { className: 'r2s-answered' },
      h('summary', null, v.answers.length + ' answered'),
      h('ol', { 'aria-label': 'Answers so far' }, ...v.answers.map((a, i) => h('li', { key: i }, h('span', null, a.prompt), ' ', h('strong', null, a.answer))))) : null,
    h('p', { className: 'r2s-qprogress', role: 'status', 'aria-live': 'polite' }, v.progress),
    asking ? h('form', { className: 'r2s-qform', 'aria-label': 'Answer the agent question',
      onSubmit: (e) => { e?.preventDefault?.(); send({ type: 'Q_SUBMIT' }); },
      onKeyDown: (e) => { const a = cardKey(e, v); if (a) { e.preventDefault?.(); send(a); } } },
      h('fieldset', null,
        h('legend', null, v.prompt),
        v.chips.length ? h('ol', { className: 'r2s-qopts' }, ...v.chips.map((c, i) => h('li', { key: c.id },
          h('button', { type: 'button', className: 'r2s-qopt', 'aria-pressed': c.selected, disabled: !onAction, 'aria-keyshortcuts': i < 9 ? String(i + 1) : undefined,
            onClick: () => send({ type: 'Q_CHIP', chipId: c.id }) }, h('kbd', { 'aria-hidden': true }, String(i + 1)), h('span', null, c.label))))) : null,
        v.freeText ? h('label', { className: 'r2s-qother' }, v.chips.length ? 'Other (your own answer)' : 'Your answer',
          h('textarea', { rows: 3, maxLength: v.freeText.maxLength, value: v.freeText.value, disabled: !onAction,
            'aria-invalid': v.error ? true : undefined, 'aria-describedby': v.error ? 'r2s-q-error' : undefined,
            onChange: (e) => send({ type: 'Q_TEXT', text: e.target.value }) })) : null),
      v.error ? h('p', { id: 'r2s-q-error', className: 'ws-error', role: 'alert' }, v.error.message) : null,
      h('div', { className: 'r2s-qactions' },
        v.canBack ? h('button', { type: 'button', className: 'r2s-qback', disabled: !onAction, onClick: () => send({ type: 'Q_BACK' }) }, 'Back') : null,
        h('button', { type: 'submit', className: 'r2s-qsubmit', 'aria-disabled': !v.canSubmit, disabled: !onAction, 'aria-keyshortcuts': 'Control+Enter Meta+Enter' },
          v.last ? 'Finish' : 'Continue', h('kbd', { 'aria-hidden': true }, 'Ctrl+Enter'))))
      : v.canBack ? h('button', { type: 'button', className: 'r2s-qback', disabled: !onAction, onClick: () => send({ type: 'Q_BACK' }) }, 'Back') : null);
}

// Centre P1 state: non-blocking; the scene preview and stage content stay below. Always-mounted live region so arrivals are announced.
export function renderWaiting(h, s, onOpen) {
  const k = pendingOf(s);
  return h('div', { className: 'r2s-wait-live', role: 'status', 'aria-live': 'polite' },
    k ? h('div', { className: 'r2s-waiting', 'data-pending': k },
      h('span', { className: 'r2s-pulse', 'aria-hidden': true }),
      h('p', null, h('strong', null, 'Agent needs your answer.'), ' Question ' + (s.index + 1) + ' of ' + s.questions.length + ': ' + s.questions[s.index].prompt),
      h('button', { type: 'button', className: 'r2s-iconbtn', 'data-open': 'agent-card', 'aria-controls': 'r2s-right', onClick: onOpen }, 'Answer in agent panel')) : null);
}
