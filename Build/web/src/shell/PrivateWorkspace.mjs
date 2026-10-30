'use client';
import React from 'react';
import { createWorkspace } from '../workspace/react.mjs';
import { createThreeViewer } from '../viewer/three-viewer.mjs';

const Workspace = createWorkspace(React);
const adapter = createThreeViewer();

export default function PrivateWorkspace({ scene }) {
  return React.createElement('section', { 'data-private-content': 'fixture', 'aria-label': 'Private workspace' },
    React.createElement('h1', null, scene.title),
    React.createElement('p', { role: 'note' }, scene.notice),
    React.createElement(Workspace, { state: scene.state, adapter, audience: 'signed-in' }));
}
