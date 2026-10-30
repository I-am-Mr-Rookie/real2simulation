# S18k-orch123

Objective: expose bounded, accepted-source simulated traces through the guest
API/loader; verify declared real PLY bytes or keep unavailable; preserve Mystery-g.

Owns: Build/library/; test-data/library-artifacts/; tests/library/; evidence/S18/;
Run-System/Runs/S18k-orch123/. No canonical controls, viewer/app or deployments.

Issue 2026-10-30T09:53:01+00:00; cutoff 10:18:01Z; deadline 10:23:01Z
(16:23:01 Dhaka). CODEX-2 / gpt-6.1-sol medium; OpenCodex-managed; not polled.
Project 91e441f8-e40c-4ec4-bea2-de7fa1582d97 supplied by delegation.
Worktree run/S18k-orch123 from main 4664258; controller owns integration.

Reach: offline generation/custody validator, stored artifacts/index, guest
projection/endpoints, framework-free loader, library tests, handoff contract.
Reuse accepted simulator functions, existing hash/store/path/pointer helpers and
loader transport validation. No dependency or general rendering framework.
Risks: publishing challenge answers; guessing absent initial conditions; treating
descriptor declarations as PLY bytes; breaking metadata consumers. Fail closed.

Checks: library unittest discovery, deterministic generation, hash/size/sample
negative cases, HTTP artifact/answer boundary, loader playable/no-fetch behavior,
git diff --check and worker_timebox.py check. No GPU/API/model/network jobs.
