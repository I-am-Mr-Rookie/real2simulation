import { requirePrivateScene } from '../../../../auth/server-access';

// Guard the leaf as well: layouts are not a data authorization boundary.
// Future workspace/viewer/job-status slots must mount only after authorization.
export default async function Workspace({ params }) {
  const { sceneId } = await params;
  await requirePrivateScene(sceneId);
  // No private repository/viewer is connected. Do not fabricate a workspace.
  return null;
}
