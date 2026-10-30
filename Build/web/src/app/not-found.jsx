import Link from 'next/link';

export default function NotFound() {
  return <section className="reading">
    <p className="eyebrow">404 · not found</p>
    <h1>Page unavailable</h1>
    <div className="state-card">
      <p>This page is not available. No scene or job data has been loaded.</p>
      <p style={{ marginTop: '1rem' }}>Private workspaces require sign-in and scene ownership.</p>
    </div>
    <p style={{ marginTop: '2rem' }}><Link className="secondary-link" href="/library">Browse the public library</Link></p>
  </section>;
}
