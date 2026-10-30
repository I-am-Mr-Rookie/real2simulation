import LibraryClient from './LibraryClient.jsx';

const CSS = `.library-grid{list-style:none;padding:0;display:grid;gap:1rem;grid-template-columns:repeat(auto-fill,minmax(min(100%,18rem),1fr))}
.library-card{border:1px solid currentColor;border-radius:.75rem;padding:1rem;min-width:0;overflow-wrap:anywhere}
.library-card[data-availability=unavailable]{opacity:.8}.library-card h2{font-size:1.05rem;margin:.5rem 0}
.library-card ul{font-size:.85rem;padding-left:1.1rem}.library-card button{min-height:44px;padding:0 1rem}
.library-card [data-slot=viewer] svg{width:100%;height:auto}`;

export default function Library() {
  return <section className="reading">
    <p className="eyebrow">Public · no account needed</p>
    <h1>Demo library</h1>
    <p className="lede">Simulated trajectories and honest placeholders. Nothing here is a calibrated measurement.</p>
    <style>{CSS}</style>
    <LibraryClient />
  </section>;
}
