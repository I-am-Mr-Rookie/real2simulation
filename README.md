# Real2Simulation

Turn a short, licensed physics video into a reconstructed scene, a fitted motion model and a
simulated prediction, then compare the prediction with held-out frames of the same clip.
Built solo by Koushik Sadhak Jeet (indie developer track) for the Meta Global AI Developer Hackathon.

- **Judging URL:** PENDING S23 (not yet deployed or approved).
- **Frozen judging revision:** PENDING S23.
- **Demo video:** PENDING.
- Railway **dev** services (development only, not the judging build): [real2simulation.up.railway.app](https://real2simulation.up.railway.app)
  (also [real2simulation.rookiecoders.tech](https://real2simulation.rookiecoders.tech)),
  api-dev-6091.up.railway.app, worker-dev-984d.up.railway.app.

## Results (honest summary)

All numbers live in [BENCHMARK.md](BENCHMARK.md); none are written here by hand. Every number there is a
JSON pointer into sha256-pinned evidence, checked by `python Build/benchmark/manifest.py check`.

| Class | What it covers |
|---|---|
| **Measured** | Real runs on licensed clips: image-space fit precision, floor-normal consistency, ST03 prefix-to-suffix prediction error (diagnostic only), GPU timings, Modal billed cost, Meta API tokens/latency. |
| **Simulated** | Fitter/lab synthetic cases and the spend-cap regression (zero provider calls, not spend). Never mixed into measured rows. |
| **UNAVAILABLE** | Any metre, m/s^2 or gravity error vs truth (no calibrated scale or capture clock); metric scene scale; bounce and pendulum prediction error; Gate RS median; Meta dollar cost. |

Gates, as recorded in BENCHMARK.md:

- **Gate M: NOT_MET_INPUT_READINESS** — no calibrated scale or capture clock, so no metric claim.
- **Gate RS: NOT_MET** — no category reaches 80% scored coverage.
- **Gate A: MET_AMENDED_Q16** — labelled "scale unverified, not setup-validated"; never plain MET.

Physical or calibrated accuracy is **not claimed** anywhere. One run per measurement; no variance claim.

## Architecture

| Part | Where | Role |
|---|---|---|
| Web app | [Build/web](Build/web/) (Next.js 16, React 19, three.js, Clerk) | Viewer, virtual lab, library, private workspace, About page ([About.jsx](Build/web/src/about/About.jsx) renders generated [about.json](Build/web/src/about/about.json)). Hosted on Railway dev. |
| API | [Build/api/health](Build/api/health/) (FastAPI) | Health/readiness probes over Postgres, Redis and S3-compatible storage; dev-only I/O guard. |
| Worker | [Build/worker/health](Build/worker/health/) (FastAPI) | Worker health process; readiness stays 503 without a job heartbeat. |
| GPU jobs | [Build/gpu](Build/gpu/), [Build/reconstruction](Build/reconstruction/), [Build/pipeline](Build/pipeline/) | Modal GPU jobs: SAM 3.1 segmentation/tracking and scene reconstruction, with per-job cost logs and ledgers. |
| Fitter / simulator / prediction | [Build/fitter](Build/fitter/), [Build/simulator](Build/simulator/) (Rapier), [Build/real2sim](Build/real2sim/), [Build/lab](Build/lab/) | Fit motion parameters, simulate, predict the held-out suffix. Numbers come only from fitter/simulator output. |
| Guardrails | [Build/guardrails](Build/guardrails/) | Spend admission, reservations, settlement and failover; routine Meta stop and GPU caps (see [API_BUDGET.md](API_BUDGET.md)). |
| Library | [Build/library](Build/library/) | Static snapshot of licensed clips and simulated examples with credits ([credits.py](Build/library/credits.py)). |
| Agent | [Build/agent](Build/agent/), [Build/sidebar-tools](Build/sidebar-tools/) | Muse-based interview/spec agent with traced tool numbers; sidebar library search. |
| Benchmark | [Build/benchmark](Build/benchmark/) | Manifest, leakage check, About data generator. |

Muse appears only as the Meta model family used by the agent; it is not a separate service.

## Run locally

Prerequisites: Python 3.11+ and Node.js >= 20.9. Copy [.env.example](.env.example) to `.env` and fill your
own keys (never commit `.env`). From the repository root:

```powershell
# Benchmark evidence check and tests (no network, no keys)
python Build/benchmark/manifest.py check
python -m unittest Build/benchmark/test_manifest.py Build/benchmark/test_about.py

# API health service
python -m pip install -r Build/api/health/requirements-test.txt
python -m uvicorn Build.api.health.app:app --host 127.0.0.1 --port 8001
python -m unittest Build.api.health.test_health Build.api.health.test_dependencies -v

# Worker health service
python -m pip install -r Build/worker/health/requirements.txt
python -m uvicorn Build.worker.health.app:app --host 127.0.0.1 --port 8002

# Web app
cd Build/web
npm install
npm run dev
```

Railway dev setup: [infra/railway/dev/README.md](infra/railway/dev/README.md). GPU jobs need your own Modal
account and stay within the guardrail caps.

## Meta model usage (exact evidence)

| Model | Route | Use | Evidence |
|---|---|---|---|
| `muse-wonder-1.0` | Meta Model API | Agent interview/spec calls (S14g); HTTP 200, tokens measured, billed USD null | [Build/agent/muse.py](Build/agent/muse.py), [S14g-fix3-ledger.jsonl](evidence/S14/S14g-fix3-ledger.jsonl) |
| `meta-models/muse-spark-open-1026` (Muse Open) | Baseten | **One** sidebar call (S16e): HTTP 200, 1,176 tokens; dollar cost UNKNOWN | [S16e-orch108-live.json](evidence/S16/S16e-orch108-live.json), [S16h-CHECKPOINT.md](evidence/S16/S16h-CHECKPOINT.md) |
| `facebook/sam3.1` | Modal GPU | Segmentation/tracking on licensed scenes | [raw-result.json](evidence/S13/S13h/live/segment/raw-result.json), [SAM licence](evidence/S05/upstream/sam_license.txt) |

- **Open-weight bonus: NOT claimed.** The sidebar Meta Spark fallback is an explicit-config refusal, not a
  working route (S16h).
- Meta dollar cost is UNAVAILABLE (tokens measured; pricing unverified).

## Event work only

All code, evidence and generated assets in this repository were created during the event window
(Oct 27 – Nov 4, 2026). No prior project code, private data or personal files are included. The demo shows only
event work.

## Licences and attribution

- Footage and third-party libraries: [ATTRIBUTION.md](ATTRIBUTION.md); clip licence ledger: [clips.csv](clips.csv).
- Only NASA public domain, Wikimedia Commons (CC BY / CC BY-SA / PD / CC0), Pexels and Pixabay clips are used.
- Project source licence: [MIT](LICENSE) (owner choice, Q18). It covers this project's own code and docs only. Third-party footage ([clips.csv](clips.csv), [ATTRIBUTION.md](ATTRIBUTION.md)), model weights/APIs (Meta Muse, SAM 3.1, etc.) and dependencies keep their own licences/terms.

## Development controls

Run system and owner checklists: [START.md](START.md), [RUNS.md](RUNS.md), [QUEUE.md](QUEUE.md),
[DECISIONS_LOG.md](DECISIONS_LOG.md), [JUDGE_RUBRIC.md](JUDGE_RUBRIC.md), [GitHub Backup.md](GitHub%20Backup.md).

## Credits

Powered by Stability AI: room objects use Stable Fast 3D under the [Stability AI Community License](LICENSES/Stability-AI-Community-License.md) ([NOTICE](NOTICE)). Its outputs are not used to train models.
