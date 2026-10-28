# S07r — implementation readiness is not measured Gate M readiness

**Finding:** the approved plan permits a smaller measured sample; it does not
require three qualified physical inputs before writing the tracker or fitter.
Current queue dependency/acceptance wording nevertheless blocks those runs.
Reconcile controls explicitly; do not silently mark S07a DONE or start S07b.
No approval, calibrated trial, g, uncertainty interval or gate result is created here.

## Source-backed conflict table

Exact numbered excerpts and full local paths: [EXCERPTS.md](EXCERPTS.md).
Full-file hashes and excerpt text: [sources.json](sources.json). These are local
approved-plan/receipt/retained-code records, not a new external research survey.

| Boundary | Exact owning source / conflict | Disposition |
|---|---|---|
| Sample-size fallback | Approved `final plan.html:328`: “if still short, Gate M runs on what exists and reports the sample size.” Queue S02 repeats this at `QUEUE.md:274`. | Three is the planned benchmark sample, not an unconditional implementation prerequisite. Existing bounded Commons/slow-motion research is documented, not an exhaustive search certificate. Record what was searched and remaining sample explicitly; no generic hunt or rights bypass is needed just to write code. |
| Literal S07a acceptance | `QUEUE.md:89`: “Three Earth fall candidates selected; scale and timebase uncertainty documented.” | It says **candidates**, not three **qualified metric trials**. Retained S07a honestly fails this literal count (one approved tracking candidate). It must remain PARTIAL/BLOCKED until a controller records an authorized plan-aligned amendment or its literal check passes. Do not rewrite history. |
| Implementation checks | `QUEUE.md:90–92`: sanitized tracks with provenance; **synthetic** recovery of known g; explicit timebase ambiguity/uncertainty. | These can be implemented/tested without three real calibrated clips. Scientific eligibility must remain separate from software behavior. Existing dependency wiring is an administrative blocker, not evidence of a physical requirement. |
| Physical measurement | `APPROVAL.md:10–21`: physical holds retained, metric fitters abstain until qualified inputs; downstream scoped local pipeline work allowed. `inputs.py:50–84` enforces metric approval, continuity, scale and capture-clock blockers. | Independent applicable scale, capture mapping and uncertainty, authorized metric use, reviewed unforced segment and sufficient observations are still prerequisites for a **real metric fit**. Container FPS, assumed object sizes/Earth g, declared receipt strings and passing synthetic tests are insufficient. |
| Complete release-to-impact | Approved S07 acceptance (`final plan.html:401–418`) contains no full-flight endpoint criterion. Retained contract `README.md:21` asks for a reviewed “pre-impact fall segment”; `inputs.py:108–114` requires a prefix and suffix, not either physical endpoint. S02f research calls absent floor contact a HOLD. | Missing impact is a blocker for a release-height/total-flight-time method, not by itself for every partial-trajectory fit. Do not convert that method-specific observation into a universal tracker/fitter implementation gate. RP01 remains HOLD for its independent scale/clock/geometry gaps; this audit does not qualify it. |
| Measured success versus short sample | Approved S07: g within 5% on **at least 2 of 3** Earth clips with covering uncertainty. `QUEUE.md:93`: “or honest failure/sample size.” | Keep the original pass criterion. On a genuinely measured smaller sample report per-trial results and actual n; do not relabel 1/1 or 2/2 as satisfying the original 2/3 benchmark. Formal small-n success equivalence would be a new owner decision. |
| No physical input | Retained S07a audit: metric-qualified/selected trials zero; S02f zero replacements; S02g neither original jointly scale/clock-qualified. | This is **NOT RUN / input abstention**, not a measured pass or measured failure. An abstention report is not an “actual Gate M result.” Do not trigger a physical-failure fallback or unlock S12 from zero measurements. |
| S12 / fallback | `QUEUE.md:17` and approved `final plan.html:224–226`: Gate M result required before S12. S07 fallback follows an actual gate failure. | Keep S12 locked. A future measured failure plus explicit reviewed fallback decision may determine scope; no such result/decision is made here. Table-plane mode is not automatically validated either. |

## What partial-flight fitting actually permits

