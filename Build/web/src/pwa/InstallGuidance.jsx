'use client';

import { useEffect, useState } from 'react';
import { createInstallStore } from './install-client.mjs';

// Not mounted anywhere yet (layout/page are outside S19c Owns). Renders nothing on the server and once installed.
export default function InstallGuidance() {
  const [store, setStore] = useState(null);
  const [snap, setSnap] = useState(null);

  useEffect(() => {
    const s = createInstallStore(window);
    const sync = () => setSnap(s.getSnapshot());
    const off = s.subscribe(sync);
    setStore(s);
    sync();
    return () => { off(); s.dispose(); };
  }, []);

  if (!snap || snap.guidance.state === 'installed') return null;
  const { guidance, orientation } = snap;
  return (
    <section aria-labelledby="install-title" className="install-guidance">
      <h2 id="install-title">{guidance.headline}</h2>
      {guidance.state === 'prompt' ? (
        <button type="button" onClick={() => store.promptInstall()}>Install</button>
      ) : (
        <ol>{guidance.steps.map((s) => <li key={s}>{s}</li>)}</ol>
      )}
      <ul>{guidance.notes.map((n) => <li key={n}>{n}</li>)}</ul>
      {orientation.hint ? <p>{orientation.hint}</p> : null}
    </section>
  );
}
