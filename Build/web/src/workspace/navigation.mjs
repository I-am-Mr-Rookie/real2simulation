// S15i: sidebar navigation (pure) + report parse/view model. Agent and report modules are Python; this package reaches them only through
// their JSON contracts (agent: interview.mjs parseQuestions; report: r2s.report/1), delivered by host-injected services.
import { STAGES, STAGE_LABEL } from './layout.mjs';
import { stageOf, availableEvents } from './workflow.mjs';
import { interviewView } from './interview.mjs';

const ID = /^[a-z][a-z_]*$/, PH = /\{\{([^{}]*)\}\}/g;
const LABELS = ['measured', 'simulated'], TEMPLATES = ['free_fall', 'pendulum', 'projectile', 'ramp'];
const ENTRY = ['path', 'value', 'unit', 'label', 'uncertainty_path', 'uncertainty'];
const obj = (o) => o && typeof o === 'object' && !Array.isArray(o);
const keys = (o, allowed, req = allowed) => obj(o) && req.every((k) => k in o) && Object.keys(o).every((k) => allowed.includes(k));
const prose = (t) => typeof t === 'string' && t.trim() !== '' && !/[\d{}]/.test(t.replace(PH, ' '));

// Closed-shape mirror of the Build/reports contract (r2s.report/1). The server runs validate_report (digest check); JS cannot recompute the digest.
export function parseReport(r) {
  if (!keys(r, ['schema', 'template', 'fitter_digest', 'title', 'sections', 'numbers']) || r.schema !== 'r2s.report/1' || !TEMPLATES.includes(r.template) ||
    typeof r.fitter_digest !== 'string' || !r.fitter_digest || !obj(r.numbers)) throw new Error('report shape');
  for (const [id, e] of Object.entries(r.numbers)) {
    if (!ID.test(id) || !keys(e, ENTRY, ['path', 'value', 'unit', 'label']) || !Number.isFinite(e.value) || typeof e.unit !== 'string' || !LABELS.includes(e.label) ||
      ('uncertainty' in e) !== ('uncertainty_path' in e) || ('uncertainty' in e && (!Number.isFinite(e.uncertainty) || e.uncertainty < 0))) throw new Error('number entry ' + id);
  }
  const texts = [r.title];
  if (!Array.isArray(r.sections) || !r.sections.length) throw new Error('sections');
  for (const s of r.sections) {
    if (!keys(s, ['id', 'title', 'text']) || !ID.test(s.id) || !Array.isArray(s.text) || !s.text.length) throw new Error('section shape');
    texts.push(s.title, ...s.text);
  }
  for (const t of texts) {
    if (!prose(t)) throw new Error('prose has a bare number or malformed placeholder');
    for (const [, id] of t.matchAll(PH)) if (!(id in r.numbers)) throw new Error('unknown placeholder ' + id);
  }
  return r;
}

// Unit "1" is the contract's dimensionless marker: shown as nothing, not as a stray "1".
const fmt = (e) => String(e.value) + (e.uncertainty !== undefined ? ' \u00b1 ' + e.uncertainty : '') + (e.unit === '1' ? '' : ' ' + e.unit) + ' (' + e.label + ')';

// Report is shown only in report.open, and only when it parses; failure is a visible message, never a partial report.
export function reportView(state, input) {
  if (state.phase !== 'report.open') return { show: false };
  if (!input) return { show: true, error: 'No report received yet.' };
  try {
    const r = parseReport(input), fill = (t) => t.replace(PH, (_, id) => fmt(r.numbers[id]));
    return { show: true, error: null, title: fill(r.title), template: r.template,
      sections: r.sections.map((s) => ({ id: s.id, title: fill(s.title), text: s.text.map(fill) })),
      labels: [...new Set(Object.values(r.numbers).map((e) => e.label))],
      notice: 'Every number is copied from fitter output with its source label. This is not gate, real-scene or physical evidence unless labelled so.' };
  } catch (e) { return { show: true, error: 'Report rejected: ' + String(e.message).slice(0, 160) }; }
}

// Sidebar: one entry per stage. Only reducer-legal moves carry an event, so navigation cannot skip fit or fake a report.
const MOVES = { interview: ['EDIT_SPEC', 'Re-opens the interview; clears the run and fit.'], report: ['REPORT_OPEN'], fit: ['REPORT_CLOSE'], upload: ['RESET', 'Discards the scene, run and fit.'] };
export function sidebarOf(state, { interview, report } = {}) {
  const cur = stageOf(state), ok = availableEvents(state), at = STAGES.indexOf(cur);
  return STAGES.map((id, i) => {
    const [ev, warn] = MOVES[id] ?? [], here = id === cur, missing = id === 'report' && !report;
    const event = !here && ev && ok.includes(ev) && !missing ? { type: ev } : null;
    const note = here ? null : event ? warn ?? null : missing && ok.includes('REPORT_OPEN') ? 'Report not received yet.' : i > at ? 'Not reached yet.' : 'Not available from here.';
    return { id, label: STAGE_LABEL[id], current: here, status: i < at ? 'done' : here ? 'current' : 'todo', event, destructive: !!(event && warn), note,
      detail: id === 'interview' && interview ? interviewView(interview).progress : null };
  });
}

export function renderSidebar(h, items, onAction) {
  return h('nav', { className: 'ws-sidebar', 'data-nav': 'sidebar', 'aria-label': 'Workspace sections' },
    h('ul', null, ...items.map((it) => h('li', { key: it.id, 'data-status': it.status },
      h('button', { type: 'button', className: 'ws-nav', 'aria-current': it.current ? 'page' : undefined, 'data-destructive': it.destructive || undefined,
        disabled: !it.event || !onAction, onClick: () => onAction?.(it.event) }, it.label),
      it.detail ? h('span', { className: 'ws-nav-detail' }, it.detail) : null,
      it.note ? h('span', { className: 'ws-nav-note' }, it.note) : null))));
}

export function renderReport(h, v) {
  if (!v.show) return null;
  if (v.error) return h('section', { className: 'ws-report', 'aria-label': 'Report' }, h('p', { className: 'ws-error', role: 'alert' }, v.error));
  return h('section', { className: 'ws-report', 'aria-label': 'Report' }, h('h3', null, v.title),
    ...v.sections.map((s) => h('article', { key: s.id }, h('h4', null, s.title), ...s.text.map((t, i) => h('p', { key: i }, t)))),
    h('p', { className: 'ws-notice', role: 'note' }, v.notice));
}
