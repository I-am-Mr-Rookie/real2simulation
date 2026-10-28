# Exact local-source excerpts

Captured 2026-10-28T06:20:37.892967+00:00; queue range correction during verification. Excerpts only, not complete files. Full paths and SHA256: sources.json. Retained records, not fresh external verification.

## manifest
Source: `C:\Users\HP\Documents\Hackathon\2026-10-26 - Meta Global AI Developer Hackathon\Run-System\Runs\S07r\DISPATCH.md`

```text
11: Potential structural bottleneck: approved final plan S02 fallback explicitly
12: says, if still fewer than3 usable free falls after Commons strobe/slowmotion
13: search, Gate M runs on what exists and reports sample size. QUEUE S07a literal
14: acceptance instead requires3 Earth candidates. S07a implementation is retained
15: unmerged in C:/Users/HP/.codex/worktrees/s07a/2026-10-26 - Meta Global AI Developer Hackathon.
16: Read actual final plan S02/S07, current queue/gates/approval receipts, retained
17: S07a contract/tests/audit, S02f/S02g reports at their managed worktrees. New
18: RP03/RP01 technical checks run separately; don't duplicate source investigation.
19:
20: Objective: source-backed reconcile what is genuinely required BEFORE tracking/
21: fitting implementation versus only for measured Gate M success. Identify any
22: invented full-release/impact or three-qualified-input prerequisite; distinguish
23: candidate selection, owner-use approval, calibration, partial-flight fitting,
24: sample-size fallback, and actual measured result. Do not silently relax criteria
25: or treat absent calibration/sample as a measured Gate M failure/pass. Do not
26: unlock S12 or fabricate g/timebase/uncertainty. An explicit abstention is not a
```

## plan
Source: `C:\Users\HP\Documents\Hackathon\2026-10-26 - Meta Global AI Developer Hackathon\08 Real2Simulation\final plan.html`

```text
316:       "id": "S02",
317:       "title": "Build the licensed public clip set",
318:       "priority": "critical",
319:       "timebox_minutes": 120,
320:       "owner": "CODEX-2 · GPT-6.1 Terra (high, browsing and computer use only) + Koushik (10-minute approval)",
321:       "dependencies": [],
322:       "acceptance": [
323:         "At least 10 clips plus clips.csv in test-data/public, every row with source, licence and attribution",
324:         "Every clip has a frame rate from the file metadata and a known-size reference object, or is marked scene-only",
325:         "Koushik's approval of the list recorded in DECISIONS_LOG.md"
326:       ],
327:       "evidence_required": "E1",
328:       "fallback": "If fewer than 3 usable free-fall clips are found, add Wikimedia Commons strobe and slow-motion clips and treat slow-motion timebase detection (S07) as required; if still short, Gate M runs on what exists and reports the sample size."
329:     },
```

```text
401:       "id": "S07",
402:       "title": "Gate M spike: measure g from public free-fall clips",
403:       "priority": "critical",
404:       "timebox_minutes": 180,
405:       "owner": "CODEX-1 · GPT-6.1 Sol (medium; high for gates)",
406:       "dependencies": [
407:         "S01",
408:         "S02",
409:         "S03"
410:       ],
411:       "acceptance": [
412:         "g within 5% of 9.81 m/s^2 on at least 2 of 3 Earth free-fall clips, with a stated uncertainty that covers the error",
413:         "Stretch: the Apollo 15 clip gives the Moon's g within 15%",
414:         "Fitter unit tests pass on synthetic data"
415:       ],
416:       "evidence_required": "E2",
417:       "fallback": "If Gate M fails, Measure mode is limited to table-plane experiments (homography only) and the pitch leads with the virtual lab and Mystery-g. Log it as a decision."
418:     },
```

```text
224:    and go into STATE.md, batched once a day.
225: 3. Order: spikes first (S05, S07 on CODEX-1) while CODEX-2 builds S04, Terra sources S02, and Opus
226:    builds S09 against a fixture scene. Do not start S12 before Gate M has a result.
```

