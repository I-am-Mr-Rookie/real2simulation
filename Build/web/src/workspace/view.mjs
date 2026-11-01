import { dash } from './display.mjs';
// S15b: workspace markup as a pure function of (layout, viewer status). h = React.createElement-compatible.
// The viewport host div has NO children: the viewer owns everything inside it.
import { VIEWER_STATUS_TEXT } from './layout.mjs';
import { interviewView } from './interview.mjs';
import { templateView } from './template.mjs';
import { renderTemplate } from './template-view.mjs';
import { renderRun } from './run-view.mjs';
import { renderInstruments } from './instrument-view.mjs';
import { renderFit } from './fit-view.mjs';
import { renderResultChart } from './result-chart.mjs';
import { renderSidebar, renderReport } from './navigation.mjs';

export function renderWorkspace(h, layout, view, hostRef, onAction, interview, template, run, instruments, fit, sidebar, report, provenance, whatIf) {
  const { viewport } = layout;
  // S15az (Gate D D1): after the answer the server ran the fitter on the RECORDED track, so Fit is done and Run says what it was.
  // Overridden here, not in layout.mjs (S15ba owns it); applies only when live_fit came back ok.
  const liveFit = layout.phase === 'report.owner' && provenance?.measurement?.live_fit?.status === 'ok' ? provenance.measurement.live_fit : null;
  const stages = liveFit ? layout.stages.map((s) => (s.id === 'fit' ? { ...s, label: 'Fit', status: 'done' }
    : s.id === 'run' ? { ...s, label: String(liveFit.track_label), status: 'done' } : s)) : layout.stages;
  const jobStatus = liveFit ? { ...layout.jobStatus, label: 'Clip result (owner clip; no scene; fit run now on RECORDED track points)' } : layout.jobStatus;
  // S15q: a viewer LOAD_FAILED must not hide a job/API error (the live spec 422 was masked this way)
  const errs = [view.error, jobStatus.error].filter((e, i, a) => e && (i === 0 || e !== a[0]));
  const specError = layout.phase === 'interview.active' ? jobStatus.error : null;
  // S15r: say why run/fit failed, not just 'Run failed.'; S15t: a report 422 leaves fit.done, say it there too
  const stageError = /\.failed$|^fit\.done$/.test(layout.phase) ? jobStatus.error : null;
  // S15ax: an owner clip has a measurement but no scene: its result chart takes the centre stage; the side card stays text
  const hero = layout.phase === 'report.owner' && provenance?.measurement ? renderResultChart(h, provenance.measurement) : null;
  // S15bb (Gate D D7): an owner clip has no scene, so no empty 3D viewport placeholder; scene jobs (no measurement) keep it
  const noViewport = !hero && !viewport.request && provenance?.measurement;
  return h('div', { className: 'ws', 'data-phase': layout.phase },
    h('nav', { className: 'ws-stages', 'data-slot': 'stage-nav', 'aria-label': 'Workspace stages' },
      h('ol', null, ...stages.map((s) => h('li', { key: s.id, 'data-status': s.status, 'aria-current': s.status === 'current' ? 'step' : undefined, title: s.status === 'skipped' ? 'Not run' : undefined },
        // S15an: skipped = dash icon (CSS) + tooltip; the "(not run)" wording stays in the DOM for screen readers.
        ...(s.status === 'skipped' && s.label.endsWith(' (not run)') ? [s.label.slice(0, -10), h('span', { className: 'r2s-sr' }, ' (not run)')] : [s.label + (s.failed ? ' (needs attention)' : '')]))))),
    sidebar ? renderSidebar(h, sidebar, onAction) : null,
    noViewport ? null : h('section', { id: 'ws-viewport', tabIndex: -1, className: 'ws-viewport', 'data-slot': 'viewport', 'data-hero': hero ? 'result' : undefined, 'aria-label': hero ? 'Clip result chart' : 'Scene viewport' },
      viewport.banner ? h('p', { className: 'ws-banner', role: 'note' }, viewport.banner) : null,
      hero,
      h('div', { className: 'ws-host', ref: hostRef, 'data-viewer-status': view.status }),
      h('p', { className: hero ? 'ws-status r2s-sr' : 'ws-status', role: 'status', 'aria-live': 'polite' }, VIEWER_STATUS_TEXT[view.status] ?? VIEWER_STATUS_TEXT.error)),
    h('section', { id: 'ws-panel', tabIndex: -1, className: 'ws-panel', 'data-slot': 'panel', 'aria-label': 'Stage panel' },
      // S15l: tabIndex -1 makes the heading the focus target after a stage change (react.mjs restoreFocus)
      h('h2', { id: 'ws-panel-heading', tabIndex: -1 }, jobStatus.label),
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
      run?.next ? h('div', { className: 'ws-actions', 'data-slot': 'next-step' },
        h('button', { type: 'button', className: 'ws-submit', 'data-event': run.next.event, disabled: !onAction, onClick: () => onAction?.({ type: run.next.event }) }, run.next.label)) : null,
      report ? renderReport(h, report) : null,
      layout.phase === 'report.owner' && provenance?.measurement ? renderMeasurement(h, provenance.measurement, !hero) : null),
    h('aside', { id: 'ws-job', tabIndex: -1, className: 'ws-job', 'data-slot': 'job-status', 'aria-label': 'Job status' },
      h('p', null, jobStatus.jobId ? 'Job ' + jobStatus.jobId : 'No job yet'),
      // S15z: at report.owner the stage panel already shows the result card; keep only a one-line pointer here
      provenance ? renderProvenance(h, provenance, layout.phase === 'report.owner') : null,
      renderStatus(h, jobStatus.surface, onAction),
      ...errs.map((e, i) => renderError(h, e, i, layout.phase, onAction))));
}

