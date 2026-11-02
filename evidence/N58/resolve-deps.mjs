// Worktree test process only: reuse the installed web dependency, including simulator imports outside Build/web.
import { createRequire, registerHooks } from 'node:module';
import { pathToFileURL } from 'node:url';
const require = createRequire(new URL('../../Build/web/package.json', import.meta.url));
const rapier = pathToFileURL(require.resolve('@dimforge/rapier3d-compat').replace(/rapier\.cjs$/, 'rapier.mjs')).href;
registerHooks({ resolve(specifier, context, next) {
  return next(specifier === '@dimforge/rapier3d-compat' ? rapier : specifier, context);
} });
