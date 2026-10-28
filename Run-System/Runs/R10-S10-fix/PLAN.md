# R10-S10-fix

- Lane/model requested: CODEX-1, existing managed Sol/high; project `91e441f8-e40c-4ec4-bea2-de7fa1582d97`. Parent supplies project context; no new chat/route created here.
- Base: `0db90bae35d9dd1c9c23a032644e0311fb843975`; branch `run/R10-S10-fix`; existing `swarm10-s10review` worktree. Preserve historical audit reports unchanged.
- Objective: reject invalid derived floor translations and initially penetrating trajectories; retain true initial touch, common output, deterministic replay and the unchanged 0.005 acceptance threshold. Verify finite JS values cannot silently become infinite Rapier inputs.
- Owns: `Build/simulator/contacts.mjs`, `tests/simulator/contacts.test.mjs`, `evidence/S10/contact-hardening/`, `Run-System/Runs/R10-S10-fix/` only.
- Issued: 2026-10-28T20:03:18.139Z; deadline: 2026-10-28T20:33:18.139Z; implementation cutoff: 2026-10-28T20:28:18.139Z.
- Controller correction: Dhaka deadline is **2026-10-29T02:33:18.139+06:00**, not the erroneous 07:03 handout value. UTC clock unchanged, no reset/extension.
- Acceptance: regressions demonstrate both audit defects before fixing; float32 boundary repro/checks; fresh contacts, simulator and contact integration; actual Python acceptance/regression with actual replay; scoped commit, no merge/rebase.
- Ponytail full: inspect all direct callers and tests; fix once at the shared contact boundary; reuse installed Rapier and existing acceptance/replay, no schema/dependency/response redesign.
- Restrictions: simulation-only owner exception; no physical Gate P/M, real scene, contact response, paid compute, secrets, service/UI/config/control changes, deployment or publication. No Claude work in this run; parent owns targeted native Claude re-review.
- Costs/tokens unknown; OpenCodex-managed; not polled.
