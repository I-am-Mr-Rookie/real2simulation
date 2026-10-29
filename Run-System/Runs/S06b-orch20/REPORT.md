# S06b-orch20 — DONE (MapAnything runtime packaged on S06a image; A10G smoke + licence audit; $0.0118)

Lane CODEX-1; model anthropic/claude-opus-5-5 high (OpenCodex-managed; not polled). Issue 12:04:00Z, deadline 12:34:00Z;
worker start 12:05:15Z, work stop see TIMEBOX.json. Worktree .worktrees/S06b-orch20, branch run/S06b-orch20 from main 4f193cf.
Canonical controls and Build/reconstruction/spike/ (S05c) untouched; no merge (controller accepts).

## Delivered (Owns only)
- Build/gpu/runtime.py — RUNTIME_IMAGE = S06a IMAGE + source mount (no rebuild); load_model() (one CUDA device,
  apache @ 00f9c24, local_files_only); smoke() A10G/cpu2/16GiB/timeout300/startup240/retries0/max1/single-use:
  nvidia-smi, model load, 2 SYNTHETIC noise frames forward, importlib.metadata licence dump of every installed dist.
- Build/gpu/licence_audit.py — classifies dump: permissive / vendor_eula (NVIDIA) / copyleft_review / unknown / denied;
  checks every lock pin installed at exact version; REVIEWED dict (mapanything Apache per evidence/S05/LICENSE_REVIEW.md,
  plyfile GPL-3.0 private-runtime-only); exit 0 iff no drift, no denied, nothing unreviewed.
- Build/gpu/test_licence_audit.py — 4 tests (classes, pins/drift/denial, duplicates+unreviewed, real lock parses).
- infra/modal/README.md — S06b runtime + licence sections, measured results, unverified items.
- evidence/S06/S06b/ — smoke-remote.json (incl. licences), licence-audit.json, run-log.txt, tests.txt, dry-run-offline.json,
  pre/post-verify.txt, billing-pre-month.csv, billing-pre/post-today-hourly.csv, job-ledger.json.

## Modal job (one A10G, standing auth, reserve $0.50, retries 0)
Pre (12:14Z): month-to-date $0.557 of $30, no non-stopped apps, containers []. Ledger reserved 12:15:20Z.
App ap-vaD1cV50rPyWL1yzQggQ6g 12:15:43Z -> stopped 12:16:27Z, rc 0; run-log shows no image build (S06a layers reused).
Post 12:16:54Z: own app stopped, tasks 0, no non-stopped apps, containers []. Cost **$0.01175778** (hourly CSV ~12:20Z; may lag).
Measured: A10G 23028 MiB, driver 610.57.04, torch 2.8.0+cu128, CUDA 12.8; model load 23.0 s, forward 1.6 s, function 24.7 s,
peak alloc 7.78 GB, pts3d [1,392,518,3] finite 1.0; client round trip 36.3 s.
Cold-setup saving: S05b recovery8 in-function-pip function 161.7 s vs 24.7 s => ~137 s per cold job (one sample each).

## Licence/dependency audit (licence-audit.json, rc 0)
116 dists (111 unique); all 96 lock pins present at locked version. 100 permissive; 14 NVIDIA CUDA wheels proprietary EULA
(private runtime only, never redistribute); plyfile GPL-3.0 and mapanything (empty metadata -> Apache) reviewed; 0 denied.
Duplicates attrs/certifi/idna/protobuf/typing-extensions each also at an older version + 15 extras (aiohttp, grpclib, cbor2, ...):
Modal-injected container client deps beside the lock.

## Fresh checks
- python -m unittest discover -s Build/gpu: 8/8 OK (local py3.14). python Build/gpu/image_spec.py: rc 0.
- modal run Build/gpu/runtime.py: rc 0 (uv py3.11, modal 1.6.3, .env MODAL_TOKEN_* by key name; values never printed).
- python Build/gpu/licence_audit.py evidence/S06/S06b/smoke-remote.json: first rc 1 (5 "drift" = duplicates, 2 unreviewed) -> fixed
  to set-based version check + recorded reviews -> rc 0.

## Limits / not verified
- Synthetic noise input only: no scene, quality, scale, Gate R or physical evidence. Real scenes = S05c/S06d-f.
- Which duplicate version wins on sys.path not checked (would need a second job; contract allowed one smoke).
- Model load 23 s still dominates; weights load from image layer, not memory snapshot. Modal image cache retention unchecked.
- plyfile GPL-3.0 must be re-reviewed before any image/bundle distribution. Billing CSV may lag; recheck before release of $0.488.

## Ponytail full
Reused: S06a IMAGE unchanged (no new layers, so no rebuild), S05b probe's infer() args/nvidia-smi pattern, importlib.metadata
instead of pip-licenses/new dependency, existing uv+modal 1.6.3 route and billing CLI. Smallest complete: 3 new files (~230
lines) + README section. Skipped: memory snapshots/Volume, second warm run, wiring into spike/ (S05c-owned), pip-licenses install,
licence text fetching. Risk: Modal-injected duplicate deps could shadow locked versions at import time.

## Communication
Silent; one completion line to controller.

