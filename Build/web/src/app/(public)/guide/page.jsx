import Link from 'next/link';
import { GUIDE } from './guide-data.mjs';
import './guide.css';

export const metadata = { title: 'Guide | Real2Simulation' };

export default function Guide() {
  return <section className="page-wide guide">
    <p className="eyebrow">Public · no account needed</p>
    <h1>Guide</h1>
    <p className="lede">A beginner walkthrough with screenshots from the live development site. <Link href="/library">Try the demo library</Link> first if you like.</p>
    <nav aria-label="Guide sections"><ul className="guide-toc">{GUIDE.map((s) => <li key={s.id}><a href={'#' + s.id}>{s.title}</a></li>)}</ul></nav>
    {GUIDE.map((s) => <section key={s.id} id={s.id} className="guide-sec">
      <h2>{s.title}</h2>
      <p>{s.text}</p>
      {s.steps && <ol>{s.steps.map((t) => <li key={t}>{t}</li>)}</ol>}
      <div className="guide-shots">{s.images.map(([f, alt]) => <img key={f} src={'/guide/' + f} alt={alt} loading="lazy" />)}</div>
    </section>)}
  </section>;
}