**Mathematical inference, not a measurement:** on a calibrated continuous segment,
constant-acceleration position can be parameterized with a free intercept and
initial velocity: `y(t) = a + b*(t-t0) + c*(t-t0)^2`. Neither t0 being the release
instant nor observing impact is intrinsically necessary to estimate curvature.
Acceleration is derived by the deterministic fitter from c with the documented
axis sign and units; no physical number is produced by this audit.

The existing analytic reference accepts signed initial velocity
(`Build/templates/free_fall.py:43–49,78–79`; tests `test_free_fall.py:61–68`) and
tests a duration shorter than impact (`:82–87`). It is **simulated forward-model
evidence**, not an existing inverse fitter or validation of an actual clip.

Three points can identify an ideal quadratic algebraically, but do not establish
robust residual/noise/uncertainty coverage. A short or near-linear visible arc,
correlated tracking error, air forces, unknown projection, retiming, cuts or
scale/clock ambiguity can make g unidentifiable or insufficiently precise. The
existing >=3-prefix / nonempty-suffix validator is an input minimum, not a Gate M
quality guarantee. A later fitter must diagnose conditioning and abstain when
appropriate, propagate physical uncertainties and preserve held-out custody.
Do not force initial velocity to zero at an arbitrary crop, reconstruct an unseen
impact, or use the expected Earth g to certify a guessed slowdown/scale.

## Current evidence: do not merge these counts

- **ST03:** sole approved local Earth-fall tracking candidate in the retained
  audit; approval is scene/tracking only. Scale and capture factor unknown.
  Local pixel tracking is within existing scope; metric fitting is not.
- **FF01/FF02:** not in the ten-ID approval. S02g recovered an independent-method
  rope-height claim for FF02, superseding the blanket “only circular methods”
  interpretation, but not its unknown projection/segment/capture applicability.
  Both share a capture group; filenames or three edited event labels do not
  certify independent qualified trials.
- **RP03/RP01:** new research candidates, not approved uses or calibrated trials.
  S02h/S02i own their active technical checks; no duplication here. Their newer
  outcomes must be integrated by the controller before any candidate disposition
  change. RP02 remains rejected in the reviewed S02f evidence.
- Ten owner-approved local pipeline IDs are not ten Earth falls or ten metric
  approvals. Rights, shortlist approval, capture-group independence, calibration,
  model/runtime eligibility and physical benchmark success are separate facts.

## Minimal controller recommendation — proposed, NOT applied

1. Review retained `run/S07a` input contract/tests. At the next serialized window,
   document the S02 fallback versus S07a leaf conflict in DECISIONS_LOG. Proposed
   S07a acceptance wording: **“Current scoped-approved Earth-fall candidate list
   and actual sample size recorded; scale/capture uncertainties or unknowns and
   blockers explicit; provenance/immutable split/abstention contract tests pass.
   Missing target-three shortlist and metric eligibility remain recorded holds.”**
   Preserve the old failed literal check in its report. This aligns implementation
   readiness with the standing plan; it does not lower Gate M's physical target.
2. Only after explicit controller acceptance/amendment and fresh verification,
   authorize the S07b implementation run against this contract. Scope it to
   sanitization, pixel/frame/PTS provenance and isolated synthetic adapter tests;
   any actual ST03 processing stays scene/tracking-only and separately observes
   applicable model/licence/runtime/budget safeguards. Allow null scale/clock and
   return blockers; do not require metric_eligible merely to produce pixel tracks.
3. Follow with S07c/S07d deterministic fitter and uncertainty/abstention tests on
   clearly synthetic tracks. Real metric execution must still reject unresolved
   approval/scale/clock/continuity/custody. Review the existing contract before
   reuse: it authenticates neither receipt text nor external held-out custody.
4. Keep S07e measured execution and S12 locked until their real prerequisites
   exist. When qualified approved trials exist, run on the available sample under
   the standing fallback and report n, exclusions, groups, method and uncertainty.
   Preserve original target and obtain cross-vendor gate review. With zero usable
   trials record input abstention, not a fabricated gate failure or completion.

**Owner decisions genuinely still needed:** approval of new candidate IDs or
metric-use scope once a concrete technically qualified proposal exists; any
change making small-n results formally equivalent to the original pass criterion;
any newly expanded spend/public/deployment action. None is necessary merely to
implement/test the existing scene-only boundary and synthetic fitter. No owner
question is opened here to repeat already-known calibration shortages. Controller
must relay any future concrete decision through STATE's owner-question fallback;
this shard has no shared-control write permission.
