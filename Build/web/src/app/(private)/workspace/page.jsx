import { redirect } from 'next/navigation';
import { requireOwnFixtureSceneId } from '../../../auth/server-access';

export default async function OwnWorkspace() {
  const sceneId = await requireOwnFixtureSceneId();
  redirect('/workspace/' + sceneId);
}
