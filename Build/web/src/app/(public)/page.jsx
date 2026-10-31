import { createElement as h } from 'react';
import Link from 'next/link';
import { icon } from '../../shell/icons.mjs';
import MarketingArt from './MarketingArt';

const FEATURES = [
  { id: 'a2', glyph: 'film', title: 'Record', line: 'Any licensed clip of a swing, drop or roll.', alt: 'A phone records a pendulum at three swing positions.' },
  { id: 'a3', glyph: 'chart', title: 'Fit', line: 'Tracked points, uncertainty bars, a fitted model.', alt: 'Measurement points with uncertainty bars and a fitted curve under a magnifier.' },
  { id: 'a4', glyph: 'play', title: 'Replay', line: 'A simulation you can test against what happens next.', alt: 'A simulated ball and its ghost position above a wireframe floor.' }
];

export default function Home() {
  return <>
    <section className="hero">
      <div className="hero-copy">
        <p className="kicker">REAL → SIMULATION</p>
        <h1>Film physics. Get a measured g.</h1>
        <p className="hero-sub">Track the object, fit the motion, replay it — every number labelled.</p>
        <div className="actions">
          <Link className="primary-link" href="/library">{icon(h, 'book', 16)}Try the demo library</Link>
          <Link className="secondary-link" href="/lab">{icon(h, 'flask', 16)}Open the lab</Link>
        </div>
        <ul className="chip-row" aria-label="Every result carries one of these labels">
          <li className="chip" data-tone="ok">RECORDED</li><li className="chip" data-tone="sim">SIMULATED</li><li className="chip" data-tone="warn">what-if</li>
        </ul>
      </div>
      <figure className="hero-art slab">
        <MarketingArt id="a1" width={1600} height={1000} eager alt="A phone records a falling ball beside a scale; tracked positions continue into a wireframe replay." />
        <figcaption>Observe. Model. Test.<span>Illustration only, not scene evidence.</span></figcaption>
      </figure>
    </section>
    <ul className="features">
      {FEATURES.map((f) => <li key={f.id} className="feature card">
        <MarketingArt id={f.id} width={800} height={600} alt={f.alt} />
        <h3>{icon(h, f.glyph, 18)}{f.title}</h3>
        <p>{f.line}</p>
      </li>)}
    </ul>
    <p className="honesty-strip">{icon(h, 'alert', 18)}We abstain when scale is unverified.</p>
  </>;
}

