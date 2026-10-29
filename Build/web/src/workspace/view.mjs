// S15b: workspace markup as a pure function of (layout, viewer status). h = React.createElement-compatible.
// The viewport host div has NO children: the viewer owns everything inside it.
import { VIEWER_STATUS_TEXT } from './layout.mjs';

export function renderWorkspace(h, layout, view, hostRef, onAction) {
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
      h('h2', null, jobStatus.label)),
    h('aside', { className: 'ws-job', 'data-slot': 'job-status', 'aria-label': 'Job status' },
      h('p', null, jobStatus.jobId ? 'Job ' + jobStatus.jobId : 'No job yet'),
      renderStatus(h, jobStatus.surface, onAction),
      err ? h('p', { className: 'ws-error', role: 'alert' }, err.code + ': ' + err.message) : null));
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

