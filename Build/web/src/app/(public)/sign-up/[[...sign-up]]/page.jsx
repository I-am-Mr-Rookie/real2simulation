import { SignUp } from '@clerk/nextjs';
import { getClerkConfiguration } from '../../../../auth/server-config';

export const dynamic = 'force-dynamic';
export default function SignUpPage() {
  if (!getClerkConfiguration().available) return <section aria-labelledby="auth-title">
    <h1 id="auth-title">Sign-up unavailable</h1>
    <p>Authentication is not configured. The demo library remains available without sign-in.</p>
    <a href="/library">Browse the demo library</a>
  </section>;
  return <section aria-labelledby="auth-title">
    <h1 id="auth-title">Join Real2Simulation</h1>
    <SignUp routing="path" path="/sign-up" />
  </section>;
}
