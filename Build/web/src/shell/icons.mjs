// S15ah: the one icon set (inline 24px stroke SVG, lucide-style; no dependency). Shared by workspace and public pages (S15ai).
// h = React.createElement (or any hyperscript); names not in PATHS render nothing.
export const PATHS = Object.freeze({
  grid: 'M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z', book: 'M5 4h9a3 3 0 0 1 3 3v13H8a3 3 0 0 1-3-3zM5 17a3 3 0 0 1 3-3h9',
  flask: 'M9 3h6M10 3v6l-5 9a2 2 0 0 0 2 3h10a2 2 0 0 0 2-3l-5-9V3', cube: 'M12 3l8 4.5v9L12 21l-8-4.5v-9zM12 12l8-4.5M12 12v9M12 12L4 7.5',
  panel: 'M4 5h16v14H4zM14 5v14', pulse: 'M3 12h4l2-5 4 10 2-5h6', chat: 'M4 5h16v11H9l-5 4z', film: 'M4 5h16v14H4zM8 5v14M16 5v14M4 9h4M16 9h4M4 15h4M16 15h4',
  history: 'M4 12a8 8 0 1 0 2.3-5.6M4 4v4h4M12 8v4l3 2', doc: 'M6 3h8l4 4v14H6zM14 3v4h4M9 12h6M9 16h6',
  rail: 'M4 5h16v14H4zM9 5v14', side: 'M4 5h16v14H4zM15 5v14', close: 'M6 6l12 12M18 6L6 18',
  compass: 'M12 3a9 9 0 1 0 0 18a9 9 0 1 0 0-18zM15.5 8.5l-2 5-5 2 2-5z', list: 'M9 6h11M9 12h11M9 18h11M4.5 6h.01M4.5 12h.01M4.5 18h.01',
  sun: 'M12 8a4 4 0 1 0 0 8a4 4 0 1 0 0-8zM12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4',
  moon: 'M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z', monitor: 'M3 4h18v12H3zM8 20h8M12 16v4',
  upload: 'M12 15V4M7 9l5-5 5 5M4 15v4a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-4', info: 'M12 3a9 9 0 1 0 0 18a9 9 0 1 0 0-18zM12 11v6M12 7.5h.01',
  play: 'M7 4l13 8-13 8z', chart: 'M4 4v16h16M8 15l3-4 3 2 5-6', check: 'M5 12l5 5 9-10', alert: 'M12 3l10 18H2zM12 10v5M12 18h.01',
  palette: 'M12 3a9 9 0 1 0 0 18c1.1 0 1.6-.8 1.6-1.6 0-1.2-1-1.6-1-2.6 0-.9.7-1.6 1.6-1.6H17a4 4 0 0 0 4-4c0-4.6-4-8.2-9-8.2zM7.5 11h.01M10 7h.01M15 7.5h.01',
});
export const icon = (h, name, size = 18) => (PATHS[name] ? h('svg', { className: 'r2s-icon', viewBox: '0 0 24 24', width: size, height: size, 'aria-hidden': true, focusable: 'false' },
  h('path', { d: PATHS[name], fill: 'none', stroke: 'currentColor', strokeWidth: 1.8, strokeLinecap: 'round', strokeLinejoin: 'round' })) : null);
