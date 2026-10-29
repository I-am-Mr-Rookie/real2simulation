# S05b-orch13 PLAN

Issued 2026-10-29T10:56:00Z; deadline 11:26:00Z (Dhaka 17:26); minute-25 cutoff 11:21Z.
Model anthropic/claude-opus-5-5 high; OpenCodex-managed, not polled. Branch run/S05b-orch13, main 7303bc5.

Objective: first actual MapAnything (facebook/map-anything-apache @00f9c24, Apache-2.0) RM02 probe on Modal L4,
using existing spike code unchanged: cpu_import_probe.py (fresh CPU import preflight) then rm02_watchdog.py
(supervise -> modal_rm02.py guarded_probe, 1200s total, exact-ID stop + independent app/container verification).

Owns: Build/reconstruction/spike/, contracts/scene/, test-data/synthetic/scene/, evidence/S05/, Run-System/Runs/S05b-orch13/.
Authority: evidence/owner/S05/GPU-AUTHORIZATION.md (standing; no new consent question).
Safeguards: fresh billing view (credits/charges/limit), apps+containers [] before, <=$1 all-in reserve in
evidence/S05/S05b/orch13/job-ledger.json, retries 0, one CPU then at most one GPU job, launch GPU only if the
full 1200s bound ends before 11:26Z, independent stop verification after. No code/resource/dependency changes planned.
Checks: (1) CPU imports PASS receipt; (2) watchdog.json confirms exact-app stopped + containers []; (3) gpu-result
receipt with GPU name/VRAM/runtime/output hash, or honest failure facts.
