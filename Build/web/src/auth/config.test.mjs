import test from 'node:test';
import assert from 'node:assert/strict';
import { clerkConfiguration } from './config.mjs';

const pk = 'pk_test_' + Buffer.from('example.clerk.accounts.dev$').toString('base64');
const sk = 'sk_test_SYNTHETIC_ONLY_NOT_A_CREDENTIAL';
test('missing and partial configuration disables Clerk without exposing values', () => {
  for (const env of [{}, { NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: pk }, { CLERK_SECRET_KEY: sk }]) {
    assert.deepEqual(clerkConfiguration(env), { available: false });
  }
});
test('blank, malformed, mismatched and unsafe configuration fails closed', () => {
  for (const [publicKey, secretKey] of [
    ['', sk], [pk, ''], ['pk_test_garbage', sk], [pk, 'oops'],
    [pk, 'sk_live_synthetic'], ['pk_test_' + Buffer.from('https://bad/$').toString('base64'), sk],
    ['pk_test_' + Buffer.from('bad host$').toString('base64'), sk],
    ['pk_test_' + Buffer.from('example.com').toString('base64'), sk]
  ]) assert.deepEqual(clerkConfiguration({ NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: publicKey,
    CLERK_SECRET_KEY: secretKey }), { available: false });
});
test('configured result exposes only the public key, never secret or custom OAuth credentials', () => {
  const result = clerkConfiguration({ NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: pk,
    CLERK_SECRET_KEY: sk, GOOGLE_CLIENT_SECRET: 'DO_NOT_RETURN' });
  assert.deepEqual(result, { available: true, publishableKey: pk });
  assert.ok(!JSON.stringify(result).includes(sk));
});
test('accepts unpadded Clerk publishable keys', () => {
  const unpadded = pk.replace(/=+$/, '');
  assert.deepEqual(clerkConfiguration({ NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: unpadded,
    CLERK_SECRET_KEY: sk }), { available: true, publishableKey: unpadded });
});
