import './styles.css';
import { Instrument_Sans, Space_Mono } from 'next/font/google';
import SiteFrame from './SiteFrame';
import AuthProvider from '../auth/AuthProvider';
import { getClerkConfiguration } from '../auth/server-config';
import SwRegister from '../pwa/SwRegister';
import { THEME_SCRIPT } from '../shell/theme.mjs';

// Self-hosted by Next at build time; CSS tokens fall back to system faces if unavailable.
const sans = Instrument_Sans({ subsets: ['latin'], display: 'swap', variable: '--r2s-face-sans' });
const mono = Space_Mono({ subsets: ['latin'], weight: ['400', '700'], display: 'swap', variable: '--r2s-face-mono' });

// Re-evaluate configuration per request; never cache a build-time provider when
// runtime credentials are absent. Private resource checks remain server-side.
export const dynamic = 'force-dynamic';

export const metadata = {
  title: 'Real2Simulation',
  description: 'A workbench for testing physical explanations against video.',
  manifest: '/pwa/manifest.webmanifest',
  icons: { icon: [{ url: '/brand/favicon.ico', sizes: 'any' }, { url: '/brand/mark-32.png', sizes: '32x32', type: 'image/png' }, { url: '/brand/mark-192.png', sizes: '192x192', type: 'image/png' }], apple: { url: '/brand/mark-192.png', sizes: '192x192' } },
  openGraph: { title: 'Real2Simulation', description: 'A workbench for testing physical explanations against video.', images: [{ url: '/images/marketing/a5-light-line@1x.png', width: 1200, height: 630, alt: 'Real2Simulation: video to a labelled simulation.' }] },
  twitter: { card: 'summary_large_image', images: ['/images/marketing/a5-light-line@1x.png'] }
};

export const viewport = { themeColor: [{ media: '(prefers-color-scheme: light)', color: '#f6f6f4' }, { media: '(prefers-color-scheme: dark)', color: '#0c0c10' }] };

export default function RootLayout({ children }) {
  const authAvailable = getClerkConfiguration().available;
  // THEME_SCRIPT sets <html data-theme> before first paint (no flash); React must not warn about that pre-hydration attribute.
  return <html lang="en" className={sans.variable + ' ' + mono.variable} suppressHydrationWarning><head><script dangerouslySetInnerHTML={{ __html: THEME_SCRIPT }} /></head><body><AuthProvider><SiteFrame authAvailable={authAvailable}>{children}</SiteFrame></AuthProvider><SwRegister /></body></html>;
}
