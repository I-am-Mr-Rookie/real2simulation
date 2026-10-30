'use client';

export default function ErrorBoundary({ reset }) {
  return <section className="reading" role="alert">
    <p className="eyebrow">Error</p>
    <h1>This page could not load</h1>
    <div className="state-card"><span className="state-tag" data-tone="danger">Load failed</span>
      <p>Try again or return to the demo library. No processing job has been cancelled.</p></div>
    <div className="actions" style={{ marginTop: '2rem' }}>
      <button type="button" onClick={() => reset()}>Try again</button>
      <a className="secondary-link" href="/library">Demo library</a>
    </div>
  </section>;
}
