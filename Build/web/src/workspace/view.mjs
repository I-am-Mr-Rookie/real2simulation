// S15b: workspace markup as a pure function of (layout, viewer status). h = React.createElement-compatible.
// The viewport host div has NO children: the viewer owns everything inside it.
import { VIEWER_STATUS_TEXT } from './layout.mjs';
import { interviewView } from './interview.mjs';
import { templateView } from './template.mjs';
import { renderTemplate } from './template-view.mjs';

export function renderWorkspace(h, layout, view, hostRef, onAction, interview, template) {
  const { stages, viewport, jobStatus } = layout;
  const err = view.error ?? jobStatus.error;
  return h('div', { className: 'ws', 'data-phase': layout.phase },
    h('nav', { className: 'ws-stages', 'data-slot': 'stage-nav', 'aria-label': 'Workspace stages' },
      h('ol', null, ...stages.map((s) => h('li', { key: s.id, 'data-status': s.status, 'aria-current': s.status === 'current' ? 'step' : undefined },
        s.label + (s.failed ? ' (needs attention)' : ''))))),
    h('section', { className: 'ws-viewport', 'data-slot': 'viewport', 'aria-label': 'Scene viewport' },
      viewport.banner ? h('p', { className: 'ws-banner', role: 'note' }, viewport.banner) : null,
      h('div', { className: 'ws-host', ref: hostRef, 'data-viewer-status': view.status }),
      h('p', { className: 'ws-status', role: 'status', 'aria-live': 'polite' }, VIEWER_STATUS_TEXT[view.status] ?? VIEWER_STATUS_TEXT.error)),
    h('section', { className: 'ws-panel', 'data-slot': 'panel', 'aria-label': 'Stage panel' },
      h('h2', null, jobStatus.label),
      interview && layout.phase === 'interview.active' ? renderInterview(h, interviewView(interview), onAction) : null,
      template && ['interview.active', 'run.ready'].includes(layout.phase) ? renderTemplate(h, templateView(template), layout.phase, onAction) : null),
    h('aside', { className: 'ws-job', 'data-slot': 'job-status', 'aria-label': 'Job status' },
      h('p', null, jobStatus.jobId ? 'Job ' + jobStatus.jobId : 'No job yet'),
      renderStatus(h, jobStatus.surface, onAction),
      err ? h('p', { className: 'ws-error', role: 'alert' }, err.code + ': ' + err.message) : null));
}

// S15d: interview panel. Chips are toggle buttons, free text a labelled textarea; everything is text (no raw HTML). Reports { type, ... }
// through onAction; the host feeds it to reduceInterview (interview.mjs).
export function renderInterview(h, v, onAction) {
  const send = (a) => onAction?.(a);
  const asking = v.status === 'asking';
  return h('section', { className: 'ws-interview', 'data-status': v.status, 'aria-label': 'Interview' },
    v.answers.length ? h('ol', { className: 'ws-qa', 'aria-label': 'Answers so far' },
      ...v.answers.map((a, i) => h('li', { key: i }, h('span', { className: 'ws-q' }, a.prompt), ' ', h('strong', { className: 'ws-a' }, a.answer)))) : null,
    h('p', { className: 'ws-progress', role: 'status', 'aria-live': 'polite' }, v.progress),
    asking ? h('form', { className: 'ws-question', onSubmit: (e) => { e?.preventDefault?.(); send({ type: 'Q_SUBMIT' }); } },
      h('fieldset', null,
        h('legend', null, v.prompt),
        v.chips.length ? h('div', { className: 'ws-chips' }, ...v.chips.map((c) => h('button', { key: c.id, type: 'button', className: 'ws-chip',
          'aria-pressed': c.selected, disabled: !onAction, onClick: () => send({ type: 'Q_CHIP', chipId: c.id }) }, c.label))) : null,
        v.freeText ? h('label', { className: 'ws-freetext' }, 'Your answer',
          h('textarea', { rows: 3, maxLength: v.freeText.maxLength, value: v.freeText.value, disabled: !onAction,
            onChange: (e) => send({ type: 'Q_TEXT', text: e.target.value }) })) : null),
      v.error ? h('p', { className: 'ws-error', role: 'alert' }, v.error.message) : null,
      h('div', { className: 'ws-actions' },
        v.canBack ? h('button', { type: 'button', className: 'ws-back', disabled: !onAction, onClick: () => send({ type: 'Q_BACK' }) }, 'Back') : null,
        h('button', { type: 'submit', className: 'ws-submit', 'aria-disabled': !v.canSubmit, disabled: !onAction }, v.last ? 'Finish' : 'Next')))
      : v.canBack ? h('button', { type: 'button', className: 'ws-back', disabled: !onAction, onClick: () => send({ type: 'Q_BACK' }) }, 'Back') : null);
}

// S15c: job-stage timeline, event log, failure/partial-state surface and retry. Text only (no raw HTML). The retry button reports
// { type } through onAction; the host supplies payload (new jobId / seed / sessionId) and dispatches to the reducer.
export function renderStatus(h, sf, onAction) {
  if (!sf) return null;
  const f = sf.failure;
  return h('div', { className: 'ws-status-surface' },
    sf.timeline.length ? h('ol', { className: 'ws-timeline', 'aria-label': 'Job stages' },
      ...sf.timeline.map((t) => h('li', { key: t.id, 'data-status': t.status }, t.label))) : null,
    sf.inFlight ? h('p', { className: 'ws-inflight' }, sf.inFlight) : null,
    sf.events.length ? h('ul', { className: 'ws-events', 'aria-label': 'Job events' }, ...sf.events.map((e, i) => h('li', { key: i }, e))) : null,
    f ? h('div', { className: 'ws-failure', 'data-kind': f.kind, 'data-stage': f.stage },
      h('h3', null, f.title), h('p', null, f.advice),
      f.kept.length ? h('p', { className: 'ws-kept' }, 'Kept: ' + f.kept.join('; ')) : null,
      f.lost.length ? h('p', { className: 'ws-lost' }, 'Not available: ' + f.lost.join('; ')) : null,
      f.retry ? h('button', { type: 'button', className: 'ws-retry', 'data-event': f.retry.event, disabled: !onAction, onClick: () => onAction?.({ type: f.retry.event }) }, f.retry.label)
        : h('p', { className: 'ws-noretry' }, 'Retry is not available for this error.')) : null);
}