## queue
Source: `C:\Users\HP\Documents\Hackathon\2026-10-26 - Meta Global AI Developer Hackathon\QUEUE.md`

```text
15: - S05a is contract/licence-only after S03; S05b and actual reconstruction wait for completed, owner-approved S02. No Gate R result is claimed from contract work.
16: - S01/S04 acceptance loop is explicitly split: S04a starts after S01a/S01c, while S01b sign-in verification waits for S04g and S04h waits for S01b. This preserves final step acceptance without a cycle.
17: - S12 waits for an actual Gate M result including explicit fallback, never an assumed pass. S22 judging access waits for written candidate-deployment approval; S23 is later promotion of a frozen revision, separately authorized.
```

```text
89: | S07a | CODEX-1 | GPT-6.1 Sol / medium | S07 | 30 | Define scale, timestamps and held-out tracking inputs | S01a, S01c, S02, S03 | Build/measurement/; tests/measurement/; evidence/S07/ | Three Earth fall candidates selected; scale and timebase uncertainty documented. | BLOCKED |
90: | S07b | CODEX-1 | GPT-6.1 Sol / medium | S07 | 30 | Implement SAM 3.1 tracking adapter | S07a | Build/measurement/; tests/measurement/; evidence/S07/ | Sanitized track output carries frame/time coordinates and provenance. | TODO |
91: | S07c | CODEX-1 | GPT-6.1 Sol / medium | S07 | 30 | Implement deterministic free-fall fit | S07b | Build/measurement/; tests/measurement/; evidence/S07/ | Synthetic tracks recover known g; units and residuals tested. | TODO |
92: | S07d | CODEX-1 | GPT-6.1 Sol / medium | S07 | 30 | Detect slow-motion and propagate measurement uncertainty | S07c | Build/measurement/; tests/measurement/; evidence/S07/ | Timebase ambiguity is explicit; uncertainty includes scale and timestamps. | TODO |
93: | S07e | CODEX-1 | GPT-6.1 Sol / high | S07 | 30 | Run Earth Gate M measurements | S07d | Build/measurement/; tests/measurement/; evidence/S07/ | 2/3 within 5% of 9.81 with uncertainty covering error, or honest failure/sample size. | TODO |
94: | S07f | CODEX-1 | GPT-6.1 Sol / high | S07 | 30 | Evaluate Apollo stretch and record Gate M decision | S07e, R-M | Build/measurement/; tests/measurement/; evidence/S07/ | Moon target within 15% if available; table-plane fallback logged if Earth gate fails. | TODO |
```

```text
265: ### S02 — Build the licensed public clip set
266:
267: - Source owner: CODEX-2 · GPT-6.1 Terra (high, browsing and computer use only) + Koushik (10-minute approval)
268: - Source timebox: 120m; priority: critical; source dependencies: none.
269: - Leaf tasks: S02a, S02b, S02c, S02c1 (NASA support), S02c2 (room support), S02d, S02e. S02c workers explicitly apply Ponytail; see S02C_PARALLEL.md. Shard research completion is not parent clip acceptance.
270: - Required evidence: E1.
271: - Acceptance: At least 10 clips plus clips.csv in test-data/public, every row with source, licence and attribution
272: - Acceptance: Every clip has a frame rate from the file metadata and a known-size reference object, or is marked scene-only
273: - Acceptance: Koushik's approval of the list recorded in DECISIONS_LOG.md
274: - Fallback: If fewer than 3 usable free-fall clips are found, add Wikimedia Commons strobe and slow-motion clips and treat slow-motion timebase detection (S07) as required; if still short, Gate M runs on what exists and reports the sample size.
275: - Status: S02a/S02b DONE. S02c unmerged54460a5: eleven unapproved local candidates, two narrowly checked for local visual tracking/scene-motion feasibility only; require-ten fails2/10. Owner changed S02c to Opus5.5/high, retaining CODEX-2 ownership. Q2 permits provisional licensed local acquisition; Pexels public-repository redistribution and third-party rights remain unresolved. S02d/S02e not started; no calibrated trial or final-use owner approval; parent acceptance not claimed.
```

