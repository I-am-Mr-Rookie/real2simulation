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
    <p style={{ maxWidth: 1100, margin: '12px auto 0', padding: '0 12px' }}>
      <button type="button" aria-pressed={editor} onClick={() => setEditor((v) => !v)} style={{ minHeight: 44, padding: '0 14px' }}>
        {editor ? 'Back to synthetic trial' : 'Open 3D lab editor'}
      </button>
    </p>
    {editor ? <LabEditor /> : <LabClient />}
  </>;
}
