import './styles.css';
import ShellFrame from '../shell/ShellFrame';
import AuthProvider from '../auth/AuthProvider';

// Re-evaluate configuration per request; never cache a build-time provider when
// runtime credentials are absent. Private resource checks remain server-side.
export const dynamic = 'force-dynamic';

export const metadata = {
  title: 'Real2Simulation',
  description: 'A workbench for testing physical explanations against video.'
};

export default function RootLayout({ children }) {
  return <html lang="en"><body><AuthProvider><ShellFrame>{children}</ShellFrame></AuthProvider></body></html>;
}
