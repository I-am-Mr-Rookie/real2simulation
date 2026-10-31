// S15ab: private workspace shell (Q21 owner spec). Left nav collapses to an icon rail, the project owns the center, and the
// rightmost header button toggles a right Agent & tools panel. Pure render + key mapping (tested); PrivateWorkspace holds state.
import { PHASE_LABEL, OWNER_INTERVIEW_LABEL } from '../workspace/layout.mjs';
import { icon } from './icons.mjs';
import { THEME_OPTIONS } from './theme.mjs';

export const LEFT_KEY = 'r2s.workspace.left';
export const NARROW_QUERY = '(max-width: 760px)';
export const SHORTCUT_LABEL = Object.freeze({ left: 'Ctrl+B', right: 'Ctrl+J' });

// Real routes and real sections of this page only.
export const NAV = Object.freeze([
  { id: 'workspace', href: '/workspace', label: 'Private workspace', icon: 'grid' },
  { id: 'library', href: '/library', label: 'Demo library', icon: 'book' },
  { id: 'lab', href: '/lab', label: 'Local simulation lab', icon: 'flask' },
]);
export const SECTIONS = Object.freeze([
  { id: 'viewport', href: '#ws-viewport', label: 'Scene viewport', icon: 'cube' },
  { id: 'panel', href: '#ws-panel', label: 'Stage panel', icon: 'panel' },
  { id: 'job', href: '#ws-job', label: 'Job status', icon: 'pulse' },
]);

// Narrow screens always start with the drawer closed; wide screens restore the stored choice (default expanded).
export const initialLeft = (stored, narrow) => !narrow && stored !== 'collapsed';

// S15ae: activity bar (Q21 section 6). The icon rail is always visible; each icon owns one pane of real links already on this page.
export const PANE_KEY = 'r2s.workspace.pane';
export const PANES = Object.freeze([
  { id: 'navigate', label: 'Go to', icon: 'compass', items: NAV },
  { id: 'project', label: 'This project', icon: 'list', items: SECTIONS },
]);
export const HOVER_OPEN_MS = 150;
export const HOVER_CLOSE_MS = 250;
// rail = { pane: current pane id, open: current pane pinned open, preview: id shown temporarily as an overlay or null }.
export const initialRail = (storedOpen, storedPane, narrow) =>
  ({ pane: PANES.some((p) => p.id === storedPane) ? storedPane : PANES[0].id, open: initialLeft(storedOpen, narrow), preview: null });
export const shownPane = (s) => s.preview ?? (s.open ? s.pane : null);
// Pure reducer; hover events arrive already debounced (open after HOVER_OPEN_MS, leave after HOVER_CLOSE_MS). No-ops return s.
export function railReduce(s, e) {
  switch (e.type) {
    case 'toggle': return { ...s, open: !s.open, preview: null };
    case 'iconClick': return e.id === s.pane && s.open && !s.preview ? { ...s, open: false } : { pane: e.id, open: true, preview: null };
    case 'hoverEnter': return s.open && e.id === s.pane ? (s.preview ? { ...s, preview: null } : s) : s.preview === e.id ? s : { ...s, preview: e.id };
    case 'hoverLeave': case 'escape': return s.preview ? { ...s, preview: null } : s;
    case 'pin': return s.preview ? { pane: s.preview, open: true, preview: null } : s;
    default: return s;
  }
}

