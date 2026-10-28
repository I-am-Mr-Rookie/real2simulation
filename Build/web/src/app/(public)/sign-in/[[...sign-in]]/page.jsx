import { SignIn } from '@clerk/nextjs';
import { getClerkConfiguration } from '../../../../auth/server-config';

export const dynamic = 'force-dynamic';
export default function SignInPage() {
  if (!getClerkConfiguration().available) return <section aria-labelledby="auth-title">
    <h1 id="auth-title">Sign-in unavailable</h1>
    <p>Authentication is not configured. The demo library remains available without sign-in.</p>
    <a href="/library">Browse the demo library</a>
  </section>;
  return <section aria-labelledby="auth-title">
    <h1 id="auth-title">Sign in to Real2Simulation</h1>
    <SignIn routing="path" path="/sign-in" />
  </section>;
}
