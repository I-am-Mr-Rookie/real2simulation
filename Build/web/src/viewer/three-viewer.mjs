// Browser entry: real three.js renderer wired into the S09a adapter. Bundlers resolve 'three'
// from Build/web/package.json (three 0.186.1, CODEX-2-owned manifest).
import * as THREE from 'three';
import { createViewerAdapter } from './adapter.mjs';
import { createThreeRenderer } from './three-renderer.mjs';

export const createThreeViewer = (opts = {}) => createViewerAdapter({ createRenderer: createThreeRenderer({ THREE, ...opts }) });
