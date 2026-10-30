'use client';
import { useEffect, useRef, useState } from 'react';
import { loadLibraryEntry } from '../../../../../library/loader.mjs';
import { mountTrajectoryReplay } from '../../../viewer/trajectory-replay.mjs';

const TAG = { playable: 'SIMULATED · playable', 'metadata-only': 'SIMULATED · setup only', unavailable: 'UNAVAILABLE' };

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
  return <div className="mount-note" data-slot="viewer" data-state={state}>
    <span className="state-tag">SIMULATED · SCALE_UNVERIFIED · display only</span>
    {state !== 'ready' && <p role="status">{state === 'loading' ? 'Loading verified trace…' : state}</p>}
    <div ref={host} />
  </div>;
}

function Card({ entry, open, onOpen }) {
  const playable = entry.availability === 'playable';
  return <li className="library-card" data-label={entry.label} data-availability={entry.availability}>
    <span className="state-tag">{TAG[entry.availability] || entry.label}</span>
    <h2>{entry.title}</h2>
    {entry.availability === 'unavailable' && <p><strong>Why unavailable:</strong> {entry.reason}</p>}
    {entry.challenge && <p>Mystery-g challenge: setup only. The answer is withheld until your own fit in the <a href="/lab">lab</a>.</p>}
    {entry.label !== 'UNAVAILABLE' && <p className="muted">{entry.scale_label || 'SCALE_UNVERIFIED'} · display only · not a measurement</p>}
    {entry.limitations?.length > 0 && <ul className="muted">{entry.limitations.map((t) => <li key={t}>{t}</li>)}</ul>}
    {playable && <button type="button" aria-expanded={open} onClick={onOpen}>{open ? 'Hide replay' : 'Play simulated replay'}</button>}
    {playable && open && <Replay entry={entry} />}
  </li>;
}

export default function LibraryClient() {
  const [manifest, setManifest] = useState(null); const [failed, setFailed] = useState(false); const [open, setOpen] = useState(null);
  useEffect(() => {
    fetch('/api/library/manifest').then((r) => (r.ok ? r.json() : Promise.reject())).then(setManifest, () => setFailed(true));
  }, []);
  if (failed) return <p role="alert">Library unavailable. No demo data was loaded.</p>;
  if (!manifest) return <p role="status">Loading library…</p>;
  const order = { playable: 0, 'metadata-only': 1, unavailable: 2 };
  const demos = [...manifest.demos].sort((a, b) => order[a.availability] - order[b.availability]);
  return <>
    <p className="muted">{manifest.scope}</p>
    <ul className="library-grid">{demos.map((d) => <Card key={d.id} entry={d} open={open === d.id}
      onOpen={() => setOpen(open === d.id ? null : d.id)} />)}</ul>
  </>;
}
