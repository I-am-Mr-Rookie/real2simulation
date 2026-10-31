'use client';
import { useEffect, useRef, useState } from 'react';
import { loadLibraryEntry } from '../../../../../library/loader.mjs';
import { mountTrajectoryReplay } from '../../../viewer/trajectory-replay.mjs';
import AppArt from '../../../lab/AppArt.jsx';
import { MYSTERY_COPY, TAG, TONE, creditLine, filterChips, groupDemos, matchesFilter } from './library-copy.mjs';

function Replay({ entry }) {
  const host = useRef(null); const [state, setState] = useState('loading');
  useEffect(() => {
    const ctl = new AbortController(); let view;
    (async () => {
      try {
        const loaded = await loadLibraryEntry(entry, { signal: ctl.signal });
        if (!loaded.canMount) throw new Error(loaded.reason);
        view = await mountTrajectoryReplay(host.current, loaded.trace, { mode: 'inspect', signal: ctl.signal });
        setState('ready');
      } catch (e) { if (!ctl.signal.aborted) setState('error: ' + (e?.message || 'replay failed')); }
    })();
    return () => { ctl.abort(); view?.dispose?.(); };
  }, [entry]);
  const failed = state.startsWith('error');
  return <div className="lib-replay" id={'replay-' + entry.id} data-slot="viewer" data-state={state} aria-busy={state === 'loading'}>
    <span className="state-tag">SIMULATED · SCALE_UNVERIFIED · display only</span>
    {state === 'loading' && <p role="status" className="muted">Loading verified trace…</p>}
    {failed && <p role="alert"><strong>Replay unavailable.</strong> {state.slice(7)} No trace was shown.</p>}
    <div ref={host} className="lib-stage" />
  </div>;
}

function Card({ entry, open, onOpen }) {
  const playable = entry.availability === 'playable';
  const licence = entry.source?.licence || entry.source?.license;
  return <li className="lib-card" data-label={entry.label} data-availability={entry.availability} data-open={open || undefined}>
    <div className="lib-thumb">
      <AppArt id="b3" width={960} height={540} />
      <div className="lib-tags">
        <span className="state-tag" data-tone={TONE[entry.availability]}>{TAG[entry.availability] || entry.label}</span>
        <span className="state-tag">{entry.scale_label || 'SCALE_UNVERIFIED'}</span>
      </div>
    </div>
    <p className="lib-kicker mono">{entry.id}{licence ? ' · ' + licence : ''}</p>
    <h3>{entry.title}</h3>
    {entry.challenge && <p className="lib-callout">{MYSTERY_COPY} <a href="/lab">Play blind in the lab →</a></p>}
    <p className="muted lib-meta">{creditLine(entry)}<br />Display only · not a measurement.</p>
    {entry.limitations?.length > 0 && <details className="lib-limits">
      <summary>Limitations ({entry.limitations.length})</summary>
      <ul>{entry.limitations.map((t) => <li key={t}>{t}</li>)}</ul>
    </details>}
    {playable && <button type="button" aria-expanded={open} aria-controls={'replay-' + entry.id} onClick={onOpen}>{open ? 'Hide replay' : 'Play simulated replay'}</button>}
    {playable && open && <Replay entry={entry} />}
  </li>;
}

export default function LibraryClient() {
  const [manifest, setManifest] = useState(null); const [failed, setFailed] = useState(false); const [open, setOpen] = useState(null);
  const [filter, setFilter] = useState('All');
  useEffect(() => {
    fetch('/api/library/manifest').then((r) => (r.ok ? r.json() : Promise.reject())).then(setManifest, () => setFailed(true));
  }, []);
  if (failed) return <div className="state-card" role="alert"><span className="state-tag" data-tone="danger">UNAVAILABLE</span>
    <p>Library unavailable. No demo data was loaded. Try again later, or use the <a href="/lab">lab</a>.</p></div>;
  if (!manifest) return <p role="status" className="muted">Loading library…</p>;
  const demos = manifest.demos || [];
  const { ready, unavailable } = groupDemos(demos.filter((d) => matchesFilter(d, filter)));
  const playable = ready.filter((d) => d.availability === 'playable').length;
  return <>
    <div className="lib-filters" role="group" aria-label="Filter demos by label">
      {filterChips(demos).map(([label, count]) => <button type="button" key={label} className="lib-chip" aria-pressed={filter === label}
        onClick={() => setFilter(label)}>{label}<span className="mono">{count}</span></button>)}
    </div>
    <p className="lib-summary mono">
      <span>{playable} playable</span><span>{ready.length - playable} practice setup</span><span>{unavailable.length} unavailable</span>
    </p>
    {!ready.length && !unavailable.length ? <div className="lib-empty" role="status">
      <AppArt id="b3" width={960} height={540} />
      <p><strong>No clips match</strong></p>
      <button type="button" className="secondary" onClick={() => setFilter('All')}>Clear filters</button>
    </div> : <>
    <h2 className="lib-section">Ready to open</h2>
    {ready.length ? <ul className="lib-grid">{ready.map((d) => <Card key={d.id} entry={d} open={open === d.id}
      onOpen={() => setOpen(open === d.id ? null : d.id)} />)}</ul>
      : <p className="state-card">No simulated entries are available right now. Nothing was substituted.</p>}
    {unavailable.length > 0 && <details className="lib-unavailable" open={filter !== 'All' || undefined}>
      <summary className="lib-section">Not available yet ({unavailable.length})</summary>
      <p className="muted">Listed so you can see what is missing and why. None of these load data.</p>
      <ul>{unavailable.map((d) => <li key={d.id} data-label={d.label} data-availability="unavailable">
        <span className="state-tag" data-tone="danger">UNAVAILABLE</span>
        <strong>{d.title}</strong><span className="muted">{d.reason}</span>
      </li>)}</ul>
    </details>}
    </>}
    <p className="muted lib-scope">Scope: {manifest.scope}</p>
  </>;
}
