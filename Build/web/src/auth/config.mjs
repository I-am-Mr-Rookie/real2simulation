// Pure server configuration parser. Never pass the environment or secret to a client.
// Syntax is checked here, NOT credential validity or instance strategy settings.
export function clerkConfiguration(env) {
  const publishableKey = env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;
  const secret = env.CLERK_SECRET_KEY;
  const match = typeof publishableKey === 'string'
    && /^(pk_(test|live)_)([A-Za-z0-9+/]+={0,2})$/.exec(publishableKey);
  if (!match || typeof secret !== 'string'
      || !new RegExp(`^sk_${match[2]}_[A-Za-z0-9_-]+$`).test(secret)) {
    return { available: false };
  }
  const host = Buffer.from(match[3], 'base64').toString('utf8');
  if (!/^(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,}\$$/i.test(host)) {
    return { available: false };
  }
  return { available: true, publishableKey };
}
