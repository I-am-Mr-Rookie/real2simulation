// S15ay: post sign-in/sign-up lands on the private workspace, not /library.
import assert from 'node:assert/strict';
import test from 'node:test';
import { readFile } from 'node:fs/promises';

test('Clerk fallback redirects go to /workspace', async () => {
  const s = await readFile(new URL('../../Build/web/src/auth/AuthProvider.jsx', import.meta.url), 'utf8');
  assert.match(s, /signInFallbackRedirectUrl="\/workspace"/);
  assert.match(s, /signUpFallbackRedirectUrl="\/workspace"/);
});
