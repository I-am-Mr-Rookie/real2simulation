import { createElement as h } from 'react';
import Link from 'next/link';
import AccountNav from '../shell/AccountNav';
import { icon } from '../shell/icons.mjs';
import { THEME_CSS } from '../shell/theme.mjs';
import ThemeToggle from './ThemeToggle';

// S15ai: branded public chrome (shell/ShellFrame unchanged; same skip link, nav targets and footer copy).
export default function SiteFrame({ children, authAvailable = false }) {
  return <>
    <style dangerouslySetInnerHTML={{ __html: THEME_CSS }} />
    <a className="skip-link" href="#main">Skip to content</a>
    <header className="site-header">
      <Link className="wordmark" href="/"><img className="brand-mark art-light" src="/brand/mark.svg" width="28" height="28" alt="" /><img className="brand-mark art-dark" src="/brand/mark-dark.svg" width="28" height="28" alt="" />Real2Simulation</Link>
      <nav aria-label="Main navigation">
        <Link href="/library" title="Demo library">{icon(h, 'book', 16)}<span className="nav-label">Demo library</span></Link>
        <Link href="/lab" title="Local simulation lab">{icon(h, 'flask', 16)}<span className="nav-label">Local simulation lab</span></Link>
        <ThemeToggle />
        {authAvailable ? <AccountNav /> : <Link className="nav-cta" href="/sign-in">Sign in</Link>}
      </nav>
    </header>
    <main id="main">{children}</main>
    <footer className="site-footer"><strong>Development build</strong><span>Synthetic lab results are not calibrated measurements. Uploads are limited to approved licensed clips in the signed-in workspace.</span></footer>
  </>;
}
