import { createElement as h } from 'react';
import Link from 'next/link';
import { icon } from '../../shell/icons.mjs';
import MarketingArt, { REPO_URL, GITHUB_MARK } from './MarketingArt';
import FeaturedRun from './home/FeaturedRun';
import './home/home.css';

const FEATURES = [
  { id: 'a2', glyph: 'film', title: 'Film it', line: 'Your own phone clip. A simple drop works best today.', alt: 'A phone records a pendulum at three swing positions.' },
  { id: 'a3', glyph: 'chart', title: 'Measure it', line: 'Tracked points, error bars, a fitted model.', alt: 'Measurement points with uncertainty bars and a fitted curve under a magnifier.' },
  { id: 'a4', glyph: 'play', title: 'Remix it', line: 'Replay it in 3D, then ask what if.', alt: 'A simulated ball and its ghost position above a wireframe floor.' }
];

const STEPS = [
  ['film', 'Film', 'A ball drop is the best first clip.'],
  ['compass', 'Agent asks', 'It asks for what it cannot see.'],
  ['grid', 'Track', 'Points, frame by frame.'],
  ['chart', 'Fit', 'A model with error bars.'],
  ['play', 'Replay', 'A labelled 3D replay.'],
  ['flask', 'What if', 'Change a value, watch it diverge.']
];

const LABELS = [
  ['ok', 'RECORDED', 'Stored footage or a stored run, shown as it was.'],
  ['ok', 'MEASURED', 'Read from the footage, for example a tracked point.'],
  ['sim', 'SIMULATED', 'Produced by the physics engine.'],
  ['warn', 'MODEL-ESTIMATED', 'A model guess, for example room geometry or mass.'],
  ['warn', 'what-if', 'Your change, not the clip.'],
  [null, 'scale unverified', 'No known size, so pixels, not metres.']
];

