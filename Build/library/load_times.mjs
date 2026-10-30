// S18i: time guest manifest + artifact fetch/validate through the real loader over local HTTP.
// Usage: node load_times.mjs <base-url> <reps>  -> JSON on stdout.
import { loadLibraryEntry } from './loader.mjs';

const [base, repsArg] = process.argv.slice(2);
const reps = Number(repsArg);
const http = (href, init) => fetch(base + href, init);
const now = () => performance.now();
const manifest = async () => {
  const response = await http('/api/library/manifest', { redirect: 'error', credentials: 'omit' });
  if (!response.ok) throw new Error(`manifest HTTP ${response.status}`);
  return response.json();
};

const t0 = now();
const first = await manifest(); // first request after server start = cold server path
const coldManifestMs = now() - t0;
const results = {};
for (let rep = 0; rep < reps; rep++) {
  // One manifest GET per rep (each costs a full server revalidation); open = that GET + entry load.
  const start = now();
  const current = await manifest();
  const manifestMs = now() - start;
  for (const { id } of first.demos) {
    const entry = current.demos.find((demo) => demo.id === id);
    const mid = now();
    const loaded = await loadLibraryEntry(entry, { fetch: http });
    const end = now();
    if (loaded.id !== id || loaded.availability !== entry.availability) throw new Error(`${id} loaded inconsistently`);
    results[id] ??= { availability: loaded.availability, canMount: loaded.canMount, open_ms: [], entry_ms: [], manifest_ms: [] };
    results[id].open_ms.push(manifestMs + end - mid);
    results[id].entry_ms.push(end - mid);
    results[id].manifest_ms.push(manifestMs);
  }
}
process.stdout.write(JSON.stringify({ cold_manifest_ms: coldManifestMs, entries: results }));
