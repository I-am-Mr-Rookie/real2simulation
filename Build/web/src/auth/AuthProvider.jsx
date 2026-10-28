import { ClerkProvider } from '@clerk/nextjs';
import { getClerkConfiguration } from './server-config';

export default function AuthProvider({ children }) {
  const config = getClerkConfiguration();
  if (!config.available) return children;
  return <ClerkProvider publishableKey={config.publishableKey}
    signInUrl="/sign-in" signUpUrl="/sign-up"
    signInFallbackRedirectUrl="/library" signUpFallbackRedirectUrl="/library">
    {children}
  </ClerkProvider>;
}
