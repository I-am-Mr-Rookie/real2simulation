// N24: Projects card grouping and short readable names for long ids. Pure, Node-testable, no DOM.
const KIND = { experiment: 'Experiment', room: 'Room' };
const SAMPLE_PREFIX = /^SAMPLE\b[^:]*:\s*/;

// 'acdb8a00edca4ba8b60f264f505719da' -> 'acdb8a'; short ids stay as they are.
export const shortId = (id) => { const s = String(id ?? ''); return s.length > 10 ? s.slice(0, 6) : s; };

// "Nov 1, 13:05 UTC" from an ISO string; '' when absent or unparsable.
export function shortWhen(iso) {
  const d = new Date(iso ?? '');
  if (!iso || Number.isNaN(d.getTime())) return '';
  return d.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false, timeZone: 'UTC' }) + ' UTC';
}

// Job item -> readable name: its title or name, else "Experiment acdb8a".
export function jobName(item, kind) {
  const t = item?.sample?.title || item?.title || item?.name; // N26: the seeded sample row carries its own SAMPLE title
  if (t && !/^[0-9a-f]{16,}$/i.test(t)) return String(t);
  return (KIND[kind] ?? 'Job') + ' ' + shortId(item?.id ?? item?.job_id ?? t);
}

export const isSample = (p) => p?.sample === true || /^SAMPLE\b/.test(p?.title ?? '');
// Sample title without its "SAMPLE (RECORDED):" prefix (the card shows SAMPLE and RECORDED as tags instead).
export const projectName = (p) => (isSample(p) ? String(p.title ?? '').replace(SAMPLE_PREFIX, '') || 'Sample project' : String(p?.title || 'Project ' + shortId(p?.id)));

// Projects (newest first, SAMPLE last) with their experiments and rooms; jobs without a known project go to a last group.
export function groupJobs(projects = [], experiments = [], rooms = []) {
  const groups = projects.map((p) => ({ id: p.id, name: projectName(p), mode: p.mode, sample: isSample(p), created: p.created, experiments: [], rooms: [] }));
  const by = new Map(groups.map((g) => [g.id, g]));
  const other = { id: null, name: 'Not in a project', sample: false, experiments: [], rooms: [] };
  for (const e of experiments) (by.get(e.project_id) ?? other).experiments.push(e);
  for (const r of rooms) (by.get(r.project_id) ?? other).rooms.push(r);
  const out = [...groups.filter((g) => !g.sample), ...groups.filter((g) => g.sample)];
  if (other.experiments.length || other.rooms.length) out.push(other);
  return out;
}
