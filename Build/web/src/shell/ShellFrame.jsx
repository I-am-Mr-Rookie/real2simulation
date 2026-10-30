import Link from 'next/link';
import AccountNav from './AccountNav';

export default function ShellFrame({ children, authAvailable = false }) {
  return <>
    <a className="skip-link" href="#main">Skip to content</a>
    <header className="site-header">
      <Link className="wordmark" href="/"><span className="wordmark-mark" aria-hidden="true">R2S</span>Real2Simulation</Link>
      <nav aria-label="Main navigation"><Link href="/library">Demo library</Link><Link href="/lab">Local simulation lab</Link>{authAvailable ? <AccountNav /> : <Link className="nav-cta" href="/sign-in">Sign in</Link>}</nav>
    </header>
    <main id="main">{children}</main>
    <footer className="site-footer"><strong>Development build</strong><span>Synthetic lab results are not calibrated measurements. Uploads are limited to approved licensed clips in the signed-in workspace.</span></footer>
  </>;
}