export const NOT_APPROVED = 'This clip is not on the approved list. Try a demo clip from the library; your own videos cannot be processed in this build.';
// S15bd: upload-stage errors only. Non-allowlisted clip: plain words, code kept small. Service down: visible "Try again" (re-runs the last upload).
function renderError(h, e, i, phase, onAction) {
  const key = 'err' + i, up = phase === 'upload.idle';
  if (up && e.code === 'INVALID_INPUT') return h('p', { key, className: 'ws-error', role: 'alert' }, NOT_APPROVED + ' ', h('small', { className: 'ws-code' }, e.code));
  if (up && e.code === 'DEPENDENCY_UNAVAILABLE') return h('div', { key, className: 'ws-failure', 'data-stage': 'upload' },
    h('p', { className: 'ws-error', role: 'alert' }, e.code + ': ' + e.message),
    h('button', { type: 'button', className: 'ws-retry', 'data-event': 'UPLOAD_RETRY', disabled: !onAction, onClick: () => onAction?.({ type: 'UPLOAD_RETRY' }) }, 'Try again'));
  return h('p', { key, className: 'ws-error', role: 'alert' }, e.code + ': ' + e.message);
}

// S15q: server job provenance (jobs.py recorded replay) shown verbatim: per-stage RECORDED labels + understand UTC. Text only.
export function renderProvenance(h, p, measurementShownElsewhere = false) {
  const labels = p.stage_labels && typeof p.stage_labels === 'object' ? Object.entries(p.stage_labels) : [];
  const utc = typeof p.understand?.recorded_utc === 'string' ? p.understand.recorded_utc : null;
  return h('div', { className: 'ws-provenance', 'data-executor': String(p.executor ?? ''), 'aria-label': 'Job provenance' },
    h('p', null, dash(p.label ?? 'Provenance') + (p.live === false ? ' (not a live run)' : '')),
    labels.length ? h('ul', null, ...labels.map(([s, l]) => h('li', { key: s }, s + ': ' + dash(l) + (s === 'understand' && utc ? ' @ ' + utc : '')))) : null,
    typeof p.note === 'string' ? h('p', { className: 'ws-note' }, p.note) : null,
    // S15az (Gate D D6): no result before the user's known-size answer; the stage panel shows it at report.owner
    p.measurement && typeof p.measurement === 'object' ? h('p', { className: 'ws-note' }, measurementShownElsewhere ? 'Clip result: shown in the stage panel.' : 'Clip result: shown after you answer the known-size question.') : null);
}

