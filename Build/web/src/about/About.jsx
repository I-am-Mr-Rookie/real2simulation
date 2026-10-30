// S21e About panel: renders generated about.json only (Build/benchmark/about.py); no numbers typed here.
import about from "./about.json";

const fmt = (r) => (r.value === null ? "UNAVAILABLE" : `${r.value} ${r.unit}`);

export default function About() {
  const g = about.gates;
  return (
    <section aria-labelledby="about-h">
      <h2 id="about-h">Benchmark: what is measured, simulated or unavailable</h2>
      <ul>
        <li>Gate M: {g.gate_m}</li>
        <li>Gate RS: {g.gate_rs}</li>
        <li>Gate A: {g.gate_a} ({g.gate_a_label})</li>
      </ul>
      {Object.entries(about.sections).map(([name, s]) => (
        <table key={name}>
          <caption>{name}: {JSON.stringify(s.summary)}</caption>
          <thead><tr><th scope="col">id</th><th scope="col">class</th><th scope="col">value</th><th scope="col">reason / note</th></tr></thead>
          <tbody>
            {s.rows.map((r) => (
              <tr key={r.id}><td>{r.id}</td><td>{r.class}</td><td>{fmt(r)}</td><td>{r.reason || r.note || ""}</td></tr>
            ))}
          </tbody>
        </table>
      ))}
      <p>Full method and limits: BENCHMARK.md. Values are copied from sha256-pinned evidence ({Object.keys(about.sources).join(", ")}).</p>
    </section>
  );
}