```text
326: ### S07 — Gate M spike: measure g from public free-fall clips
327:
328: - Source owner: CODEX-1 · GPT-6.1 Sol (medium; high for gates)
329: - Source timebox: 180m; priority: critical; source dependencies: S01, S02, S03.
330: - Leaf tasks: S07a, S07b, S07c, S07d, S07e, S07f.
331: - Required evidence: E2.
332: - Acceptance: g within 5% of 9.81 m/s^2 on at least 2 of 3 Earth free-fall clips, with a stated uncertainty that covers the error
333: - Acceptance: Stretch: the Apollo 15 clip gives the Moon's g within 15%
334: - Acceptance: Fitter unit tests pass on synthetic data
335: - Fallback: If Gate M fails, Measure mode is limited to table-plane experiments (homography only) and the pitch leads with the virtual lab and Mystery-g. Log it as a decision.
336: - Status: NOT STARTED — acceptance not claimed.
337:
```

## approval
Source: `C:\Users\HP\Documents\Hackathon\2026-10-26 - Meta Global AI Developer Hackathon\evidence\owner\S02\APPROVAL.md`

```text
3: Direct owner response to Q7:
4: > A: Approve scoped local processing; retain all holds (Recommended)
5:
6: **Approved IDs:** RM02,RM04,RM05,PD02,PD03,PD04,PD06,PJ03,ST03,BN01.
7: **Use:** local scene/tracking pipeline work ONLY, under existing source/licence
8: restrictions. This is the authoritative scoped approval record; older CSV
9: UNAPPROVED_CANDIDATE/owner_approved=NO flags describe prior broad status and
10: MUST NOT be interpreted as public/final-use approval or changed broadly.
11:
12: **Holds retained:** no verified physical scale/capture timebase, calibrated g or
13: restitution, physical gate success, full original category coverage, public raw
14: media redistribution, other candidate use, GPU execution/spend increase or deploy.
15: RM05 is ISS, not an Earth room. AP15 NOT_TRACKABLE and ST05 HOLD remain excluded.
16: Fitters requiring verified metric inputs must abstain until qualified inputs exist.
17: GPU scheduling priority remains subject to runtime/budget/rights prerequisites.
18:
19: S02e owner decision is complete; downstream runs may do scoped local pipeline work.
20: Source evidence: decision-request.md; clips.csv;
21: evidence/clips/S02d-metadata-scale-audit.md.
```

## a-audit
Source: `C:\Users\HP\.codex\worktrees\s07a\2026-10-26 - Meta Global AI Developer Hackathon\evidence\S07\S07a-input-audit.md`

```text
3: **PARTIAL. Literal acceptance remains unmet:** "Three Earth fall candidates
4: selected; scale and timebase uncertainty documented." The approved local set
5: contains **one** Earth-fall candidate (ST03), not three. None has a verified
6: independent metric scale AND capture timebase, and metric processing is not
7: approved. No g, residual, physical uncertainty interval or Gate M result exists.
8:
```

```text
29:
30: ## Input and uncertainty disposition
31:
32: [Contract](../../Build/measurement/README.md) and validator require explicit
33: source hash, receipt references, scoped approval, coordinates/PTS, immutable
34: prefix/suffix split and non-circular scale/capture mapping. Unknown scale or
35: capture clock stays null and produces abstention. No arbitrary standard object
```

```text
43: split/track is generated here because the calibration/capture inputs are absent
44: and no tracking task was requested. ST03 cannot enter a metric fit under current
45: approval even if synthetic contract tests pass.
46:
47: ## Acceptance check (deliberately fails)
48:
49: From this run worktree, after verifying receipt source hashes against canonical:
50:
```

## a-contract
Source: `C:\Users\HP\.codex\worktrees\s07a\2026-10-26 - Meta Global AI Developer Hackathon\Build\measurement\README.md`

