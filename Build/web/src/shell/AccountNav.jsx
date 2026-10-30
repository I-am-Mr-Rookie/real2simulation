'use client';
import Link from 'next/link';
import { UserButton, useAuth } from '@clerk/nextjs';

// Rendered only inside ClerkProvider. UserButton supplies account management and sign-out.
export default function AccountNav() {
  const { isLoaded, isSignedIn } = useAuth();
  if (!isLoaded) return null; // S15r: never show 'Sign in' before Clerk knows the session (was shown while signed in)
  if (isSignedIn) return <><Link href="/workspace" prefetch={false}>Private workspace</Link><UserButton /></>;
  return <Link className="nav-cta" href="/sign-in">Sign in</Link>;
}
