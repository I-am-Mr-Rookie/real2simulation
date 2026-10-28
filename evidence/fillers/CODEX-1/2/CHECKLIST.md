# Finished CODEX-1 coverage map

What this change does: Maps existing owned-module tests and adds independent review observations, not product tests. Prior finding descriptions remain in [review 1](../1/CHECKLIST.md); this document records coverage deltas only.

## Existing coverage

Runtime inventory and in-process executed lines: [results.json](results.json). Counts are test methods, not cases inside subtests; ten generated acceptance methods are included.

| Owned source/contract | Existing tests | Covered behavior inspected | Concrete gap / disposition |
|---|---|---|---|
| `contracts/scene/{scene.schema.json,validate_scene.py}` | `contracts/scene/test_scene.py` (11) | Closed schema, IDs, unknown scale, gravity direction, asset length/hash/missing asset, PLY payload mutation, provenance identity, strict JSON | No mesh/splat render branches exercised; 64-line PLY header rejection also unseen. Add byte-authenticated synthetic mesh/splat contract cases and overlong-header rejection in source lane. Codec correctness/rights authenticity remain outside this validator's promises. |
| `contracts/experiment/experiment.schema.json` | `test_experiment_schema.py` (13) | Four variants, exact versions, closed/required fields, units, provenance, unknown drafts, seed, environment | Structural acceptance is not execution permission; no new schema bug reproduced. |
| `contracts/experiment/validate_experiment.py:validate` | `test_experiment_validation.py` (13) | Finite/huge numbers, duplicate/overflow JSON, units, signed domains, uncertainty, malformed input, CLI | CLI is tested in subprocesses: do not mislabel its untraced lines as uncovered. |
| Same module `validate_setup` | `test_setup_validation.py` (13) | Authoritative scene/bundle, all colliders, clearance, swept apex, timestep, contact rejection, energy/subnormal limits, unchanged rejected inputs | Existing `test_contact_and_tiny_numeric_domains_fail_closed` does not test a positive displacement smaller than coordinate spacing: add P2 endpoint case. |
| `Build/templates/free_fall.py` | `test_free_fall.py` (8) | Copy isolation, rest/upward/downward roots, shortened duration, bad scalar time, bundle/collision, provenance | Missing signed huge-time rejection (P1), container/size guard cases and P2 precision boundary. Existing passing tests do not guard these inputs. |
| `Build/templates/projectile.py` | `test_projectile.py` (9) | Analytic endpoints/scaling, zero-speed relation, translated origin, ordering, invalid times/size including `10**400`, validation/provenance | Positive huge-time coverage already exists; negative huge-time symmetry is additional hardening, not a reproduced defect. |
| `Build/templates/ramp.py` | `test_ramp.py` (12) | Friction/energy/direction, nonaccelerating regime, endpoint/scaling, duration, invalid times including `10**1000`, asset integrity | P3 factory+oracle domain rejection is already tested; not a missing rejection. Preserve a separate setup-versus-capability assertion if integration UI is later added. |
| `Build/templates/pendulum.py` | `test_pendulum.py` (11) | Small-angle boundary, zero equilibrium, signed velocity/energy, period scaling, large amplitude rejected at both entries, time/type/size/order, no mutation | Signed huge-time case absent; independent probe rejects it correctly. Phase/sample representability guard lines unseen: reachability under validated constraints not established. Do not create fake invalid specs to claim legitimate coverage. |
| Four template/setup boundaries | `test_s08_acceptance.py` (12: two static + ten generated) | Single-mutation negatives across four templates; deterministic factories/oracles; sourced output envelopes | Same ID with changed input is not checked for evidence identity (P4). Define revision-binding policy before adding a persisted-output regression; no persistence code inspected. |

## Independent disposition of prior findings

| Prior ID | Status | New independent evidence | Required missing-case check |
|---|---|---|---|
| P1 | **Reproduced** | Both signs of `10**1000`: free fall raises OverflowError; three siblings raise ValueError; inputs unchanged in all eight runs. | Add both signs to free-fall `test_input_rejections`; require readable field-specific ValueError. |
| P2 | **Reproduced** | At Y=2 and Y=4, height=ULP(Y)/8 passes setup but endpoint Y collapses; height=ULP(Y) remains distinct. Four runs isolate coordinate rounding, not a blanket failure for small drops. | Two-origin below-resolution rejection (or explicitly supported relative-coordinate representation), plus one-ULP positive control. |
| P3 | **Reproduced, intentional limit** | Setup accepts each configured unsupported domain; both factory and oracle reject it (four observations). | Capability integration assertion only; existing domain rejection is not broken. |
| P4 | **Reproduced, integration limit** | Changed height with same ID keeps evidence; changing ID changes evidence. | Revision/content binding at a future persistence boundary; no current downstream failure inferred. |

**Refuted:** none of P1–P4. Stronger readings are unsupported: P2 is not universal (positive controls pass); P3 is not an oracle bypass; huge-time rejection is not absent from all sibling suites.

**Unverified:** downstream API/storage effects; actual media decoding; real-size performance; reachability of unexecuted numeric representability guards; simulator and event gates. No new measured physics, gate, or production-security claim.

## Should fix — source-lane follow-up only

1. **Free-fall boundary tests.** What: invalid-time and endpoint contract checks. Problem: passing suite misses P1/P2 and free-fall collection limit. Fix: add the cases above in a separately authorized CODEX-1 run, then smallest production correction. If skipped: these synthetic regressions remain outside the suite.
2. **Scene alternative-format contract tests.** What: mesh/splat size/count and PLY header guards. Problem: existing scene tests never execute those format branches. Fix: small authored byte fixtures and positive/negative size/count cases, without pretending they prove decoding. If skipped: format-contract changes can regress without detection.

Verdict: evidence-only review complete; P1/P2 fixes and production tests remain unimplemented and require separate authorization.

Trace limits: no branch coverage or percentage claimed. Imports before tracing, definition/docstring starts and subprocess calls explain many unseen lines. Defensive representability guards may be unreachable after validation; unseen lines alone are not bugs. `coverage` package unavailable; stdlib selective tracing used without installation.