```text
3: `inputs.validate_input(record)` validates a JSON-compatible object. Malformed
4: data raises `ValueError`. Valid scene/tracking input may carry abstention
5: `blockers`; an empty list means declared prerequisites are present, **not** that
6: rights/calibration were independently verified or Gate M passed. No model,
7: tracking, fitting, download, remote call or physical number is produced here.
8: This function is not an approval authority: a trusted run must resolve evidence,
9: licence and scope before use. Never manufacture `metric_measurement` approval.
10: Current S02 approval grants `scene_tracking` only for the ten listed IDs.
```

```text
21: | `continuous_segment_evidence` | Reviewed uninterrupted, non-reversed, pre-impact fall segment. Null/empty => abstain. Repeats/edits/occlusions need explicit segment/time mapping before any fit. |
22: | `scale` | Null if unknown; otherwise independent in-plane reference with fields below. Unknown is not zero. |
23: | `timebase` | Null if unknown; otherwise verified capture-time mapping with fields below. File/container FPS alone cannot fill it. |
```

```text
50: source hash, selected segment, immutable split, calibration evidence and config
51: hash **before** any fit. Send only `training` and frozen prefix-derived calibration
52: to S07b/S07c. Keep suffix coordinates/frames out of tracking tuning, calibration,
53: model prompts and fitting; evaluate predictions once against the withheld suffix.
54: Changing the split after viewing errors invalidates that evaluation. This local
55: validator cannot enforce external storage custody or prevent a caller from
56: reading `held_out`; downstream integration must enforce it. It does not seal a
57: dataset or authenticate caller-supplied evidence strings.
58:
59: S07d must propagate scale, time-ratio, per-frame timestamp/coordinate precision,
60: tracking error and covariance/systematic effects; this validator merely preserves
61: declared calibration requirements and rejects malformed numbers. Uncertainty in
62: g depends on scale and inverse-square capture-time ratio, so playback acceleration
63: is not g. Never set uncertainty to an invented value to unlock a fit; if unknown,
64: set the whole calibration object null. No uncertainty propagation is implemented
65: or claimed in S07a. Zero is allowed only when independently justified in evidence.
```

## a-code
Source: `C:\Users\HP\.codex\worktrees\s07a\2026-10-26 - Meta Global AI Developer Hackathon\Build\measurement\inputs.py`

```text
50:     for key in ("clip_id", "licence", "provenance", "motion"):
51:         if not _text(data.get(key)):
52:             raise ValueError(f"{key} required")
53:     if not isinstance(data.get("source_sha256"), str) or not re.fullmatch(
54:         r"[0-9a-f]{64}", data["source_sha256"]
55:     ):
56:         raise ValueError("source_sha256 must be lowercase hex")
57:     approval = data.get("approval")
58:     if not isinstance(approval, dict) or approval.get("scope") not in (
59:         "scene_tracking", "metric_measurement"
60:     ) or not _text(approval.get("evidence")):
61:         raise ValueError("explicit scoped approval evidence required")
62:     blockers = []
63:     if approval["scope"] != "metric_measurement":
64:         blockers.append("metric_use_not_approved")
65:     if data["motion"] != "earth_free_fall":
```

```text
78:             raise ValueError(f"{name} must be null or an object")
79:         if section is not None:
80:             for field, positive in fields:
81:                 if field in section:
82:                     _number(section[field], f"{name}.{field}", positive=positive)
83:     if not (scale and scale.get("method") == "independent_reference"
84:             and scale.get("plane_verified") is True and _text(scale.get("evidence"))
```

```text
108:         if parsed and (index <= parsed[-1].frame_index or pts <= parsed[-1].pts_s):
109:             raise ValueError("frame indices and video PTS must strictly increase")
110:         parsed.append(Frame(index, pts, x, y))
111:     training = tuple(f for f in parsed if f.frame_index <= split)
112:     held_out = tuple(f for f in parsed if f.frame_index > split)
113:     if len(training) < 3 or not held_out or training[-1].frame_index != split:
114:         raise ValueError("split must end a >=3-frame prefix and leave a nonempty suffix")
```

