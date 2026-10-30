import './styles.css';
import { Instrument_Sans, Space_Mono } from 'next/font/google';
import ShellFrame from '../shell/ShellFrame';
import AuthProvider from '../auth/AuthProvider';
import { getClerkConfiguration } from '../auth/server-config';

// Self-hosted by Next at build time; CSS tokens fall back to system faces if unavailable.
const sans = Instrument_Sans({ subsets: ['latin'], display: 'swap', variable: '--r2s-face-sans' });
const mono = Space_Mono({ subsets: ['latin'], weight: ['400', '700'], display: 'swap', variable: '--r2s-face-mono' });

// Re-evaluate configuration per request; never cache a build-time provider when
// runtime credentials are absent. Private resource checks remain server-side.
export const dynamic = 'force-dynamic';

export const metadata = {
  title: 'Real2Simulation',
  description: 'A workbench for testing physical explanations against video.'
};

export const viewport = { themeColor: '#f3eee3' };

export default function RootLayout({ children }) {
  const authAvailable = getClerkConfiguration().available;
  return <html lang="en" className={sans.variable + ' ' + mono.variable}><body><AuthProvider><ShellFrame authAvailable={authAvailable}>{children}</ShellFrame></AuthProvider></body></html>;
}