// Tools exist only when the private API answered (live); each maps to a real backend-driven surface already on the page.
export function toolsOf({ live, phase, owner, jobId, uploadStatus, hasReport, pending = 0 }) {
  if (!live) return [];
  const label = PHASE_LABEL[phase] ?? phase;
  return [
    { id: 'agent', label: 'Agent', status: (pending ? pending + (pending === 1 ? ' question' : ' questions') + ' waiting. ' : '') + (owner && phase === 'interview.active' ? OWNER_INTERVIEW_LABEL : label),
      pending, target: pending ? 'r2s-q-h' : 'ws-panel', key: '1', icon: 'chat' },
    { id: 'clips', label: 'Clips', status: uploadStatus || 'Upload an approved licensed clip', target: 'ws-upload-file', key: '2', icon: 'film' },
    { id: 'runs', label: 'Runs & history', status: jobId ? 'Job ' + jobId + ': ' + label : 'No job yet', target: 'ws-job', key: '3', icon: 'history' },
    { id: 'report', label: 'Report', status: hasReport ? 'Report available' : 'No report yet (needs a finished fit or clip result)', target: 'ws-panel', key: '4', icon: 'doc' },
  ];
}

// Keyboard map: Ctrl/Cmd+B left, Ctrl/Cmd+J right, Alt+1..4 tools, Escape closes overlays.
export function shellKey(e, tools = []) {
  const mod = (e.ctrlKey || e.metaKey) && !e.altKey && !e.shiftKey;
  const k = (e.key || '').toLowerCase();
  if (mod && k === 'b') return 'left';
  if (mod && k === 'j') return 'right';
  if (e.altKey && !e.ctrlKey && !e.metaKey) { const t = tools.find((x) => e.code === 'Digit' + x.key); if (t) return 'tool:' + t.id; }
  if (k === 'escape') return 'escape';
  return null;
}

const navList = (h, label, items, onNav) => h('nav', { className: 'r2s-nav', 'aria-label': label },
  h('p', { className: 'r2s-nav-h', 'aria-hidden': true }, label),
  h('ul', null, ...items.map((it) => h('li', { key: it.id },
    h('a', { href: it.href, title: it.label, 'data-nav': it.id, onClick: onNav }, icon(h, it.icon), h('span', { className: 'r2s-label' }, it.label))))));

