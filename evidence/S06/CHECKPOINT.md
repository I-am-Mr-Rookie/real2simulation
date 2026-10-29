# S06h — GPU runtime + fallback checkpoint (consolidation only; no new GPU job, $0)

Machine record: [CHECKPOINT.json](CHECKPOINT.json) (regenerate: `python evidence/S06/S06h/checkpoint.py`, asserts billing ≥ ledger, scenes ≤300 s, totals ≤$30).
Billing: one read-only `modal billing report --for "this month" --json --show-resources` at **2026-10-29T15:49:15Z** ([billing-month.json](billing-month.json)) + today hourly ([billing-today-hourly.json](billing-today-hourly.json)). Hourly report lags; latest read wins.

**Scope of evidence:** measured Modal runs on owner-approved licensed public clips (RM02, RM04). NOT Gate R pass, not real-scene metric, physical or calibrated evidence.

## Chosen path

| Layer | Choice | Basis |
|---|---|---|
| Reconstruction | MapAnything `facebook/map-anything-apache` (Apache-2.0) on Modal **A10G** (2 CPU, 16 GiB), `s06d-scene-job` entry point, S06b runtime image (not rebuilt since S06a) | S05a licence, S06b–S06f runs |
| Colliders | **primitive** planes + boxes; SAM 3D Objects **off** | Off by default: needs >=32 GB GPU (A10G 23028 MiB < 32768 MiB); checkpoint/runtime unverified. Access **GRANTED** (evidence/owner/S06/SAM3D-ACCESS.md + SAM3D-ACCESS-granted-20261029.png); S06c gate-default.json access reason predates that receipt |
| Renderer / scene | **Gate R Fallback 2**: frame-textured planes + boxes, scale **UNVERIFIED** (model-metric only) | S05f GATE_R.json: FAIL, scale 0/3, orientation 0/3, GPU 3/3 |
| AWS | adapter exists, refuses without owner gates; never launched | S06g aws-adapter-receipt.json |
| CPU dry-run | image_spec pins valid (96), no GPU needed | S06g image-spec-dryrun.json; Build/gpu 29 tests OK (fresh, [tests.txt](tests.txt)) |

Gate R cross-vendor recheck (R-R, orch28): **PENDING** — not CLEAR. Fallback 2 is the recorded decision, not a pass.

## Per-scene timing (measured, container + client clocks, A10G)

| Clip / task | client round-trip s | container boot s | cold start s | model load s | cold→model-ready s | inference s | function s | peak alloc |
|---|---|---|---|---|---|---|---|---|
| RM02 / S06e | 39.55 | 6.46 | 10.81 | 19.73 | 30.54 | 1.45 | 21.72 | 7.78 GB |
| RM04 / S06f | 43.64 | 7.59 | 11.88 | 18.81 | 30.69 | 1.51 | 20.92 | 7.78 GB |
| RM02 / S06d | — | — | — | — | — | — | 20.96 (elapsed) | 7.78 GB |

RM04 whole command wall 63.3 s (S06f) → meets S06f ≤5 min target incl. cold start. Inference is ~1.5 s; ~30 s is cold start + model load → warm reuse is the only big lever.
Earlier S05 path (pre-S06 image): RM02 161.73 s, RM04+RM05 2-scene job 177.9 s function; RM02 cumulative incl. failed attempt 320.39 s (S05f).

## Cost — estimated vs billed (USD)

| Task | App | GPU | rc | Reservation | Estimated (list rate) | Upper bound | Ledger billed (at run) | Billed now (15:49Z) |
|---|---|---|---|---|---|---|---|---|
| S06a | ap-Gf1f5xsIuhpOIGFiwLE1zr | CPU build | 0 | 0.50 | — | — | 0.01564 | 0.01564 |
| S06b | ap-vaD1cV50rPyWL1yzQggQ6g | A10G smoke | 0 | 0.50 | — | — | 0.01176 | 0.01176 |
| S06d | ap-DwCMDeReYWQYBxl3xvR2IO | A10G RM02 | 0 | 0.30 | — | — | 0.00661 (partial read) | **0.00955** |
| S06e | ap-HT56BJbqGtr7qg1pdadmu0 | A10G RM02 | 1* | 0.30 | 0.01032 | 0.01528 | 0.01135 | 0.01135 |
| S06f | ap-ltdA9yMPSJynaFT34T4Ent | none (preflight refusal) | 1 | — | — | — | 0 | 0 |
| S06f | ap-yeKuf0FjgU0P0H8mB9lOvt | A10G RM04 | 0 | 0.50 | 0.01001 | 0.01678 | 0.00955 | 0.00955 |
| **S06 total** | | | | | | | | **0.05786** |

*S06e rc=1 = local post-processing (jsonschema) failure after the remote GPU function succeeded; bundle completed offline, no second call.
S06d ledger was a lagging partial read: fresh billing is $0.00294 higher (recorded as `ledger_lag_usd`). Fresh `cost_log.py` reconcile on copies ([RM02](RM02-scene-log.reconciled.json), [RM04](RM04-scene-log.reconciled.json)) reproduced the S06e/S06f billed values exactly (stable).
Estimator error per scene: RM02 −$0.00103 (under, missed egress $0.00031 + 2 s), RM04 +$0.00045 (over). Billed GPU-s: 30.0 / 26.0.

**Modal month-to-date billed: $0.59959** of $30 monthly (Oct28 $0.00638, Oct29 $0.59321). By resource: A10G 0.42474, Network Egress 0.07489, CPU 0.05212, Memory 0.04563, L4 0.00222. By app prefix: s07b SAM3.1 tracking $0.35053, s05b $0.12639, s05c $0.06482, S06 (s06a/b/d) $0.05786.
Projection (estimate, not measured): ~$0.01/scene warm-image A10G → $30 budget is not the constraint; cold start is.

## Remaining risks

- Gate R FAIL: no metric scale/orientation on public clips; Fallback 2 scale unverified; R-R recheck pending.
- Billing lags by hours; month total may still rise for today's jobs. Reservations (sum of retained, unreconciled across workers) not re-audited here.
- SAM 3D Objects unexercised (needs ≥32 GB GPU, e.g. L40S/A100/H100; access granted; checkpoint/runtime unverified); AWS g6e path untested by design.
- ~30 s cold start dominates per-scene latency; demo should prewarm or use cached bundles.
- RM05 visual-only (ISS, gravity ineligible).