export default function Home() {
  return <div className="home-motion">
    <section className="hero">
      <div className="hero-copy">
        <p className="kicker">REAL → SIMULATION</p>
        <h1 className="home-h1"><span>Film Physics</span><span>Simulate it in 3D</span></h1>
        <p className="hero-sub">{'Point your phone at a real experiment. Get a 3D replay, measurements with error bars, and a lab to ask "what if".'}</p>
        <p className="trust-line">For physics students and teachers: turn a class demo into data you can check, then rerun it with different values.</p>
        <div className="actions">
          <Link className="primary-link" href="/library">{icon(h, 'book', 16)}Try the demo library</Link>
          <Link className="secondary-link" href="/lab?editor=1&template=physics-lab">{icon(h, 'flask', 16)}Open the physics lab</Link>
        </div>
        <p className="trust-line">No video needed: the physics lab has two short lessons (does a heavier ball fall faster? does twice the height take twice as long?), and the demo library works without an upload.</p>
        <ul className="chip-row" aria-label="Every result carries one of these labels">
          <li className="chip" data-tone="ok">RECORDED</li><li className="chip" data-tone="sim">SIMULATED</li><li className="chip" data-tone="warn">what-if</li>
        </ul>
        <p className="trust-line">Every number shows where it came from: measured, simulated or what-if.</p>
      </div>
      <figure className="hero-art slab">
        {/* N89: real product output first, so the promise has visible proof. */}
        <img src="/guide/room-tab.webp" width={1280} height={720} fetchPriority="high" style={{ width: '100%', height: 'auto', display: 'block' }}
          alt="The lab editor showing a classroom reconstructed from a phone video: walls, windows, chairs and tables, with the source video frame in the side panel." />
        <figcaption>Real output.<span>A classroom video (SAMPLE, RECORDED) turned into an editable physics lab. Geometry MODEL-ESTIMATED, scale unverified.</span></figcaption>
      </figure>
    </section>
    <FeaturedRun />
    <section className="show featured-run" aria-labelledby="class-use">
      <h2 id="class-use">Use it in a class</h2>
      <p className="show-line">One lesson period, one question, two kinds of evidence: a simulation and the students' own clip.</p>
      <ol className="fr-steps">
        <li className="card"><span className="chip" data-tone="sim">SIMULATED</span><h3>1. Predict, then test</h3><p>Open the <Link href="/lab?editor=1&template=physics-lab">physics lab</Link> and pick a lesson in the Scene panel: does a heavier ball fall faster, does twice the height take twice as long? Students predict, run two drops and compare them with uncertainty. No account needed.</p></li>
        <li className="card"><span className="chip" data-tone="ok">RECORDED</span><h3>2. Film a real drop</h3><p>Phone on a stand, ball in front of a plain wall, 5 to 30 s. Measure the ball diameter with a ruler.</p></li>
        <li className="card"><span className="chip" data-tone="warn">scale assumed</span><h3>3. Measure it</h3><p>Upload after signing in. Meta SAM 3.1 tracks the ball (MEASURED track); type its diameter and the fitter returns g in m/s^2 with error bars, labelled scale assumed (user size).</p></li>
        <li className="card"><span className="chip" data-tone="warn">what-if</span><h3>4. Compare and redo</h3><p>Replay the clip in 3D, change gravity or height, and see where the simulation leaves the measured dots. Copy results gives a worksheet summary.</p></li>
      </ol>
    </section>
    <ul className="features">
      {FEATURES.map((f) => <li key={f.id} className="feature card">
        <MarketingArt id={f.id} width={800} height={600} alt={f.alt} />
        <h3>{icon(h, f.glyph, 18)}{f.title}</h3>
        <p>{f.line}</p>
      </li>)}
    </ul>
    <p className="honesty-strip">{icon(h, 'alert', 18)}Imperfect inputs are welcome. Results show uncertainty and a "scale unverified" or "scale assumed" label when needed.</p>
    <Link className="mg-hook card" href="/lab">{icon(h, 'compass', 18)}<strong>Guess the Gravity</strong><span>Watch a drop. Guess g. Then see the reveal.</span></Link>

    <section className="show show-steps" aria-labelledby="how">
      <h2 id="how">How it works</h2>
      <ol className="steps">
        {STEPS.map(([g, t, l]) => <li key={t} className="step card">{icon(h, g, 18)}<strong>{t}</strong><span>{l}</span></li>)}
      </ol>
    </section>

    <section className="show show-split show-agent" aria-labelledby="agent">
      <div className="show-copy">
        <h2 id="agent">The agent asks instead of guessing</h2>
        <p className="show-line">Missing a scale or a frame rate? It asks you, then labels the answer.</p>
      </div>
      <div className="agent-art">
        <figure className="slab"><MarketingArt set="app" id="b5" width={384} height={384} alt="Illustration of the agent asking a question about the clip." /><figcaption>The agent asks</figcaption></figure>
        <figure className="slab"><MarketingArt set="app" id="b6" width={512} height={512} alt="Illustration of the agent using the answer in the analysis." /><figcaption>Your answer, labelled</figcaption></figure>
      </div>
    </section>

    <section className="show show-split show-honest" aria-labelledby="honest">
      <div className="show-copy">
        <h2 id="honest">Honest by design</h2>
        <p className="show-line">Every result carries one of these labels.</p>
      </div>
      <ul className="label-list">
        {LABELS.map(([tone, word, line]) => <li key={word} className="label-row card"><span className="chip" data-tone={tone || undefined}>{word}</span><span>{line}</span></li>)}
      </ul>
    </section>

    <section className="show show-split show-cta" aria-labelledby="cta">
      <div className="show-copy">
        <h2 id="cta">See it for yourself</h2>
        <p className="show-line">Start with a demo clip, run the physics lab template, or read the code.</p>
      </div>
      <div className="actions">
        <Link className="primary-link" href="/library">{icon(h, 'book', 16)}Try the demo library</Link>
        <Link className="secondary-link" href="/lab?editor=1&template=physics-lab">{icon(h, 'flask', 16)}Open the physics lab</Link>
        <Link className="secondary-link" href="/lab?editor=1&template=blank">{icon(h, 'plus', 16)}Start a blank lab</Link>
        <Link className="secondary-link" href="/lab">{icon(h, 'compass', 16)}Guess the Gravity</Link>
        <a className="secondary-link gh-link" href={REPO_URL} target="_blank" rel="noopener noreferrer">{GITHUB_MARK}Explore the code on GitHub</a>
      </div>
    </section>
  </div>;
}
