import LibraryClient from './LibraryClient.jsx';
import FeaturedRun from '../home/FeaturedRun';
import './library.css';

export default function Library() {
  return <section className="page-wide">
    <p className="eyebrow">Public · no account needed</p>
    <h1>Demo library</h1>
    <p className="lede">One real tracked run, then simulated trajectories and practice setups. Nothing here is a calibrated measurement.</p>
    <FeaturedRun />
    <LibraryClient />
  </section>;
}