## a-tests
Source: `C:\Users\HP\.codex\worktrees\s07a\2026-10-26 - Meta Global AI Developer Hackathon\tests\measurement\test_inputs.py`

```text
28:         result = validate_input(synthetic_input())
29:         self.assertIn("metric_use_not_approved", result.blockers)
30:         self.assertFalse(result.metric_eligible)
31:
32:     def test_qualified_synthetic_input_has_disjoint_immutable_prefix_suffix(self):
```

```text
46:         data.update(scale=None, timebase=None, continuous_segment_evidence=None)
47:         self.assertEqual(set(validate_input(data).blockers), {
48:             "metric_use_not_approved", "scale_unverified", "capture_timebase_unverified",
49:             "continuous_segment_unverified"})
50:
51:     def test_circular_scale_and_unverified_plane_abstain(self):
52:         for changes in ({"method": "fall_time"}, {"plane_verified": False}, {"evidence": ""}):
```

```text
59:         data["timebase"] = {"file_fps": "25/1"}
60:         self.assertIn("capture_timebase_unverified", validate_input(data).blockers)
61:
62:     def test_non_fall_motion_cannot_count_as_earth_trial(self):
63:         for motion in ("projectile", "bounce", "pendulum", "iss", "lunar_free_fall"):
64:             data = synthetic_input()
65:             data["motion"] = motion
66:             self.assertIn("not_earth_free_fall", validate_input(data).blockers)
67:
68:     def test_bad_numbers_bounds_order_or_leaking_split_rejected(self):
```

## f-report
Source: `C:\Users\HP\.codex\worktrees\s02f-research\2026-10-26 - Meta Global AI Developer Hackathon\Run-System\Runs\S02f\REPORT.md`

```text
16: **Literal objective remains unmet: 0/3 metric-qualified replacements.**
17: Three source/licence-backed media files were provisionally acquired, fully
18: decoded and visually audited; that is not three suitable benchmark trials.
19: No S07a completion, Gate M, g, fitter run, physical uncertainty, new approval
20: or model/GPU processing is claimed.
21:
22: 1. **RP03 strongest HOLD:** new April2025 Rhetos drop. Embedded independent
23:    rope-height evidence9.00 m; explicit240 fps capture,200 fps editing and20x
24:    replay declarations. Top-down depth-changing geometry is not a valid affine
25:    image-plane scale; capture/edit/replay mapping and uncertainty remain
26:    unresolved. One drop plus replay is not two trials.
27: 2. **RP01 HOLD:** NUSTEM metre-rule/g-ball apparatus has independent physical
28:    scale/timer potential. Inspected127–128 s release loses the ball below frame
29:    before floor contact; camera capture provenance and plane applicability
30:    absent. Delivered25 fps is not evidence of actual capture timing.
31: 3. **RP02 REJECT for metric shortlist:** GetAClass real studio slow-motion
32:    falls, no identified dimensional witness or capture clock; dark/small
33:    objects, edits and unclear endpoints. No assumed standard object size.
```

## f-research
Source: `C:\Users\HP\.codex\worktrees\s02f-research\2026-10-26 - Meta Global AI Developer Hackathon\evidence\clips\calibration-recovery\S02f\RESEARCH.md`

