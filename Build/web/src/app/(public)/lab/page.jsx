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
    {!editor && <p className="lab-toggle" style={{ maxWidth: 1100, margin: '8px auto 0', padding: '0 16px', display: 'flex', justifyContent: 'flex-end', gap: 8, flexWrap: 'wrap' }}>
      {/* N89: no-video entry points; Make my copy in the editor saves a template to the signed-in workspace. */}
      <a className="secondary-link" href="/lab?editor=1&template=physics-lab" style={{ minHeight: 36 }}>Physics lab template</a>
      <a className="secondary-link" href="/lab?editor=1&template=blank" style={{ minHeight: 36 }}>Blank lab template</a>
      <button type="button" aria-pressed={editor} onClick={() => setEditor(true)} style={{ minHeight: 36, padding: '0 12px' }}>
        Open 3D lab editor
      </button>
    </p>}
    {editor ? <LabEditor onTemplateTrials={() => setEditor(false)} /> : <LabClient />}
  </>;
}
