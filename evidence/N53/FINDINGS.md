# N53 room latency

## Result and scope

Two public RM02 backend jobs on the actual DEV API host completed below five minutes: **271.561 s cold**, **254.655 s with a reused A10G container**. N47's recorded backend job was 667 s, from second-resolution status timestamps. These are backend times, not browser upload times.

The owner explicitly extended this run to 15:00 Dhaka, authorized a separate worker ceiling of $5 per job, clarified that the $10/day pool is for all visitors collectively, and approved one additional warm test after the original single paid test. No visitor quota configuration was changed.

No deployment: nine source files were copied to isolated /tmp/n53-orch298 and /tmp/n53-orch298-warm overlays and executed in separate processes, using the DEV CPU, actual Modal functions, hosted SAM, existing approved public N47 RM02 upload, and shared DEV GPU queue. Deployed source hashes were unchanged before/after each run. Critical overlay sources match this branch after CRLF normalization. No private video or owner-room output was accessed.

## Measured stages

| Stage | N47 recorded DEV | New cold DEV | New reused-container DEV |
|---|---:|---:|---:|
| Browser upload | not recorded | not run | not run |
| Frame sampling | not isolated | 0.967 s | 0.987 s |
| L4 capacity attempt | 240.250 s | 90.376 s | 90.341 s |
| A10G round trip | 28.934 s | 35.040 s | 26.462 s |
| MapAnything inference | 1.928 s | 3.261 s | 2.918 s |
| Hosted SAM call span | 59.030 s, 72 images | 49.675 s, 176 images | 41.357 s, 176 images |
| Detection incl. PNG preparation and mask validation | not isolated | 50.198 s | 41.904 s |
| Mask decode/validation thread-duration sum | not isolated | 7.597 s | 7.762 s |
| Analysis and furniture lift | not isolated | 3.959 s | 3.967 s |
| Remaining shell geometry | not isolated | 0.202 s | 0.200 s |
| SF3D attempts | 305.260 + 13.374 + 2.075 s | one 90.235 s timeout | one 90.239 s timeout |
| All JSON status/result write durations, summed | not isolated | 0.003701 s | 0.003375 s |
| Whole backend job | 667 s | 271.561 s | 254.655 s |

SAM spans and mask timings overlap and must not be added. Thread-duration sums are not standalone stage wall times. Raw monotonic events and settlements are in events.json, warm-events.json, ledger.json and warm-ledger.json; stage totals are in live.json, warm.json and summary.json. N47 used eight frames and the newer jobs use sixteen, so this is not a controlled same-model-output A/B comparison. Wall times are individual measurements, subject to provider/network/CPU variation.

Cold A10G: 7.078 s call-to-function start plus 20.598 s model load; 3.261 s inference. The second call reused the container: its container-start timestamp precedes the call by 512.655 s, and function-start delay is 1.187 s. It still reloads model weights in 18.278 s, so this is **warm container, not cached-model inference**. Negative container_boot_s in that existing log schema denotes a pre-existing container, not a negative-duration operation.

## Changes and controlled CPU comparisons

- Keep the existing four-thread hosted SAM pool. Its calls were already concurrent; no new pool or dependency was needed.
- Fuse binary mask canonical validation into range decoding. Encoder and decoder have the same low/range states; collect the encoder's normalization/finalization bytes while decoding and compare with the already strictly unpacked payload. This removes the second full adaptive encode pass, not validation. Lossless behavior is preserved.
- Against the unchanged codec in base b635d89e: **426 cached public mask records decode identically**; serial strict validation 58.961 s versus 36.721 s. Random binary masks, count rescaling, malformed/truncated/noncanonical payloads are also tested.
- Actual production shell-file path, same cached RM02 replies: **34.151 -> 23.129 s**, with byte-identical scene.json, 23 objects. Detection 25.688 -> 14.578 s; lift 7.921 -> 7.984 s; JSON scene/room saves approximately 0.007 -> 0.005 s. Different from the fresh paid reconstructions above.
- Extract frames in two bounded workers, preserving timestamp order and exact PNG bytes: local RM02 sampling **18.575 -> 11.337 s**, all 16 hashes identical. Pending decodes are cancelled on error.
- Persist room and shell stage timings for subsequent jobs.

