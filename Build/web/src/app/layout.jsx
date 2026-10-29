import './styles.css';
import ShellFrame from '../shell/ShellFrame';
import AuthProvider from '../auth/AuthProvider';
import { getClerkConfiguration } from '../auth/server-config';

// Re-evaluate configuration per request; never cache a build-time provider when
// runtime credentials are absent. Private resource checks remain server-side.
export const dynamic = 'force-dynamic';

export const metadata = {
  title: 'Real2Simulation',
  description: 'A workbench for testing physical explanations against video.'
};

export default function RootLayout({ children }) {
  const authAvailable = getClerkConfiguration().available;
  return <html lang="en"><body><AuthProvider><ShellFrame authAvailable={authAvailable}>{children}</ShellFrame></AuthProvider></body></html>;
}
