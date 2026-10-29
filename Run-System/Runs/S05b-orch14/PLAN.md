# S05b-orch14 PLAN

Issued 2026-10-29T11:21:47Z; deadline 11:51:47Z (Dhaka 17:51:47); minute-25 cutoff 11:46:47Z.
Model anthropic/claude-opus-5-5 high; OpenCodex-managed, not polled. Branch run/S05b-orch14 from main 3819cc4.

Objective: ONE MapAnything (facebook/map-anything-apache @00f9c24 only) RM02 GPU probe on Modal **A10G**
(controller decision after 3 L4 admission failures), existing rm02_watchdog -> modal_rm02 guarded_probe.
Bounds: TOTAL 1020s (watchdog reserve 60, startup 90, execution 600, cleanup 60 -> admission 210s);
function timeout 600s. Launch ~11:27Z so stop+verify lands before 11:46Z.

Owns: Build/reconstruction/spike/, contracts/scene/, test-data/synthetic/scene/, evidence/S05/, Run-System/Runs/S05b-orch14/.
Authority: evidence/owner/S05/GPU-AUTHORIZATION.md (standing). Reserve $0.95 (<=$1) in evidence/S05/S05b/orch14/job-ledger.json.
Safeguards: apps/containers before & after, exact-ID stop, billing read-only (in-app browser), no second attempt
without controller message, no AWS/NC/SAM3D/footage/upload/billing change. No Gate R claim.
