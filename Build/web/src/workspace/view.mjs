// S15b: workspace markup as a pure function of (layout, viewer status). h = React.createElement-compatible.
// The viewport host div has NO children: the viewer owns everything inside it.
import { VIEWER_STATUS_TEXT } from './layout.mjs';

export function renderWorkspace(h, layout, view, hostRef) {
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
      err ? h('p', { className: 'ws-error', role: 'alert' }, err.code + ': ' + err.message) : null));
}
