import LibraryClient from './LibraryClient.jsx';
import FeaturedRun from '../home/FeaturedRun';
import './library.css';

export default function Library() {
  return <section className="page-wide">
    <p className="eyebrow">Public · no account needed</p>
    <h1>Demo library</h1>
    <p className="lede">Real tracked runs (twelve phone book drops with a ruler-measured scale, and a stock apple clip with none), then simulated trajectories and practice setups. None of it is a calibrated instrument.</p>
    <FeaturedRun />
    <LibraryClient />
  </section>;
}
