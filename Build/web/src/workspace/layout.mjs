// S15b: pure workspace layout model. State (S15a reducer) -> slots, stage rail, viewer request, job status text.
// No DOM/React/viewer imports: the viewer is reached only through an injected adapter (see viewport.mjs).
import { PHASES, stageOf } from './workflow.mjs';
import { statusSurface } from './status.mjs';

export const SLOTS = Object.freeze(['stage-nav', 'viewport', 'panel', 'job-status']);
export const STAGES = Object.freeze(['upload', 'interview', 'run', 'fit', 'report']);
export const STAGE_LABEL = Object.freeze({ upload: 'Upload', interview: 'Interview', run: 'Run', fit: 'Fit', report: 'Report' });

// "ready" means an artifact exists, never accuracy or a passed gate (S15a invariant).
export const PHASE_LABEL = Object.freeze({
  'upload.idle': 'Waiting for an upload', 'upload.queued': 'Upload queued', 'upload.running': 'Processing upload',
  'upload.failed': 'Upload failed', 'upload.cancelled': 'Upload cancelled',
  'interview.active': 'Scene ready; interview in progress (not a measurement)',
  'run.ready': 'Ready to run', 'run.running': 'Run in progress', 'run.paused': 'Run paused', 'run.done': 'Run finished', 'run.failed': 'Run failed',
  'fit.running': 'Fit in progress', 'fit.done': 'Fit finished', 'fit.failed': 'Fit failed',
  'report.open': 'Report open',
});

export const SYNTHETIC_SCENE_BANNER = 'SYNTHETIC scene: authored geometry, not reconstruction, measurement or gate evidence';

export const sceneKey = (s) => (s ? [s.scene_id, s.scene_version, s.access, s.evidence].join('|') : null);

// Viewer request per integration.schema.json $defs.viewer. Mystery mode is never requested here (S10 payload absent).
export const viewerRequestOf = (state, { audience = 'signed-in', mode = 'inspect' } = {}) =>
  state.scene ? { contract_version: '1.0.0', kind: 'viewer', audience, mode, scene: { ...state.scene } } : null;

export const VIEWER_STATUS_TEXT = Object.freeze({
  empty: 'No scene yet. The viewport appears when an upload produces a scene.',
  loading: 'Loading scene…',
  ready: 'Scene loaded.',
  unavailable: 'This view is not available yet.',
  error: 'The scene could not be shown.',
});

export function layoutOf(state, opts = {}) {
  const cur = STAGES.indexOf(stageOf(state));
  const failed = /\.(failed|cancelled)$/.test(state.phase);
  const request = viewerRequestOf(state, opts);
  return {
    slots: SLOTS,
    phase: state.phase,
    stages: STAGES.map((id, i) => ({ id, label: STAGE_LABEL[id], status: i < cur ? 'done' : i === cur ? 'current' : 'todo', failed: i === cur && failed })),
    viewport: { request, key: request && [sceneKey(request.scene), request.mode, request.audience].join('|'),
      banner: state.scene?.evidence === 'synthetic' ? SYNTHETIC_SCENE_BANNER : null },
    jobStatus: { label: PHASE_LABEL[state.phase], jobId: state.job?.id ?? null, error: state.error, surface: statusSurface(state, opts.log) },
  };
}

export const ALL_PHASES = PHASES;
