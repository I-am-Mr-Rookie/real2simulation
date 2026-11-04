'use client';

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import LabClient from '../../../lab/LabClient';
import '../../../lab/lab.css';

// N10: the 3D lab editor (three + lazy Rapier) loads only when toggled on, or with ?editor=1.
const LabEditor = dynamic(() => import('../../../lab-editor/LabEditor.jsx'), { ssr: false });

export default function LabPage() {
  const [editor, setEditor] = useState(false);
  useEffect(() => { if (new URLSearchParams(window.location.search).has('editor')) setEditor(true); }, []);
  return <>
    {!editor && <div className="lab-toggle" style={{ maxWidth: 1100, margin: '12px auto 0', padding: '0 16px', display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
      {/* N89: 3D labs first (no video needed); Make my copy in the editor saves a template to the signed-in workspace. */}
      <p style={{ margin: 0, flex: '1 1 18rem' }}><strong>No video needed.</strong> Open a 3D lab, or play Guess the Gravity below.</p>
      <a className="primary-link" href="/lab?editor=1&template=physics-lab" style={{ minHeight: 36 }}>Physics lab (3D)</a>
      <a className="secondary-link" href="/lab?editor=1&template=blank" style={{ minHeight: 36 }}>Blank lab (3D)</a>
      <button type="button" aria-pressed={editor} onClick={() => setEditor(true)} style={{ minHeight: 36, padding: '0 12px' }}>
        Open 3D editor
      </button>
    </div>}
    {editor ? <LabEditor onTemplateTrials={() => setEditor(false)} /> : <LabClient />}
  </>;
}
