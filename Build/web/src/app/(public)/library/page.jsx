import LibraryClient from './LibraryClient.jsx';

const CSS = `.lib-summary{display:flex;flex-wrap:wrap;gap:.5rem;margin:1.25rem 0 0;font-size:.8rem}
.lib-summary span{padding:.25rem .6rem;border:1.5px solid var(--r2s-ink);border-radius:3px;background:var(--r2s-surface);box-shadow:var(--r2s-shadow-sm)}
.lib-section{font-family:var(--r2s-font-sans);font-size:1.15rem;font-weight:600;letter-spacing:-.02em;margin:2rem 0 .9rem}
.lib-grid{list-style:none;padding:0;margin:0;display:grid;gap:1.25rem;grid-template-columns:repeat(auto-fill,minmax(min(100%,19rem),1fr))}
.lib-card{display:flex;flex-direction:column;gap:.7rem;padding:1.15rem 1.2rem;min-width:0;overflow-wrap:anywhere;background:var(--r2s-surface);border:1.5px solid var(--r2s-ink);border-radius:var(--r2s-radius);box-shadow:var(--r2s-shadow);transition:box-shadow .15s ease-out}
.lib-card:focus-within{box-shadow:6px 6px 0 var(--r2s-ink)}
.lib-card[data-open]{grid-column:1/-1}
.lib-card h3{font-size:1.05rem;margin:0}.lib-card p{margin:0}
.lib-tags{display:flex;flex-wrap:wrap;gap:.4rem}.lib-tags .state-tag{margin:0}
.state-tag[data-tone=ok]{color:var(--r2s-ink)}
.lib-meta{font-size:.85rem;line-height:1.45}
.lib-callout{padding:.7rem .85rem;border-left:3px solid var(--r2s-warn);background:var(--r2s-bg);font-size:.92rem}
.lib-callout a{font-weight:600;white-space:nowrap}
.lib-limits{font-size:.85rem}.lib-limits summary{cursor:pointer;font-weight:600;min-height:44px;padding-block:.7rem}
.lib-limits ul{margin:.4rem 0 0;padding-left:1.1rem;color:var(--r2s-muted)}
.lib-card button{align-self:flex-start;min-height:44px;padding:0 1.1rem;margin-top:auto}
.lib-replay{padding:1rem;border:1.5px dashed var(--r2s-ink);border-radius:var(--r2s-radius);background:var(--r2s-bg)}
.lib-stage svg,.lib-stage canvas{display:block;width:100%;height:auto;max-height:70vh}
.lib-unavailable{margin-top:2rem;border-top:1.5px solid var(--r2s-ink)}
.lib-unavailable>summary{cursor:pointer;margin-bottom:0;padding-top:1.2rem;min-height:44px}
.lib-unavailable ul{list-style:none;padding:0;margin:.75rem 0 0}
.lib-unavailable li{display:grid;grid-template-columns:auto 1fr;gap:.2rem .75rem;align-items:baseline;padding:.75rem 0;border-bottom:1px solid #d8cfbd;font-size:.9rem}
.lib-unavailable li .state-tag{margin:0;grid-row:span 2}
.lib-scope{margin-top:2rem;font-size:.8rem}
@media (max-width:420px){.lib-card{padding:1rem;box-shadow:3px 3px 0 var(--r2s-ink)}.lib-unavailable li{grid-template-columns:1fr}.lib-unavailable li .state-tag{grid-row:auto;justify-self:start}}`;

export default function Library() {
  return <section className="reading">
    <p className="eyebrow">Public · no account needed</p>
    <h1>Demo library</h1>
    <p className="lede">Simulated trajectories and honest placeholders. Nothing here is a calibrated measurement.</p>
    <style>{CSS}</style>
    <LibraryClient />
  </section>;
}
