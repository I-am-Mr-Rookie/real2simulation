'use client';

export default function ErrorBoundary({ reset }) {
  return <section className="reading" role="alert">
    <h1>This page could not load</h1>
    <p>Try again or return to the demo library. No processing job has been cancelled.</p>
    <button type="button" onClick={() => reset()}>Try again</button>
    <a href="/library">Demo library</a>
  </section>;
}
