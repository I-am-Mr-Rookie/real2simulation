// Local production-server boundary checks; synthetic configuration is NOT a real Clerk session.
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../../', import.meta.url));
for (const args of [[], ['--synthetic-clerk'], ['--synthetic-clerk', '--container-bind']]) {
  const result = spawnSync(process.execPath, ['Build/web/src/shell/smoke.mjs', ...args], {
    cwd: root, encoding: 'utf8', timeout: 60_000,
    env: { ...process.env, RAILWAY_ENVIRONMENT_NAME: 'dev' },
  });
  process.stdout.write(result.stdout ?? '');
  process.stderr.write(result.stderr ?? '');
  assert.ifError(result.error);
  assert.equal(result.status, 0, `bounded smoke ${args.join(' ') || 'missing-config'}`);
}