```text
9: | Rank | Candidate | New evidence | Unmet requirement / action |
10: |---|---|---|---|
11: | 1 | RP03 — [Impaktecholot (Pilotversuch)](https://commons.wikimedia.org/wiki/File:Impaktecholot_(Pilotversuch).webm) | April 18, 2025, Rhetos. Embedded slate explicitly distinguishes a **9.00 m nonstretch-rope measurement** from circular optical/acoustic estimates. Capture slate: DJI Osmo Action 4, **240 fps captured, 200 fps edited**; another slate explicitly labels a **20x replay**. These are source claims, not derived slowdown estimates. | HOLD. Camera looks downward; depth changes greatly through descent, so 9 m endpoint height is **not** an image-plane metres-per-pixel reference. No calibrated projection/reference plane or scale uncertainty. Delivery is 60 fps; mapping from capture to edit to replay/transcode has not been verified. Same single drop repeated, not two trials. Best next technical lead, but not fit-ready. |
12: | 2 | RP01 — [A-level Physics Core Practical](https://commons.wikimedia.org/wiki/File:A-level_Physics_Core_Practical-_Finding_a_value_for_g_using_a_free_fall_method.webm) | NUSTEM, 2016. Producer [notes](https://nustem.uk/activity/measuring-g/) identify a metre rule/bracket and independent g-ball release/impact timer, with 0.01 s display resolution. | HOLD. Reviewed g-ball release around 127–128 s is visible, but ball drops below the lower image before floor contact; no certified continuous release-to-impact segment. Ruler coplanarity/projective error and readable ruler endpoints unverified. 25 fps file cadence is not camera provenance. Apparatus timing is not per-frame mapping. Do not turn separate methods/cuts into independent trials. |
13: | 3 | RP02 — [Свободное падение](https://commons.wikimedia.org/wiki/File:%D0%A1%D0%B2%D0%BE%D0%B1%D0%BE%D0%B4%D0%BD%D0%BE%D0%B5_%D0%BF%D0%B0%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5.webm) | GetAClass, 2014; Commons cooperation provenance and CC BY 3.0. Actual HD file inspected: real paired-object studio drops near 65–73 s and 105–114 s, distinct from surrounding drawn animation. | REJECT for metric shortlist. No numbered ruler/known object dimension in reviewed drop views; dark objects, low contrast and undocumented slow motion. 24000/1001 delivered fps does not establish capture rate. Endpoints/independence not certified. Do not infer dimensions from wood, ball, backdrop or studio equipment. |
```

```text
59:    it does describe rope measurement and25 fps Lumix capture. Preliminary
60:    summary/pointers retained; **S02g now owns all further FF01/FF02 forensics**.
61:    Nothing about current segment applicability or independent trials is proven
62:    here. Previously generated FF sheets are ignored and not used as conclusions.
63: 2. NUSTEM's producer notes and visible ruler might qualify a replacement:
64:    apparatus is promising, but inspected framing loses the impact and no actual
65:    camera-clock mapping was found. Independent hardware total time alone is not
66:    a licence to infer a uniform slow-motion multiplier.
67: 3. GetAClass's educational experiment might contain a calibrated studio shot:
68:    reviewed footage has real falls but no identified dimensional or capture-time
69:    witness. Rejected instead of inventing standard object dimensions.
70: 4. New April2025 Rhetos capture might add a separate, high-rate trial: source
71:    supplies concrete capture/edit/rope information, but top-down projective
72:    geometry and edit mapping prevent metric qualification.
73:
74: Firecrawl plus web searches were focused on ruler/size, capture cadence and
75: primary allowed-source educational footage. Searches returning stroboscopic
```

## g-report
Source: `C:\Users\HP\.codex\worktrees\s02g-forensics\2026-10-26 - Meta Global AI Developer Hackathon\Run-System\Runs\S02g\REPORT.md`

```text
3: **Result:** recovered a previously unestablished **non-circular rope-height
4: measurement claim** in FF02's original creator article. Neither FF01 nor FF02
5: has demonstrated segment-applicable metric scale **and** capture-time mapping.
6: No clip approval, independent qualified-trial count, S07a completion or Gate M.
```

```text
27: - FF01 height remains fall-time/gravity-derived. FF02's creator also describes
28:   a rope lowered from railing to ground and measured with folding rulers.
29:   That is an independent-method **claim**, not yet verified spatial calibration.
30:   Stair ruler is in another shot/plane; cyclist height assumed; top-down
31:   perspective and release/impact/reference correspondence unresolved.
32: - Corrected 20→25fps upload and Lumix25fps testimony verified in primary text.
33:   Actual files both deliver25fps/40ms PTS; edits include holds, crossfades and
34:   frame-stepping. Delivery clock/editor overlays do not prove capture mapping.
35: - FF02 contains three labelled sandbag events plus wood; FF01/FF02 retain one
36:   common capture group. No certified duplicate mapping or independent qualified
37:   extra trial. Diagnostic SSIM/exact-hash limitations are explicit, not hidden.
38: - Commons CC BY-SA4.0 and differing embedded CC BY4.0/Mathe-AC notices retained.
```

