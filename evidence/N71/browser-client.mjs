// Local synthetic QA only: real workspace components/useLive against the worktree's API router.
import React from 'react';
import { createRoot } from 'react-dom/client';
import { createLive } from '../../Build/web/src/workspace/live-view.mjs';
import { renderShell } from '../../Build/web/src/shell/workspace-shell.mjs';
import { icon } from '../../Build/web/src/shell/icons.mjs';
const Live = createLive(React, icon), h = React.createElement;
function App() {
  const [right, setRight] = React.useState(false);
  const L = Live.useLive(true, () => setRight(true), 'n71-synthetic');
  return renderShell(h, { title: 'N71 local synthetic QA', rail: { pane: 'project', open: false }, right, tools: [],
    agent: h(Live.Chat, { L }), status: h(Live.Dot, { L }), foot: h(Live.Meter, { L }) },
    { toggleRight: () => setRight(!right), close: () => setRight(false) }, {}, h(Live.Centre, { L }));
}
createRoot(document.getElementById('main')).render(h(App));
