import Link from 'next/link';

export default function NotFound() {
  return <section className="reading">
    <h1>Page unavailable</h1>
    <p>This page is not available. No scene or job data has been loaded.</p>
    <p>Private workspaces remain unavailable until sign-in and ownership checks are connected.</p>
    <Link href="/library">Browse the public library</Link>
  </section>;
}