## g-findings
Source: `C:\Users\HP\.codex\worktrees\s02g-forensics\2026-10-26 - Meta Global AI Developer Hackathon\evidence\clips\calibration-recovery\S02g\FINDINGS.md`

```text
52:
53: The camera looks steeply down from the railing; hand, railing, falling bag,
54: stairs and ground have different depths. The ruler shot cannot supply a global
55: metres/pixel factor. Even a trusted 9m vertical span does not establish the
56: projective mapping along this foreshortened motion. Release hand height,
57: ground endpoint, camera pose/movement, lens model and reference correspondence
58: remain unverified. The rope claim cannot automatically be transferred to FF01.
59:
60: ## Time: corrected claim versus demonstrated mapping
```

```text
103: Multiple events in one capture group may eventually supply distinct repetitions,
104: but share the same scale/clock systematic errors. Neither two filenames nor
105: three edited labels establish independent qualified trials. No extra trial is
106: credited here.
107:
108: ## Rights and next bounded check
109:
110: Commons declares both originals **CC BY-SA 4.0**, author Rhetos. Their end cards
111: instead state CC BY 4.0 and name Mathe-AC Lernwerkstatt Aachen. Preserve both
112: notices; retain the existing stricter Commons route, not an inferred relicence.
113: See [local derivative notice](LICENSE-NOTICE.md). FF01/FF02 remain absent from
114: the scoped owner-approved ten IDs. Forensic inspection is authorized by S02g;
115: pipeline/metric/final/public use is not thereby approved.
116:
```

## analytic
Source: `C:\Users\HP\Documents\Hackathon\2026-10-26 - Meta Global AI Developer Hackathon\Build\templates\free_fall.py`

```text
1: """Validated free-fall inputs and an independent closed-form Gate P reference.
2:
3: No integrator, fitter, external calls, default physical numbers or measured claims.
```

```text
43:
44: def analytic_free_fall(spec, scene, scene_root, *, times=()):
45:     """Return ideal stop-plane impact plus requested pre-impact samples.
46:
47:     Positive Y velocity is upward. Samples must lie in [0, min(duration, impact)].
48:     Impact metrics describe the full ideal flight, even if duration is shorter.
49:     Input uncertainty is NOT propagated; result uncertainty stays null.
```

```text
78:         # Anchor the endpoint to its exact stop-plane definition.
79:         y = origin[1] - h if t == impact else origin[1] + t * (v - 0.5 * g * t)
```

## analytic-tests
Source: `C:\Users\HP\Documents\Hackathon\2026-10-26 - Meta Global AI Developer Hackathon\tests\spec\test_free_fall.py`

```text
61:     def test_signed_velocity_and_upward_apex(self):
62:         self.scene['gravity']['magnitude_m_s2'] = 8
63:         for v, expected_t, expected_v in [(3, 1, -5), (-3, 0.25, -5)]:
64:             with self.subTest(v=v):
65:                 spec = self.make(gravity=quantity(8, 'm/s^2'),
66:                                  initial_vertical_velocity=quantity(v, 'm/s'))
67:                 a = self.api.analytic_free_fall(spec, self.scene, BUNDLE, times=[0, expected_t])
68:                 self.assertEqual(a['impact_time']['value'], expected_t)
```

```text
82:     def test_short_duration_does_not_fake_impact_sample(self):
83:         spec = self.make(duration=quantity(0.1, 's'))
84:         a = self.api.analytic_free_fall(spec, self.scene, BUNDLE, times=[0.1])
85:         self.assertGreater(a['impact_time']['value'], 0.1)
86:         with self.assertRaisesRegex(ValueError, 'times'):
87:             self.api.analytic_free_fall(spec, self.scene, BUNDLE, times=[0.2])
```
