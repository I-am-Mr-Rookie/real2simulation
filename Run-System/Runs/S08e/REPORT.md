# S08e — DONE

## Objective, routing and lifecycle

- Add validated horizontal-projectile template and deterministic analytic answer.
- Requested CODEX-1 GPT-6.1 Sol / medium; actual delegated Codex session, exact
  runtime model/effort unavailable. No model/provider/credential/policy changes.
- UTC start 2026-10-27T18:19:17Z; main verification ended 18:23:50Z;
  receipt 18:24 UTC (under 30m). Prior reports read: S09a, S02b, S08d.
- Initial main9abe3e4; concurrent orchestrator commit545159b preserved; claim8876980.
  Product commit e0a443d435112bf0951c561a51de590bc04b7a4e, run/S08e,
  .worktrees/S08e; rebase main up to date, fast-forward main successful.
  Clean worktree removed after resolved-path containment check. No remote action.

## Changes

- Build/templates/projectile.py: explicit sourced-input factory, deep-copy snapshot,
  authoritative surface/collider lists and validate_setup at factory/oracle entry.
- Closed-form vacuum +X launch, zero initial vertical speed, uniform -Y gravity:
  ideal impact time/range/position/velocity and explicit time/position/velocity
  samples. Zero horizontal speed, translated origins, exact stop-plane endpoint,
  preserved sample order/duplicates, no automatic sampling or post-impact motion.
- Every number uses units, simulated label, analytic method/evidence and null
  uncertainty; copied input source labels retained. No model-authored numbers.
- Build/templates/README.md and contracts/experiment/README.md document APIs,
  equations, conventions, duration/provenance/uncertainty limits; no schema change.
- tests/spec/test_projectile.py:9 synthetic tests, no product fixture imports.

## Actual checks

| Command / stage | Result |
|---|---|
| python -m unittest discover -s tests/spec -p test_projectile.py -q, RED |9 failures: missing-feature assertion, not import errors |
| Same with -v after implementation |9 PASS, no fixture corrections/safety weakening |
| python -m unittest discover -s tests/spec -p 'test_*.py' -q |56 PASS worktree10.324s, after rebase10.686s, main34.656s |
| python -m unittest discover -s contracts/scene -p 'test_*.py' -q |11 PASS worktree5.234s, after rebase7.961s, main9.313s |
| git diff --cached --check; git diff main...HEAD --check; git diff --check |PASS; normal LF/CRLF warnings only |
| git rebase main; git merge --ff-only run/S08e |PASS; unrelated files preserved |

Exact g=8,u=3,h=1 test checks T=0.5, range1.5, impact velocity[3,-4,0]
and intermediate positions against hand-selected analytic values. Further cases
cover zero-speed free-fall agreement, three gravity magnitudes, energy identity,
strict finite/bounded sample inputs (including huge ints), invalid units/ranges,
timestep rejection, tampered asset hashes, hidden collisions and scene bounds.
Synthetic cases establish code behavior only, never measured physics or Gate P.

## Skills/plugins actually applied

Read Superpowers test-driven-development and verification-before-completion under
C:/Users/HP/.codex/plugins/cache/openai-curated-remote/superpowers/7.0.1/skills/.
Applied RED before implementation, then GREEN + full regressions after rebase
and on main before DONE. Initial RED detects missing feature; real numerical
behavior is exercised by final exact and invariant checks. Read workflow/ponytail
guidance; reused existing free-fall conventions with no unrelated refactor or new
dependency. Codex app get_usage_limits queried before/after. External research,
browser, deployment, GPU and provider tools skipped: offline arithmetic/contract
work needs none. No native-control or service readiness claims.

## Limits, costs, next

S08e acceptance met; S08 parent and Gate P NOT complete. No simulator accuracy,
real footage, UI, contact or launch-angle support established. Input uncertainty
not propagated. Repeated per-entry scene/bundle hashing remains a structural
cost, retained for safety rather than introducing an unreviewed cache.

No external inference/GPU calls ($0), secrets read, personal/archive imports,
uploads, deployment, publication, purchases, terms or submissions. Coding tokens,
task dollar cost and Claude quota unavailable. Shared Codex before/after
used70%5h/50%weekly; reset1793132283; no task attribution/reset/purchase.
Owner questions: none. Next separately authorized run: S08f CODEX-1 Sol medium.
