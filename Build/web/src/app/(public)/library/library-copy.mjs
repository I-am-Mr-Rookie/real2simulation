// Pure copy/grouping for /library; imported by LibraryClient.jsx and node tests.
export const TAG = { playable: 'SIMULATED · playable', 'metadata-only': 'SIMULATED · practice setup', unavailable: 'UNAVAILABLE' };
export const TONE = { playable: 'ok', 'metadata-only': 'warn', unavailable: 'danger' };
export const MYSTERY_COPY = 'Mystery-g practice shape at Earth g. This is not a blind test. To play blind, open the lab: the server draws a hidden g for each session.';

export function creditLine(entry) {
  const s = entry.source;
  if (!s) return 'Credit: no media is served for this entry.';
  if (s.kind === 'synthetic') return 'Credit: SIMULATED · project-authored, no external footage.';
  const parts = [s.creator || s.author, s.licence || s.license].filter(Boolean);
  return parts.length ? 'Credit: ' + parts.join(' · ') : 'Credit: source not recorded.';
}

const ORDER = { playable: 0, 'metadata-only': 1, unavailable: 2 };
// L1 chips: the evidence labels always listed (zero counts are honest), plus any other manifest label verbatim.
export const FILTER_LABELS = ['RECORDED', 'SIMULATED', 'what-if'];
export function filterChips(demos) {
  const labels = [...new Set([...FILTER_LABELS, ...demos.map((d) => d.label).filter(Boolean)])];
  return [['All', demos.length], ...labels.map((l) => [l, demos.filter((d) => d.label === l).length])];
}
export const matchesFilter = (entry, filter) => filter === 'All' || entry.label === filter;

export function groupDemos(demos) {
  const sorted = [...demos].sort((a, b) => (ORDER[a.availability] ?? 3) - (ORDER[b.availability] ?? 3));
  return { ready: sorted.filter((d) => d.availability !== 'unavailable'), unavailable: sorted.filter((d) => d.availability === 'unavailable') };
}
