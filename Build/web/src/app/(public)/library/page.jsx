export default function Library() {
  return <section className="reading">
    <h1>Demo library</h1>
    <p className="lede">No demos are published yet.</p>
    <p>Guest browsing needs no account. Approved scene playback will be connected here in a later run.</p>
    <div className="mount-note" data-slot="viewer" data-state="unavailable">
      <h2>Viewer not connected</h2>
      <p>No scene has been loaded. This is not a reconstruction or simulation result.</p>
    </div>
  </section>;
}
