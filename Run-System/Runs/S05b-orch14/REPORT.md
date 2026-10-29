# S05b-orch14 — DONE (first real MapAnything RM02 output on Modal A10G; measured cost; all own apps stopped)

Lane/model: anthropic/claude-opus-5-5 high (OpenCodex-managed; not polled). Issue 11:21:47Z, deadline 11:51:47Z; work stop ~11:44Z.
Branch run/S05b-orch14 from main 3819cc4, worktree `.worktrees/S05b-orch14`. Canonical controls untouched.

## Result
| Attempt | App | Outcome |
|---|---|---|
| #1 A10G 11:26:48Z | ap-n1kdxs0OPi7hgSfJbAsuDX | ADMITTED (~20s). Remote ran fully: NVIDIA A10 23028 MiB, inference 1.13s, function 158.7s. Client DeserializationError: receipt `torch.__version__` is a TorchVersion (torch type), local client has no torch -> npz lost locally. Stopped 11:29:50Z, containers []. Cost **$0.0582** |
| #2 A10G 11:34:02Z (controller-approved rerun) | ap-TqJhwZi4v9ucIKg16ZKh1E | **OK rc=0**, result received+persisted. Stopped 11:37:11Z, containers [] (own). Cost **$0.0572** |

Attempt #2 measured: GPU "NVIDIA A10, 23028 MiB, driver 610.57.04", 1 GPU; MapAnything facebook/map-anything-apache @00f9c24
(code 3d10cf7); 4 RM02 frames (SHA match); inference_s 1.198; function_elapsed_s 161.7 (pip+weights dominate); peak alloc
7.72 GB / reserved 7.93 GB; npz 25,929,797 B sha256 4ce3c82c...f466b (identical to #1 remote hash -> deterministic).
Per view: pts3d/pts3d_cam/ray_directions/img [1,294,518,3], depth/mask [1,294,518,1], conf [1,294,518], intrinsics 3x3,
camera_poses 4x4, cam_trans/quats, metric_scaling_factor; all finite. Receipt: `evidence/S05/S05b/recovery8/attempt-6719a7021d70479294ffad678cede3de/gpu-result.json`;
npz in gitignored `.../local/RM02-mapanything.npz` (not committed). physical_scale/capture_timebase unverified; **Gate R NOT RUN**.

## Cost (measured, read-only)
`modal billing report --start 2026-10-29 --end 2026-10-30 --resolution h --csv` (evidence/S05/S05b/orch14/billing-report-cli.csv):
#1 $0.05817517, #2 $0.05715299 => **~$0.057-0.058 per A10G RM02 4-frame probe (~3 min wall, ~160s function)**; orch13 CPU job $0.00468;
orch13 L4 attempts not billed. Billing UI (in-app browser): 11:35Z usage $0.20/credits $129.80; ~11:39Z $0.28/$129.73; $0 charges; limit $155.
Ledger: evidence/S05/S05b/orch14/job-ledger.json — $0.95 reserve (total retained $4.75/$30), actual $0.115, release $0.83 suggested.
Sizing hint: per-job cost is dominated by ~155s pip/weights setup, not inference (1.2s/4 frames); batching scenes per container or a
prebuilt image would cut cost/scene sharply.

## Code changes (Owns: Build/reconstruction/spike/)
- modal_rm02.py: gpu L4->A10G, function timeout 480->600; receipt `"torch": str(torch.__version__)` (root-cause fix for #1).
- rm02_deadline.py: TOTAL 900->1020, EXECUTION 480->600 (admission 210s). Actual use: admission ~20s, function ~160s.
- test_modal_rm02.py: pins A10G/600, asserts str(torch.__version__), planned-compute at A10G rate $0.375.

## Fresh checks
- test_modal_rm02 + test_rm02_result: 13/13 OK (after fix, before rerun).
- Full spike suite (uv ephemeral Py3.11 + modal 1.6.3): 62/66; 4 failures all in test_rm02_watchdog (untouched). Same failure
  reproduced on UNMODIFIED orch13/main code with this interpreter ("Independent stop unconfirmed") => environment/interpreter
  dependent, not caused by this diff; orch13 recorded 66/66 under its interpreter. Not re-investigated (cutoff). evidence/S05/S05b/orch14/spike-tests.txt.
- Live: own apps both "stopped", tasks 0; own containers 0 (final-verify.txt). Only live container belongs to other worker s07b-orch14.
- Pre-launch: apps [] relevant / containers [] (pre-verify.txt, pre-attempt2.txt).

## Limits / honest notes
- Pre-launch billing UI did not load (skeleton/CDP timeout); headroom relied on orch13 11:09Z read ($129.99, $0 charges) + post reads.
- Watchdog `stop_returncode` 1 both attempts (app already completed); independent stop confirmed by exact-ID listing.
- Output is model geometry, not calibrated scale; no S05c/Gate R/physical claim.

## Ponytail full
Reused runner/watchdog/frames/requirements unchanged; diff = GPU string, two constants, one str() fix, test pins. Skipped: GPU
fallback list, image prebuild/volume caching, scene-contract conversion (S05c), watchdog test env investigation. Risk: per-run
~155s cold setup; watchdog tests interpreter-sensitive.

## Communication
One nonterminal blocker message (rerun request) + controller approval; one completion line.

