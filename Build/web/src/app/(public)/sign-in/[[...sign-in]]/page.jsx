import { SignIn } from '@clerk/nextjs';
import { getClerkConfiguration } from '../../../../auth/server-config';
import { clerkAppearance } from '../../../../auth/appearance';

export const dynamic = 'force-dynamic';
export default function SignInPage() {
  if (!getClerkConfiguration().available) return <section className="reading" aria-labelledby="auth-title">
    <p className="eyebrow">Account</p>
    <h1 id="auth-title">Sign-in unavailable</h1>
    <div className="state-card"><span className="state-tag" data-tone="warn">Not configured</span>
    <p>Authentication is not configured. The demo library remains available without sign-in.</p></div>
    <p style={{ marginTop: '2rem' }}><a className="secondary-link" href="/library">Browse the demo library</a></p>
  </section>;
  return <section className="auth-frame" aria-labelledby="auth-title">
    <h1 id="auth-title">Sign in to Real2Simulation</h1>
    <SignIn routing="path" path="/sign-in" appearance={clerkAppearance} />
  </section>;
}
