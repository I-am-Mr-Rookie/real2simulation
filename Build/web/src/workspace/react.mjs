// S15b: React binding. React is injected so this package has no dependency of its own and stays node-testable.
// App composition (S04-owned page, inside a 'use client' module):
//   import React from 'react'; import './workspace.css';
//   export const Workspace = createWorkspace(React);
//   <Workspace state={state} adapter={createThreeViewer()} loadScene={createArtifactLoader({ bundleUrl })} audience="signed-in" />
import { layoutOf } from './layout.mjs';
import { createViewport } from './viewport.mjs';
import { renderWorkspace } from './view.mjs';
import { runView } from './runcontrol.mjs';
import { instrumentView } from './instruments.mjs';
import { fitView } from './fit-view.mjs';
import { sidebarOf, reportView } from './navigation.mjs';

// S15l: after a stage change the focused control may be gone (focus falls to body). Move focus to the panel heading then; never steal
// it from a control that survived. Returns true when focus moved.
export function restoreFocus(doc = globalThis.document) {
  const a = doc?.activeElement;
  if (a && a !== doc.body && doc.body?.contains?.(a)) return false;
  const hd = doc?.getElementById?.('ws-panel-heading');
  hd?.focus?.();
  return !!hd;
}

export const createWorkspace = (React) => function Workspace({ state, adapter, loadScene, audience, log, onAction, interview, template, run, instruments, fit, report, navigate, provenance, whatIf }) {
  const { createElement: h, useRef, useEffect, useState } = React;
  const host = useRef(null), ctl = useRef(null);
  const [view, setView] = useState({ status: 'empty', error: null });
  const layout = layoutOf(state, { ...(audience ? { audience } : {}), log });
  const prevPhase = useRef(layout.phase);
  useEffect(() => { if (prevPhase.current !== layout.phase) { prevPhase.current = layout.phase; restoreFocus(); } }, [layout.phase]);
  useEffect(() => {
    ctl.current = createViewport({ adapter, loadScene, onStatus: setView });
    return () => ctl.current.destroy();
  }, [adapter, loadScene]);
  useEffect(() => { ctl.current.sync(host.current, layout.viewport.request, layout.viewport.key); },
    [layout.viewport.key, adapter, loadScene]); // eslint-disable-line react-hooks/exhaustive-deps -- request is derived from key
  return renderWorkspace(h, layout, view, host, onAction, interview, template, run && runView(state, run), instruments && instrumentView(state, instruments), fit && fitView(state, fit, whatIf), navigate && sidebarOf(state, { interview, report }), report !== undefined || state.phase === 'report.open' ? reportView(state, report) : null, provenance, whatIf);
};
