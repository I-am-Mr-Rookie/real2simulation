import Link from 'next/link';

export default function Home() {
  return <section className="entry">
    <div>
      <h1>Put the physical world to the test.</h1>
      <p className="lede">From video to a virtual lab. Compare a physical explanation with what happens next.</p>
      <p>This workbench is under construction. The library will host explicitly labelled demos when they are ready.</p>
      <Link className="primary-link" href="/library">Open demo library</Link>
    </div>
    <figure className="bench">
      <svg viewBox="0 0 420 230" role="img" aria-labelledby="bench-title">
        <title id="bench-title">Illustrative camera and lab bench, not a reconstruction or measurement</title>
        <path d="M35 182H385 M70 182V205 M350 182V205" fill="none" stroke="currentColor" strokeWidth="3" />
        <rect x="48" y="80" width="70" height="50" rx="6" fill="none" stroke="currentColor" strokeWidth="3" />
        <path d="M118 92L142 82V128L118 118 M82 130V181 M65 181L82 150L99 181" fill="none" stroke="currentColor" strokeWidth="3" />
        <path d="M157 106H290" stroke="currentColor" strokeDasharray="5 7" strokeWidth="2" />
        <circle cx="315" cy="111" r="28" fill="none" stroke="currentColor" strokeWidth="3" />
        <path d="M315 139V181 M285 181H345" fill="none" stroke="currentColor" strokeWidth="3" />
      </svg>
      <figcaption>Observe. Model. Test.<span>Illustration only, not scene evidence.</span></figcaption>
    </figure>
  </section>;
}
