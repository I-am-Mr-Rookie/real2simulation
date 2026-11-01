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
    <p className={editor ? 'lab-toggle lab-toggle-editor' : 'lab-toggle'} style={{ maxWidth: editor ? 1680 : 1100, margin: '8px auto 0', padding: '0 16px', display: 'flex', justifyContent: 'flex-end' }}>
      <button type="button" aria-pressed={editor} onClick={() => setEditor((v) => !v)} style={{ minHeight: 36, padding: '0 12px' }}>
        {editor ? 'Template trials' : 'Open 3D lab editor'}
      </button>
    </p>
    {editor ? <LabEditor /> : <LabClient />}
  </>;
}
