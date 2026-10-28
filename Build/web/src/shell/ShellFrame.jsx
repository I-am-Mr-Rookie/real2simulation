import Link from 'next/link';

export default function ShellFrame({ children }) {
  return <>
    <a className="skip-link" href="#main">Skip to content</a>
    <header className="site-header">
      <Link className="wordmark" href="/">Real2Simulation</Link>
      <nav aria-label="Main navigation"><Link href="/library">Demo library</Link><Link href="/lab">Local simulation lab</Link><Link href="/sign-in">Sign in</Link></nav>
    </header>
    <main id="main">{children}</main>
    <footer className="site-footer">Development build. Synthetic lab results are not calibrated measurements. No uploads are enabled.</footer>
  </>;
}
