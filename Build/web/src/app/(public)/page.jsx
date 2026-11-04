import { createElement as h } from 'react';
import Link from 'next/link';
import { icon } from '../../shell/icons.mjs';
import MarketingArt, { REPO_URL, GITHUB_MARK } from './MarketingArt';
import FeaturedRun from './home/FeaturedRun';
import HeroClock from './home/HeroClock';
import ScrollMount from './home/ScrollMount';
import FallCalc from './home/FallCalc';
import './home/home.css';

const FEATURES = [
  { id: 'a2', glyph: 'film', title: 'Film it', line: 'Your own phone clip. A simple drop works best today.', alt: 'A phone records a pendulum at three swing positions.' },
  { id: 'a3', glyph: 'chart', title: 'Measure it', line: 'Tracked points, error bars, a fitted model.', alt: 'Measurement points with uncertainty bars and a fitted curve under a magnifier.' },
  { id: 'a4', glyph: 'play', title: 'Remix it', line: 'Replay it in 3D, then ask what if.', alt: 'A simulated ball and its ghost position above a wireframe floor.' }
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
    <ScrollMount />
    {/* N90 scroll-craft: pinned hero; the scroll is the clip clock of a real tracked drop (HeroClock). */}
    <section className="hero-act" data-sc-act="pin" data-sc-span="2.4" data-pin-min="861 700">
      <div className="hero hero-stage" data-sc-stage>
      <div className="hero-copy">
        <p className="kicker">REAL → SIMULATION</p>
        <h1 className="home-h1"><span>Film Physics</span><span>Simulate it in 3D</span></h1>
        <p className="hero-sub">{'Point your phone at a real experiment. Get a 3D replay, measurements with error bars, and a lab to ask "what if".'}</p>
        <div className="actions">
          <Link className="primary-link" href="/library">{icon(h, 'book', 16)}Try the demo library</Link>
          <Link className="secondary-link" href="/lab?editor=1&template=physics-lab">{icon(h, 'flask', 16)}Open the physics lab</Link>
        </div>
        <p className="trust-line">For physics classes. No video and no account needed to start.</p>
      </div>
      <HeroClock>A real stock clip, tracked by hosted Meta SAM 3.1. Scroll to play it.</HeroClock>
      </div>
    </section>
    <section className="show room-out" data-sc-act="flow" aria-labelledby="room-out">
      <h2 id="room-out">A room video becomes a lab</h2>
      <figure className="hero-art slab">
        {/* N89: real product output first, so the promise has visible proof. N90: the wipe is the change of state. */}
        <div data-sc-reveal="up" data-sc-reveal-at="0.06 0.4"><img src="/guide/room-tab.webp" width={1280} height={720} style={{ width: '100%', height: 'auto', display: 'block' }}
          alt="The lab editor showing a classroom reconstructed from a phone video: walls, windows, chairs and tables, with the source video frame in the side panel." /></div>
        <figcaption>Real output.<span>A classroom video (SAMPLE, RECORDED) turned into an editable physics lab. Geometry MODEL-ESTIMATED, scale unverified.</span></figcaption>
      </figure>
    </section>
    <FeaturedRun />
    <section className="show featured-run class-act" aria-labelledby="class-use" data-sc-act="pin" data-sc-span="2" data-pin-min="861 760">
      <div data-sc-stage className="class-stage">
      <h2 id="class-use">Use it in a class</h2>
      <p className="show-line">One lesson period, one question, two kinds of evidence: a simulation and the students' own clip.</p>
      {/* N90: pinned on desktop, the four steps light up in lesson order from the act progress (--sc-p). */}
      <ol className="fr-steps lit-steps" data-flow-stagger>
        <li className="card" style={{ '--i': 0 }}><span className="chip" data-tone="sim">SIMULATED</span><h3>1. Predict, then test</h3><p>Pick a lesson in the <Link href="/lab?editor=1&template=physics-lab">physics lab</Link>, predict, run two drops.</p></li>
        <li className="card" style={{ '--i': 1 }}><span className="chip" data-tone="ok">RECORDED</span><h3>2. Film a real drop</h3><p>Phone on a stand, plain wall, ruler for the ball size.</p></li>
        <li className="card" style={{ '--i': 2 }}><span className="chip" data-tone="warn">scale assumed</span><h3>3. Measure it</h3><p>SAM 3.1 tracks it; the fitter returns g with uncertainty.</p></li>
        <li className="card" style={{ '--i': 3 }}><span className="chip" data-tone="warn">what-if</span><h3>4. Compare and redo</h3><p>Replay in 3D, change gravity, copy a worksheet.</p></li>
      </ol>
      <p className="show-line">Why predict first: students who predict before a demo understand it better than students who only watch (<a href="https://doi.org/10.1119/1.1707018">Crouch et al., Am. J. Phys. 72, 835, 2004</a>).</p>
      </div>
    </section>
    <ul className="features" data-sc-in>
      {FEATURES.map((f) => <li key={f.id} className="feature card">
        <MarketingArt id={f.id} width={800} height={600} alt={f.alt} />
        <h3>{icon(h, f.glyph, 18)}{f.title}</h3>
        <p>{f.line}</p>
      </li>)}
    </ul>
    <p className="honesty-strip" data-sc-in>{icon(h, 'alert', 18)}Imperfect inputs are welcome. Results show uncertainty and a "scale unverified" or "scale assumed" label when needed.</p>
    <Link className="mg-hook card" href="/lab" data-sc-in>{icon(h, 'compass', 18)}<strong>Guess the Gravity</strong><span>Mystery-g mode: a SIMULATED drop with g hidden. Guess, then reveal.</span></Link>

    <section className="show show-split show-agent" aria-labelledby="agent" data-sc-act="flow">
      <div className="show-copy">
        <h2 id="agent">The agent asks instead of guessing</h2>
        <p className="show-line">Missing a scale or a frame rate? It asks you, then labels the answer.</p>
      </div>
      <div className="agent-art">
        <figure className="slab" data-sc-parallax="-0.09"><MarketingArt set="app" id="b5" width={384} height={384} alt="Illustration of the agent asking a question about the clip." /><figcaption>The agent asks</figcaption></figure>
        <figure className="slab" data-sc-parallax="0.05"><MarketingArt set="app" id="b6" width={512} height={512} alt="Illustration of the agent using the answer in the analysis." /><figcaption>Your answer, labelled</figcaption></figure>
      </div>
    </section>

    <section className="show show-split show-honest" aria-labelledby="honest">
      <div className="show-copy">
        <h2 id="honest">Honest by design</h2>
        <p className="show-line">Every number shows where it came from: measured, simulated or what-if.</p>
      </div>
      <ul className="label-list" data-sc-in data-sc-stagger="50">
        {LABELS.map(([tone, word, line]) => <li key={word} className="label-row card"><span className="chip" data-tone={tone || undefined}>{word}</span><span>{line}</span></li>)}
      </ul>
    </section>

    <section className="show show-split show-cta" aria-labelledby="cta">
      <div className="show-copy">
        <h2 id="cta">See it for yourself</h2>
        <p className="show-line">Start with a demo clip, run the physics lab template, or read the code.</p>
        <FallCalc />
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
