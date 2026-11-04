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

// N55: "just now", "5 min ago", "3 h ago", "2 d ago", else the short date; '' when absent.
export function relTime(iso, now = Date.now()) {
  const t = new Date(iso ?? '').getTime();
  if (!iso || Number.isNaN(t)) return '';
  const s = Math.max(0, (now - t) / 1000);
  return s < 60 ? 'just now' : s < 3600 ? Math.floor(s / 60) + ' min ago' : s < 86400 ? Math.floor(s / 3600) + ' h ago' : s < 7 * 86400 ? Math.floor(s / 86400) + ' d ago' : shortWhen(iso);
}

// N55 card status from the newest job of a group (tracked live view first): { state: 'empty'|'processing'|'ready'|'failed', progress, reason }.
export function groupStatus(g, tracked = {}) {
  const when = (j) => String(j.created || j.created_at || j.updated || j.updated_at || ''); // Legacy room rows only carry updated_at.
  const jobs = [...g.rooms.map((j) => ['room', j]), ...g.experiments.map((j) => ['experiment', j])]
    .sort((a, b) => when(b[1]).localeCompare(when(a[1])));
  if (!jobs.length) return { state: g.snapshot || g.lab ? 'saved' : 'empty' }; // N89: lab = saved lab scene (template copy)
  const [kind, j] = jobs[0], live = tracked[kind + ':' + (j.id ?? j.job_id)];
  const st = String(live?.state ?? j.status ?? j.state ?? 'unknown');
  if (st === 'done') return { state: 'ready', kind, job: j };
  if (/^(failed|error)$/.test(st)) return { state: 'failed', kind, job: j, reason: live?.error || j.error?.message || j.error || j.reason || 'no reason given' };
  return { state: 'processing', kind, job: j, progress: Number.isFinite(j.progress) ? j.progress : null, step: live?.step };
}
// Sample title without its "SAMPLE (RECORDED):" prefix (the card shows SAMPLE and RECORDED as tags instead).
export const projectName = (p) => (isSample(p) ? String(p.title ?? '').replace(SAMPLE_PREFIX, '') || 'Sample project' : String(p?.title || 'Project ' + shortId(p?.id)));

// Projects (newest first, SAMPLE last) with their experiments and rooms; jobs without a known project go to a last group.
export function groupJobs(projects = [], experiments = [], rooms = []) {
  // N55: snapshot_url = optional saved lab snapshot (N56); the card falls back to a video frame.
  const groups = projects.map((p) => ({ id: p.id, name: projectName(p), mode: p.mode, sample: isSample(p), created: p.created, snapshot: p.snapshot_url ?? null, trackPreview: p.track_preview ?? null, lab: p.lab === true, experiments: [], rooms: [] }));
  const by = new Map(groups.map((g) => [g.id, g]));
  const other = { id: null, name: 'Not in a project', sample: false, experiments: [], rooms: [] };
  for (const e of experiments) (by.get(e.project_id) ?? other).experiments.push(e);
  for (const r of rooms) (by.get(r.project_id) ?? other).rooms.push(r);
  const out = [...groups.filter((g) => !g.sample), ...groups.filter((g) => g.sample)];
  if (other.experiments.length || other.rooms.length) out.push(other);
  return out;
}
