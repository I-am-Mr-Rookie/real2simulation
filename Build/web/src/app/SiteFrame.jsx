import { createElement as h } from 'react';
import Link from 'next/link';
import AccountNav from '../shell/AccountNav';
import { icon } from '../shell/icons.mjs';
import { THEME_CSS } from '../shell/theme.mjs';
import ThemeToggle from './ThemeToggle';
import { REPO_URL, GITHUB_MARK } from './(public)/MarketingArt';

// S15au: chrome-only overrides (styles.css is outside this run): larger mark, icon-only links, one-line workspace link on phones,
// wordmark text back where it fits beside the signed-in nav (>=521px), tighter 40px targets at <=420px so 375px does not overflow.
const FRAME_CSS = '.brand-mark{width:34px;height:34px}.site-header nav .nav-icon .r2s-icon{margin-right:0}'
  + '@media (max-width:700px){.site-header nav a[href="/workspace"]{font-size:0;white-space:nowrap}.site-header nav a[href="/workspace"]::before{content:"Workspace" / "";font-size:.9rem}}'
  + '@media (min-width:521px) and (max-width:700px){.wordmark{font-size:1rem;gap:.5rem}}'
  + '@media (max-width:420px){.site-header{gap:.5rem}.site-header nav{gap:0}.site-header nav a{min-width:2.5rem;padding-inline:.35rem}}';

// S15ai: branded public chrome (shell/ShellFrame unchanged; same skip link, nav targets and footer copy).
export default function SiteFrame({ children, authAvailable = false }) {
  return <>
    <style dangerouslySetInnerHTML={{ __html: THEME_CSS + FRAME_CSS }} />
    <a className="skip-link" href="#main">Skip to content</a>
    <header className="site-header">
      <Link className="wordmark" href="/"><img className="brand-mark art-light" src="/brand/mark.svg" width="34" height="34" alt="" /><img className="brand-mark art-dark" src="/brand/mark-dark.svg" width="34" height="34" alt="" />Real2Simulation</Link>
      <nav aria-label="Main navigation">
        <Link href="/library" title="Demo library">{icon(h, 'book', 16)}<span className="nav-label">Demo library</span></Link>
        <Link href="/lab" title="Local simulation lab">{icon(h, 'flask', 16)}<span className="nav-label">Local simulation lab</span></Link>
        <a className="nav-icon" href={REPO_URL} target="_blank" rel="noopener noreferrer" aria-label="GitHub repository" title="GitHub repository">{GITHUB_MARK}</a>
        <ThemeToggle />
        {authAvailable ? <AccountNav /> : <Link className="nav-cta" href="/sign-in">Sign in</Link>}
      </nav>
    </header>
    <main id="main">{children}</main>
    <footer className="site-footer"><strong>Development build</strong><span>Sign in to upload your own videos. Every result is labelled MEASURED, MODEL-ESTIMATED or SIMULATED, with its uncertainty; template lab results are not calibrated measurements.</span><small>Powered by Stability AI</small></footer>
  </>;
}
