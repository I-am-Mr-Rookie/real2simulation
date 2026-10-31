import { createElement as h } from 'react';
import Link from 'next/link';
import { icon } from '../../shell/icons.mjs';
import MarketingArt from './MarketingArt';
import './home/home.css';

const REPO_URL = 'https://github.com/I-am-Mr-Rookie/real2simulation';
// Official GitHub mark, used only for the link to the repository.
const GITHUB_MARK = <svg className="r2s-icon" width="16" height="16" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true" focusable="false"><path d="M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z" /></svg>;

const FEATURES = [
  { id: 'a2', glyph: 'film', title: 'Film it', line: 'A licensed clip of a swing, drop or roll.', alt: 'A phone records a pendulum at three swing positions.' },
  { id: 'a3', glyph: 'chart', title: 'Measure it', line: 'Tracked points, error bars, a fitted model.', alt: 'Measurement points with uncertainty bars and a fitted curve under a magnifier.' },
  { id: 'a4', glyph: 'play', title: 'Remix it', line: 'Replay it in 3D, then ask what if.', alt: 'A simulated ball and its ghost position above a wireframe floor.' }
];

const STEPS = [
  ['film', 'Film', 'A drop, swing or roll.'],
  ['compass', 'Agent asks', 'It asks for what it cannot see.'],
  ['grid', 'Track', 'Points, frame by frame.'],
  ['chart', 'Fit', 'A model with error bars.'],
  ['play', 'Replay', 'A labelled 3D replay.'],
  ['flask', 'What if', 'Change a value, watch it diverge.']
];

const LABELS = [
  ['ok', 'RECORDED', 'Read from the footage.'],
  ['sim', 'SIMULATED', 'Produced by the fitted model.'],
  ['warn', 'what-if', 'Your change, not the clip.'],
  [null, 'scale unverified', 'No trusted ruler, so no metres.']
];

export default function Home() {
  return <div className="home-motion">
    <section className="hero">
      <div className="hero-copy">
        <p className="kicker">REAL → SIMULATION</p>
        <h1 className="home-h1"><span>Film Physics</span><span>Simulate it in 3D</span></h1>
        <p className="hero-sub">{'Point your phone at a real experiment. Get a 3D replay, measurements with error bars, and a lab to ask "what if".'}</p>
        <div className="actions">
          <Link className="primary-link" href="/library">{icon(h, 'book', 16)}Try the demo library</Link>
          <Link className="secondary-link" href="/lab">{icon(h, 'flask', 16)}Open the lab</Link>
        </div>
        <ul className="chip-row" aria-label="Every result carries one of these labels">
          <li className="chip" data-tone="ok">RECORDED</li><li className="chip" data-tone="sim">SIMULATED</li><li className="chip" data-tone="warn">what-if</li>
        </ul>
        <p className="trust-line">Every number shows where it came from: measured, simulated or what-if.</p>
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
    <Link className="mg-hook card" href="/lab">{icon(h, 'compass', 18)}<strong>Guess the Gravity</strong><span>Watch a drop. Guess g. Then see the reveal.</span></Link>

    <section className="show show-steps" aria-labelledby="how">
      <h2 id="how">How it works</h2>
      <ol className="steps">
        {STEPS.map(([g, t, l]) => <li key={t} className="step card">{icon(h, g, 18)}<strong>{t}</strong><span>{l}</span></li>)}
      </ol>
    </section>

    <section className="show show-agent" aria-labelledby="agent">
      <h2 id="agent">The agent asks instead of guessing</h2>
      <p className="show-line">Missing a scale or a frame rate? It asks you, then labels the answer.</p>
      <div className="agent-art">
        <figure className="slab"><MarketingArt set="app" id="b5" width={384} height={384} alt="Illustration of the agent asking a question about the clip." /></figure>
        <figure className="slab"><MarketingArt set="app" id="b6" width={512} height={512} alt="Illustration of the agent using the answer in the analysis." /></figure>
      </div>
    </section>

    <section className="show show-honest" aria-labelledby="honest">
      <h2 id="honest">Honest by design</h2>
      <ul className="label-list">
        {LABELS.map(([tone, word, line]) => <li key={word} className="label-row card"><span className="chip" data-tone={tone || undefined}>{word}</span><span>{line}</span></li>)}
      </ul>
    </section>

    <section className="show show-cta" aria-labelledby="cta">
      <h2 id="cta">See it for yourself</h2>
      <div className="actions">
        <Link className="primary-link" href="/library">{icon(h, 'book', 16)}Try the demo library</Link>
        <Link className="secondary-link" href="/lab">{icon(h, 'flask', 16)}Open the lab</Link>
        <Link className="secondary-link" href="/lab">{icon(h, 'compass', 16)}Guess the Gravity</Link>
        <a className="secondary-link gh-link" href={REPO_URL} target="_blank" rel="noopener noreferrer">{GITHUB_MARK}Explore the code on GitHub</a>
      </div>
    </section>
  </div>;
}
