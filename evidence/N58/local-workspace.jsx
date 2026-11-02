'use client';
// Local-only harness, copied to /lab/n58-check for headed verification, removed before the final build.
// No auth bypass ships: Playwright routes /api/workspace to an isolated public-data-only local API.
import PrivateWorkspace from '../../../../shell/PrivateWorkspace.mjs';
import ThemeToggle from '../../../ThemeToggle';
import { initialState } from '../../../../workspace/workflow.mjs';
import '../../../../workspace/workspace.css';
export default function LocalPublicWorkspace() {
  return <PrivateWorkspace scene={{ sceneId: 'n58-public-sample', title: 'Public sample workspace', notice: 'Local verification harness. Authentication not tested.', state: initialState() }} controls={<ThemeToggle />} />;
}
