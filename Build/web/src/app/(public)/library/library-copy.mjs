// Pure copy/grouping for /library; imported by LibraryClient.jsx and node tests.
export const TAG = { playable: 'SIMULATED · playable', 'metadata-only': 'SIMULATED · practice setup' };
export const TONE = { playable: 'ok', 'metadata-only': 'warn' };
export const MYSTERY_COPY = 'Mystery-g practice shape at Earth g. This is not a blind test. To play blind, open the lab: the server draws a hidden g for each session.';

export function creditLine(entry) {
  const s = entry.source;
  if (!s) return 'Credit: no media is served for this entry.';
  if (s.kind === 'synthetic') return 'Credit: SIMULATED · project-authored, no external footage.';
  const parts = [s.creator || s.author, s.licence || s.license].filter(Boolean);
  return parts.length ? 'Credit: ' + parts.join(' · ') : 'Credit: source not recorded.';
}

const ORDER = { playable: 0, 'metadata-only': 1 };
// Keep the evidence-label order, but only offer filters with public entries.
export const FILTER_LABELS = ['RECORDED', 'SIMULATED', 'what-if'];
export function filterChips(demos) {
  const ready = groupDemos(demos);
  const labels = [...new Set([...FILTER_LABELS, ...ready.map((d) => d.label).filter(Boolean)])];
  return [['All', ready.length], ...labels.map((l) => [l, ready.filter((d) => d.label === l).length])].filter(([, n]) => n > 0);
}
export const matchesFilter = (entry, filter) => filter === 'All' || entry.label === filter;

export function groupDemos(demos) {
  return demos.filter((d) => d.availability !== 'unavailable')
    .sort((a, b) => (ORDER[a.availability] ?? 3) - (ORDER[b.availability] ?? 3));
}
