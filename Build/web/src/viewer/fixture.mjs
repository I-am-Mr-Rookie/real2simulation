// Synthetic fixture scene for viewer development (S09a).
// Points at the single S05a bundle via the S04a fixture mount; no geometry copy.
// Authored geometry only: never reconstruction, measured/simulated, physics or Gate R evidence.
import { deepFreeze } from './common.mjs';

export const SYNTHETIC_BANNER =
  'SYNTHETIC fixture — authored geometry, not reconstruction, physics or Gate R evidence';

export const SYNTHETIC_FIXTURE = deepFreeze({
  sceneId: 'synthetic-room-v1',
  repositoryManifest: 'test-data/synthetic/scene/room-v1/scene.json',
  reservedRoute: '/library/synthetic-room-v1',
  gateEvidence: false,
  request: {
    contract_version: '1.0.0', kind: 'viewer', audience: 'guest', mode: 'inspect',
    scene: { scene_id: 'synthetic-room-v1', scene_version: '1.0.0', access: 'public-library', evidence: 'synthetic' },
  },
});