// S15az: fitter output from analysis.owner_live_fit, shown verbatim (display rounding only); an error status shows its message, no number.
function renderLiveFit(h, f) {
  const n = (v, d = 2) => (typeof v === 'number' && Number.isFinite(v) ? v.toFixed(d) : '?');
  const list = (a) => (Array.isArray(a) ? a.map((v) => n(v, 1)).join(', ') : '');
  if (f.status !== 'ok') return h('p', { className: 'ws-note', 'data-slot': 'live-fit', 'data-status': 'error' }, 'Live fit not run: ' + String(f.message ?? f.error ?? ''));
  return h('div', { className: 'ws-live-fit', 'data-slot': 'live-fit', 'data-status': 'ok' },
    h('p', null, String(f.label)),
    h('p', { className: 'ws-note' }, String(f.track_label) + ' \u00b7 Fit: done (run now on the server)'),
    h('p', null, h('strong', null, 'g = ' + n(f.g) + ' \u00b1 ' + n(f.u) + ' m/s\u00b2'), ' (fitter, ' + String(f.fitter) + ')'),
    // S15bb: headline u = fit scatter + recorded S07m budget terms; one line says what it is made of (values from the server)
    h('p', { className: 'ws-note', 'data-slot': 'live-u' }, 'Uncertainty: ' + (f.u_terms && typeof f.u_terms === 'object'
      ? Object.entries(f.u_terms).map(([k, v]) => k.replace(/_/g, ' ') + ' ' + n(v)).join(', ') + ' (' + String(f.u_rule) + '); '
      : '') + String(f.u_label ?? '')),
    h('p', { className: 'ws-note' }, 'Fit residuals (px): ' + list(f.residuals_px) + '; rmse = ' + n(f.rmse_px) + ' px; dof = ' + String(f.dof) + '; points fitted = ' + String(f.n_fit)),
    h('p', { className: 'ws-note' }, 'Held-out residuals (px, ' + String(f.n_held_out) + ' points not fitted): ' + list(f.held_out_residuals_px)),
    h('p', { className: 'ws-note', 'data-slot': 'live-scale' }, 'Scale: ' + String(f.scale?.label ?? '')),
    h('p', { className: 'ws-note' }, String(f.caveat)));
}

// S15v: owner phone clip result from jobs.owner_measurement: stored MEASURED g ± u as a labelled RECORDED replay, or an abstain. Text only.
function renderMeasurement(h, m, chart = true) {
  const s = (v) => String(v ?? '');
  const scale = m.scale?.value_m != null ? 'Scale: ' + s(m.scale.reference) + ' = ' + s(m.scale.value_m) + ' m (' + s(m.scale.label) + ')' : null;
  const us = m.user_scale; // S15y: the interview's known-size answer, declared or abstain
  const yours = us?.status === 'declared' ? 'Your known size: ' + s(us.object) + ' = ' + s(us.length_m) + ' m (' + s(us.label) + ')' : us ? s(us.label) : null;
  return h('div', { className: 'ws-measurement', 'data-status': s(m.status), role: 'status', 'aria-label': 'Clip result' },
    m.live_fit && typeof m.live_fit === 'object' ? renderLiveFit(h, m.live_fit) : null,
    m.live_fit && m.status === 'recorded' ? h('hr', { className: 'ws-divider' }) : null,
    m.live_fit && m.status === 'recorded' ? h('h4', { className: 'ws-subhead' }, 'Recorded reference (not affected by your scale)') : null,
    h('p', null, s(m.clip_id) + ' \u00b7 ' + s(m.input_label) + ' \u00b7 ' + s(m.label)),
    // S15an: unit typeset only (m/s^2 -> m/s²; same stored numbers); the long source path sits in a collapsed "Source" detail.
    m.status === 'recorded' ? h('p', null, 'Recorded reference (precomputed, S07m): ', h('strong', null, 'g = ' + s(m.g) + ' ± ' + s(m.u) + ' ' + s(m.unit).replace('^2', '²')), ' (' + s(m.measured_label) + ')') : null,
    m.status === 'recorded' ? h('details', { className: 'ws-source' }, h('summary', null, 'Source'), h('code', null, s(m.source))) : null,
    m.status === 'recorded' ? h('p', { className: 'ws-note' }, s(m.caveat)) : h('p', { className: 'ws-note' }, s(m.message)),
    chart ? renderResultChart(h, m) : null,
    scale ? h('p', { className: 'ws-note' }, scale) : null,
    yours ? h('p', { className: 'ws-note', 'data-slot': 'user-scale' }, yours) : null);
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
            'aria-invalid': v.error ? true : undefined, 'aria-describedby': v.error ? 'ws-q-error' : undefined,
            onChange: (e) => send({ type: 'Q_TEXT', text: e.target.value }) })) : null),
      v.error ? h('p', { id: 'ws-q-error', className: 'ws-error', role: 'alert' }, v.error.message) : null,
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
    f ? h('div', { className: 'ws-failure', role: 'alert', 'data-kind': f.kind, 'data-stage': f.stage },
      h('h3', null, f.title), h('p', null, f.advice),
      f.kept.length ? h('p', { className: 'ws-kept' }, 'Kept: ' + f.kept.join('; ')) : null,
      f.lost.length ? h('p', { className: 'ws-lost' }, 'Not available: ' + f.lost.join('; ')) : null,
      f.retry ? h('button', { type: 'button', className: 'ws-retry', 'data-event': f.retry.event, disabled: !onAction, onClick: () => onAction?.({ type: f.retry.event }) }, f.retry.label)
        : h('p', { className: 'ws-noretry' }, 'Retry is not available for this error.')) : null);
}

