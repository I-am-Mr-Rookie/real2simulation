import { requirePrivateSceneView } from '../../../../auth/server-access';
import PrivateWorkspace from '../../../../shell/PrivateWorkspace.mjs';
import ThemeToggle from '../../../ThemeToggle';
import { UserButton } from '@clerk/nextjs';

export default async function Workspace({ params }) {
  const { sceneId } = await params;
  const scene = await requirePrivateSceneView(sceneId);
  return <PrivateWorkspace scene={scene} controls={<><ThemeToggle /><UserButton /></>} />;
}