## Spend-code review, required before controller merge/deploy

1. live_room.py: L4 get budget 240 -> 90 s; cancel before the single narrow A10G retry. Existing GPU order, fallback budget, rates, reservation estimates, idle windows, queue leases and daily-cap implementation remain unchanged. Unconfirmed cancellation prevents retry and retains the full reservation estimate.
2. sf3d.py: client get budget 600 -> 90 s, with cancellation for client/function timeout; keep original worst-case A10G reservation. Failed cancellation retains that full estimate. Remote function/startup limits and deployment resources are unchanged.
3. room_shell.py: after an SF3D budget timeout, do not launch more shape calls for that shell. Keep explicitly labelled box fallbacks. Do not parallelize the single-container SF3D pool, which would queue work and make cancellation unsafe.
4. paid_probe.py: owner-only $5 admission guard, separate per-job worker ledger, every call reserved/settled; visitor cap policy is not modified. The replay harness now preserves the shared queue's default ledger path; the two probes reaped zero unrelated jobs. No deployment or credential change.

Paid cold: 176 sam-3.1 images, two MapAnything GPU attempts, one SF3D attempt; **$1.12006113 estimated**. Paid second job, explicitly approved: same units, **$1.11689456 estimated**. **Total $2.23695569**, 358 settled rows, zero unsettled. Each ledger row includes UTC, model, units, reservation and settlement. Estimates include conservative GPU idle windows; provider invoices were not reconciled. Do not mix worker charges into the visitor quota.

## SF3D diagnosis and remaining quality finding

Existing N47 Modal logs show CUDA banner at 04:36:43Z, Transformers cache initialization at 04:40:37Z, timm import at 04:41:36Z, then a 300 s function timeout at 04:41:46Z. The next calls complete in about 13.4 and 2.1 s. This implicates cold dependency/model initialization rather than proving the first object's mesh is intrinsically slow; the exact blocking import was not traced.

Both new jobs hit the 90 s SF3D client budget and kept boxes, so the latency win has a real mesh-quality tradeoff. Cold mesh generation remains unresolved, not disguised as successful shape generation.

Extra SIMULATED physics QA: all five actual table colliders support a ball in isolation, but **4/5 pass in the complete scene** in both jobs. In the cold scene room-object-5 expects rest y=0.11085 and reaches y=0.356081; isolated it reaches y=0.110781. This is a full-scene proxy-interference/geometry finding, not a table falling-through result. No renderer/physics or geometry workaround was introduced for this latency task. Full traces/results: physics-cold.json and physics-warm.json. Geometry remains MODEL-ESTIMATED and scale unverified.

## Checks and reproduction

Production-pinned Python 3.12: uv run --python 3.12 --with-requirements Build/api/health/requirements.txt --with modal==1.6.3 --with pytest --with httpx python -m pytest tests/reconstruction tests/gpu tests/measurement/test_hosted_sam.py tests/guardrails/test_daily_cap.py -q: **117 passed**. Existing Pillow/AnyIO deprecation warnings remain.

Offline scripts: sample.py PUBLIC_RM02 OUTPUT; verify_codec.py N52_SAM_CACHE OUTPUT; replay.py N49_JOB N52_SAM_CACHE OUTPUT; shell_files.py N49_JOB N52_SAM_CACHE OUTPUT [--strict-codec]; summarize_n47.py N47_EVIDENCE OUTPUT. All are under evidence/N53 and use no new paid call. Physics: node evidence/N53/physics.mjs evidence/N53/live-scene.json OUTPUT, or warm-scene.json.

No web source changed, so no Node suite/Next build was required. Controller must cross-vendor review spend changes, merge and deploy DEV; browser/BFF upload-to-saved-lab behavior on the deployed service is still unverified. No production release, physical calibration or owner-room QA is claimed.
