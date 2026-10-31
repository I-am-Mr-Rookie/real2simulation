import LibraryClient from './LibraryClient.jsx';
import './library.css';

export default function Library() {
  return <section className="page-wide">
    <p className="eyebrow">Public · no account needed</p>
    <h1>Demo library</h1>
    <p className="lede">Simulated trajectories and honest placeholders. Nothing here is a calibrated measurement.</p>
    <LibraryClient />
  </section>;
}