// v = { title, rail, right, tools, pending, agent }; rail null = not yet read (before hydration): wide CSS shows it expanded, narrow keeps the drawer shut.
// S15ac: agent = the question card element (rendered above Tools); pending > 0 with the panel closed shows a badge on the toggle.
// on = { toggleLeft, toggleRight, tool, close, navigated, rail(event), hover(id, pointerEvent), unhover, paneEnter }; refs = { rightToggle, rightHead }.
export function renderShell(h, v, on = {}, refs = {}, ...content) {
  const { right, tools, pending = 0 } = v;
  const rail = v.rail ?? initialRail(null, null, false);
  const left = rail.open;
  const shown = shownPane(rail);
  return h('div', { className: 'r2s-shell', 'data-left': v.rail == null ? 'auto' : left ? 'expanded' : 'collapsed', 'data-right': right ? 'open' : 'closed' },
    h('aside', { id: 'r2s-left', className: 'r2s-left', 'aria-label': 'Workspace sidebar' },
      h('div', { className: 'r2s-rail', role: 'group', 'aria-label': 'Sidebar panes' }, ...PANES.map((p) =>
        h('button', { key: p.id, type: 'button', className: 'r2s-railbtn', 'data-pane': p.id, 'aria-label': p.label, title: p.label,
          'aria-current': p.id === rail.pane ? 'true' : undefined, 'aria-expanded': shown === p.id, 'aria-controls': 'r2s-pane-' + p.id,
          onClick: () => on.rail?.({ type: 'iconClick', id: p.id }), onPointerEnter: (e) => on.hover?.(p.id, e), onPointerLeave: on.unhover }, icon(h, p.icon)))),
      ...PANES.map((p) => h('div', { key: p.id, id: 'r2s-pane-' + p.id, className: 'r2s-pane', role: 'region', 'aria-label': p.label, hidden: shown !== p.id,
        'data-mode': rail.preview === p.id ? 'temporary' : 'pinned', onPointerEnter: on.paneEnter, onPointerLeave: on.unhover },
        navList(h, p.label, p.items, on.navigated)))),
    h('div', { className: 'r2s-center' },
      h('header', { className: 'r2s-top' },
        h('button', { type: 'button', className: 'r2s-iconbtn', 'data-toggle': 'left', 'aria-controls': 'r2s-left', 'aria-expanded': left,
          'aria-keyshortcuts': 'Control+B', title: (left ? 'Collapse' : 'Expand') + ' sidebar (' + SHORTCUT_LABEL.left + ')', 'aria-label': 'Sidebar', onClick: on.toggleLeft },
          icon(h, 'rail')),
        h('h1', { title: typeof v.title === 'string' ? v.title : undefined }, v.title),
        // S15am: compact theme menu (System + six COLOR_MODES, swatch icons); native <details> = keyboard/escape-free disclosure, no new state.
        h('details', { className: 'r2s-theme' },
          h('summary', { className: 'r2s-iconbtn', 'aria-label': 'Colour theme', title: 'Colour theme' }, icon(h, 'palette', 16)),
          h('div', { className: 'r2s-theme-menu', role: 'group', 'aria-label': 'Colour theme' }, ...THEME_OPTIONS.map((t) =>
            h('button', { key: t.id, type: 'button', className: 'r2s-themebtn', 'data-theme-option': t.id, 'aria-pressed': (v.theme ?? 'system') === t.id,
              'aria-label': t.label + ' theme', title: t.label, onClick: (e) => { on.theme?.(t.id); e?.currentTarget?.closest?.('details')?.removeAttribute('open'); } },
              t.tokens ? h('span', { className: 'r2s-swatch', 'aria-hidden': true, style: { background: t.tokens.bg, borderColor: t.tokens['border-strong'], color: t.tokens.accent } }) : icon(h, t.icon, 16),
              h('span', { className: 'r2s-themename' }, t.label))))),
        h('button', { type: 'button', ref: refs.rightToggle, className: 'r2s-iconbtn r2s-tools-btn', 'data-toggle': 'right', 'aria-controls': 'r2s-right', 'aria-expanded': right,
          'aria-keyshortcuts': 'Control+J', title: (right ? 'Close' : 'Open') + ' agent and tools (' + SHORTCUT_LABEL.right + ')', onClick: on.toggleRight },
          icon(h, 'side'), h('span', { className: 'r2s-label' }, 'Agent & tools'),
          pending && !right ? h('span', { className: 'r2s-badge', 'data-badge': pending }, String(pending), h('span', { className: 'r2s-sr' }, pending === 1 ? ' question waiting' : ' questions waiting')) : null)),
      ...content),
    h('aside', { id: 'r2s-right', className: 'r2s-right', 'aria-labelledby': 'r2s-right-h', hidden: !right },
      h('div', { className: 'r2s-right-head' },
        h('h2', { id: 'r2s-right-h', ref: refs.rightHead, tabIndex: -1 }, 'Agent & tools'),
        h('button', { type: 'button', className: 'r2s-iconbtn', 'aria-label': 'Close agent and tools', title: 'Close (Esc)', onClick: on.toggleRight }, icon(h, 'close'))),
      v.agent ?? null,
      h('h3', { className: 'r2s-nav-h' }, 'Tools'),
      tools.length ? h('ul', { className: 'r2s-tools' }, ...tools.map((t) => h('li', { key: t.id },
        h('button', { type: 'button', className: 'r2s-tool', 'data-tool': t.id, 'aria-keyshortcuts': 'Alt+' + t.key, title: t.status, onClick: () => on.tool?.(t) },
          icon(h, t.icon), h('span', { className: 'r2s-tool-text' }, h('strong', null, t.label), h('span', { className: 'r2s-tool-status' }, t.status)),
          h('kbd', null, 'Alt+' + t.key)))))
        : h('p', { className: 'r2s-empty' }, 'No tools: the private workspace service is not connected, so nothing here can act.')),
    h('div', { className: 'r2s-scrim', 'aria-hidden': true, onClick: on.close }));
}
