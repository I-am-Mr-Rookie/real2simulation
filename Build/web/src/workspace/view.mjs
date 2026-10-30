// S15b: workspace markup as a pure function of (layout, viewer status). h = React.createElement-compatible.
// The viewport host div has NO children: the viewer owns everything inside it.
import { VIEWER_STATUS_TEXT } from './layout.mjs';
import { interviewView } from './interview.mjs';
import { templateView } from './template.mjs';
import { renderTemplate } from './template-view.mjs';
import { renderRun } from './run-view.mjs';
import { renderInstruments } from './instrument-view.mjs';
import { renderFit } from './fit-view.mjs';
import { renderSidebar, renderReport } from './navigation.mjs';

export function renderWorkspace(h, layout, view, hostRef, onAction, interview, template, run, instruments, fit, sidebar, report, provenance, whatIf) {
  const { stages, viewport, jobStatus } = layout;
  // S15q: a viewer LOAD_FAILED must not hide a job/API error (the live spec 422 was masked this way)
  const errs = [view.error, jobStatus.error].filter((e, i, a) => e && (i === 0 || e !== a[0]));
  const specError = layout.phase === 'interview.active' ? jobStatus.error : null;
  const stageError = /\.failed$/.test(layout.phase) ? jobStatus.error : null; // S15r: say why run/fit failed, not just 'Run failed.'
  return h('div', { className: 'ws', 'data-phase': layout.phase },
    h('nav', { className: 'ws-stages', 'data-slot': 'stage-nav', 'aria-label': 'Workspace stages' },
      h('ol', null, ...stages.map((s) => h('li', { key: s.id, 'data-status': s.status, 'aria-current': s.status === 'current' ? 'step' : undefined },
        s.label + (s.failed ? ' (needs attention)' : ''))))),
    sidebar ? renderSidebar(h, sidebar, onAction) : null,
    h('section', { className: 'ws-viewport', 'data-slot': 'viewport', 'aria-label': 'Scene viewport' },
      viewport.banner ? h('p', { className: 'ws-banner', role: 'note' }, viewport.banner) : null,
      h('div', { className: 'ws-host', ref: hostRef, 'data-viewer-status': view.status }),
      h('p', { className: 'ws-status', role: 'status', 'aria-live': 'polite' }, VIEWER_STATUS_TEXT[view.status] ?? VIEWER_STATUS_TEXT.error)),
    h('section', { className: 'ws-panel', 'data-slot': 'panel', 'aria-label': 'Stage panel' },
      h('h2', null, jobStatus.label),
      whatIf && /^(run|fit|report)\./.test(layout.phase) ? h('p', { className: 'ws-whatif', role: 'note', 'data-label': 'what-if' }, whatIf) : null,
      stageError ? h('p', { className: 'ws-error', 'data-stage-error': layout.phase }, stageError.code + ': ' + stageError.message) : null,
      interview && layout.phase === 'interview.active' ? renderInterview(h, interviewView(interview), onAction) : null,
      specError ? h('div', { className: 'ws-failure', 'data-stage': 'spec' },
        h('p', { className: 'ws-error', role: 'alert' }, specError.code + ': ' + specError.message),
        h('button', { type: 'button', className: 'ws-retry', 'data-event': 'SPEC_RETRY', disabled: !onAction, onClick: () => onAction?.({ type: 'SPEC_RETRY' }) }, 'Retry')) : null,
      template && ['interview.active', 'run.ready'].includes(layout.phase) ? renderTemplate(h, templateView(template), layout.phase, onAction) : null,
      run ? renderRun(h, run, onAction) : null,
      instruments ? renderInstruments(h, instruments, onAction) : null,
      fit ? renderFit(h, fit) : null,
      report ? renderReport(h, report) : null),
    h('aside', { className: 'ws-job', 'data-slot': 'job-status', 'aria-label': 'Job status' },
      h('p', null, jobStatus.jobId ? 'Job ' + jobStatus.jobId : 'No job yet'),
      provenance ? renderProvenance(h, provenance) : null,
      renderStatus(h, jobStatus.surface, onAction),
      ...errs.map((e, i) => h('p', { key: 'err' + i, className: 'ws-error', role: 'alert' }, e.code + ': ' + e.message))));
}

// S15q: server job provenance (jobs.py recorded replay) shown verbatim: per-stage RECORDED labels + understand UTC. Text only.
export function renderProvenance(h, p) {
  const labels = p.stage_labels && typeof p.stage_labels === 'object' ? Object.entries(p.stage_labels) : [];
  const utc = typeof p.understand?.recorded_utc === 'string' ? p.understand.recorded_utc : null;
  return h('div', { className: 'ws-provenance', 'data-executor': String(p.executor ?? ''), 'aria-label': 'Job provenance' },
    h('p', null, String(p.label ?? 'Provenance') + (p.live === false ? ' (not a live run)' : '')),
    labels.length ? h('ul', null, ...labels.map(([s, l]) => h('li', { key: s }, s + ': ' + String(l) + (s === 'understand' && utc ? ' @ ' + utc : '')))) : null,
    typeof p.note === 'string' ? h('p', { className: 'ws-note' }, p.note) : null);
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

