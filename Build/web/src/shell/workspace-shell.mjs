// S15ab: private workspace shell (Q21 owner spec). Left nav collapses to an icon rail, the project owns the center, and the
// rightmost header button toggles a right Agent & tools panel. Pure render + key mapping (tested); PrivateWorkspace holds state.
import { PHASE_LABEL, OWNER_INTERVIEW_LABEL } from '../workspace/layout.mjs';

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

const PATHS = {
  grid: 'M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z', book: 'M5 4h9a3 3 0 0 1 3 3v13H8a3 3 0 0 1-3-3zM5 17a3 3 0 0 1 3-3h9',
  flask: 'M9 3h6M10 3v6l-5 9a2 2 0 0 0 2 3h10a2 2 0 0 0 2-3l-5-9V3', cube: 'M12 3l8 4.5v9L12 21l-8-4.5v-9zM12 12l8-4.5M12 12v9M12 12L4 7.5',
  panel: 'M4 5h16v14H4zM14 5v14', pulse: 'M3 12h4l2-5 4 10 2-5h6', chat: 'M4 5h16v11H9l-5 4z', film: 'M4 5h16v14H4zM8 5v14M16 5v14M4 9h4M16 9h4M4 15h4M16 15h4',
  history: 'M4 12a8 8 0 1 0 2.3-5.6M4 4v4h4M12 8v4l3 2', doc: 'M6 3h8l4 4v14H6zM14 3v4h4M9 12h6M9 16h6',
  rail: 'M4 5h16v14H4zM9 5v14', side: 'M4 5h16v14H4zM15 5v14', close: 'M6 6l12 12M18 6L6 18',
};
const icon = (h, name) => h('svg', { className: 'r2s-icon', viewBox: '0 0 24 24', width: 18, height: 18, 'aria-hidden': true, focusable: 'false' },
  h('path', { d: PATHS[name], fill: 'none', stroke: 'currentColor', strokeWidth: 1.8, strokeLinecap: 'round', strokeLinejoin: 'round' }));

const navList = (h, label, items, onNav) => h('nav', { className: 'r2s-nav', 'aria-label': label },
  h('p', { className: 'r2s-nav-h', 'aria-hidden': true }, label),
  h('ul', null, ...items.map((it) => h('li', { key: it.id },
    h('a', { href: it.href, title: it.label, 'data-nav': it.id, onClick: onNav }, icon(h, it.icon), h('span', { className: 'r2s-label' }, it.label))))));

// v = { title, left, right, tools, pending, agent }; left null = not yet read (before hydration): wide CSS shows it expanded, narrow keeps the drawer shut.
// S15ac: agent = the question card element (rendered above Tools); pending > 0 with the panel closed shows a badge on the toggle.
// on = { toggleLeft, toggleRight, tool, close, navigated }; refs = { rightToggle, rightHead }.
export function renderShell(h, v, on = {}, refs = {}, ...content) {
  const { right, tools, pending = 0 } = v;
  const left = v.left ?? true;
  return h('div', { className: 'r2s-shell', 'data-left': v.left == null ? 'auto' : left ? 'expanded' : 'collapsed', 'data-right': right ? 'open' : 'closed' },
    h('aside', { id: 'r2s-left', className: 'r2s-left', 'aria-label': 'Workspace sidebar' },
      navList(h, 'Go to', NAV), navList(h, 'This project', SECTIONS, on.navigated)),
    h('div', { className: 'r2s-center' },
      h('header', { className: 'r2s-top' },
        h('button', { type: 'button', className: 'r2s-iconbtn', 'data-toggle': 'left', 'aria-controls': 'r2s-left', 'aria-expanded': left,
          'aria-keyshortcuts': 'Control+B', title: (left ? 'Collapse' : 'Expand') + ' sidebar (' + SHORTCUT_LABEL.left + ')', 'aria-label': 'Sidebar', onClick: on.toggleLeft },
          icon(h, 'rail')),
        h('h1', null, v.title),
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
        h('button', { type: 'button', className: 'r2s-tool', 'data-tool': t.id, 'aria-keyshortcuts': 'Alt+' + t.key, onClick: () => on.tool?.(t) },
          icon(h, t.icon), h('span', { className: 'r2s-tool-text' }, h('strong', null, t.label), h('span', { className: 'r2s-tool-status' }, t.status)),
          h('kbd', null, 'Alt+' + t.key)))))
        : h('p', { className: 'r2s-empty' }, 'No tools: the private workspace service is not connected, so nothing here can act.')),
    h('div', { className: 'r2s-scrim', 'aria-hidden': true, onClick: on.close }));
}
