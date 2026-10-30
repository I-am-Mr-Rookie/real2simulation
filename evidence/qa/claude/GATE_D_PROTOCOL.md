# Gate D QA protocol and checklist (S22a)

Author run: S22a-orch70 (CLAUDE, Opus 5.5 medium assigned). Written 2026-10-30 from main a2fa169.
Status: **protocol only. Gate D is NOT met and NOT assessed.** No product code, deploys, accounts or terms touched.
Current per-surface checklist (main 67e299a): [GATE_D_CHECKLIST.md](GATE_D_CHECKLIST.md) (S22a-orch127); it supersedes the dependency table below.

## 0. Authority and hard preconditions

- Gate D (final plan S22, Nov 3): (a) a **fresh account completes upload -> report in < 5:00, 3 runs in a row**;
  (b) a **logged-out judge can open and run a library demo**. Evidence class E4.
  Fallback if not met at freeze: demo video uses the library path; uploads limited (S22j records it).
- Scoring lens: JUDGE_RUBRIC.md (Impact 30, Tooling 25, Depth 20, Demo 25). Gate D mainly protects **Demo**
  ("product holds up live") and **Depth** ("sound, refined"). Rubric is a lens for defect priority, never a score claim.
- **Written candidate-deploy approval from Koushik is required before any judging traffic** or judging/candidate
  environment exists. Until then S22b-i run ONLY against Railway **dev** (owner-approved Oct27):
  web https://web-dev-cd80.up.railway.app (api/worker per STATE.md Deployments). Dev results are rehearsal evidence,
  not Gate D evidence. S22 itself performs **no deploys**; deploy belongs to S23 after written go-ahead.
- **Accounts/terms:** creating a fresh account or accepting Clerk/app terms needs Koushik's written approval
  per account. Without it, record the flow step as BLOCKED-BY owner-approval; never use a personal account,
  never reuse one account and call it "fresh".
- Browser: signed-in ChatGPT in-app browser (owner instruction Oct28), not Chrome. Secrets: key-name presence only.
- Numbers shown in UI must come from fitter/simulator and carry measured/simulated labels; QA records, never edits.

## 1. Dependency gate (state at a2fa169)

| Dep | Needed for | Current | Effect |
|---|---|---|---|
| S15k/S15l workspace full flow + a11y | upload->report flow, 375px | TODO | Section 3/4 BLOCKED-BY S15k, S15l |
| S16a-h sidebar tools/search | sidebar patch/search checks | all TODO | 3.6 BLOCKED-BY S16 |
| S17f report a11y/fallback | report download/print | TODO (S17a-e DONE) | 5.4 BLOCKED-BY S17f |
| S19d installability/375 walkthrough | PWA/375 | TODO (S19a-c DONE) | 4.3 BLOCKED-BY S19d |
| S20c failover / S20d Gate C regression | spend-cap UI behaviour | PARTIAL / TODO | 5.2-5.3 BLOCKED-BY S20c, S20d |
| S14g/S14h Gate A interview | interview step | PARTIAL / TODO | 3.4 BLOCKED-BY S14g, S14h |
| S01b/S04h real sessions | sign-in (STATE: "sign-in unavailable" on dev) | open | 3.1-3.2, 4.2 BLOCKED-BY S04h |
| Owner written candidate-deploy approval + candidate env | real Gate D run | none on record | all Gate D-of-record runs BLOCKED-BY owner-approval (candidate). S23a (frozen judging promotion) is a separate later approval, after S22 |
| S18 library demos (+ viewer connected on /library) | guest demo run | S18a-j TODO; dev /library shows no demos | 2.2-2.4 BLOCKED-BY S18 |

Runnable now (dev, read-only): Section 2 guest library checks and the logged-out half of 4.2.

## 2. Guest library walkthrough (S22b)

Logged-out fresh browser profile/private window, cache cleared.

| # | Step | Pass | Fail |
|---|---|---|---|
| 2.1 | Open web root | 200, no login wall, link to /library visible | redirect to sign-in, 5xx, blank |
| 2.2 | Open /library | >=1 precomputed demo listed with licence/credit field | empty, missing licence, unlicensed clip |
| 2.3 | Open a demo scene and its viewer | 3D scene renders within 15 s; controls respond | WebGL error, endless spinner |
| 2.4 | Run the demo (simulate/replay) | runs to completion; numbers labelled measured/simulated | unlabelled or model-authored numbers |
| 2.5 | Attempt upload / private route as guest | blocked with clear sign-in prompt; 401/403/404 per auth CONTRACT | upload accepted, private data visible |
| 2.6 | Console + network | no uncaught errors, no secret/storage-root URL in responses | any token/secret, 5xx on happy path |

Gate D (b) passes only when 2.1-2.5 pass on the **approved candidate/judging URL** (BLOCKED-BY owner-approval); dev = rehearsal.

## 3. Fresh-account full flow x3 (S22c/S22d/S22e)

Each run: new approved account (or owner-designated demo account reset to empty -- record which), new profile,
stopwatch from first click on sign-up/sign-in to report visible. One clip from approved clips.csv set, same
for all three unless owner varies it; record clip id + licence.

| # | Step | Pass | BLOCKED-BY |
|---|---|---|---|
| 3.1 | Sign up / sign in (Clerk Google or email OTP) | session established; no terms accepted without approval | S04h, owner-approval |
| 3.2 | Land in private workspace | own empty state; no other user's scenes | S04h |
| 3.3 | Upload approved clip | stage events visible (S15c); quota/cap message honest | S15k |
| 3.4 | Agent interview | valid spec; chips + free text; no invented numbers | S14g, S14h |
| 3.5 | Run experiment / fit | fit table + residuals from fitter; labels kept | S15k |
| 3.6 | Sidebar patch/search (if in build) | invalid patch rejected before rebuild | S16 |
| 3.7 | Report rendered | every number == fitter output; download/print works or honest fallback | S17f |
| 3.8 | Total time | **< 5:00** wall-clock | -- |

Gate D (a) passes only if **three consecutive** runs each pass 3.1-3.8; any failure resets the streak (record it,
do not discard it). Screenshots alone never pass a step (S22f rule): need timing log + network/console capture.

## 4. 375px and auth boundary (S22g)

| # | Check | Pass | BLOCKED-BY |
|---|---|---|---|
| 4.1 | 375x812 viewport: library, viewer, workspace, report | no horizontal scroll; sidebar below viewport; tap targets usable | S15l |
| 4.2 | Auth boundary: guest vs signed-in vs other account | guest: library only; cross-account scene id -> 403/404, no existence leak; sign-out clears private views | S04h (guest half runnable now) |
| 4.3 | PWA install + 375 walkthrough | installability evidence; private/auth responses not cached | S19d |
| 4.4 | Keyboard/error states | focus visible, errors announced | S15l |

## 5. Retry, spend-cap and report (S22h)

| # | Check | Pass | BLOCKED-BY |
|---|---|---|---|
| 5.1 | Retry after induced/observed stage failure | retry visible, idempotent, no duplicate spend row | S15k |
| 5.2 | Spend cap reached (simulated, not real money) | uploads pause with honest message; **library keeps working**; $30 reserve untouched | S20c, S20d |
| 5.3 | AWS failover state | disabled by default unless owner gate met; UI makes no false claim | S20c |
| 5.4 | Report download/print/fallback | works or honest fallback; no fabricated PDF success | S17f |

QA must not spend real money to hit a cap; use the S20d simulated-cap path only.

## 6. Recheck and decision (S22f, S22i, S22j)

- S22f: Opus judges S22b-e evidence; defects ranked P0 (blocks Gate D or exposes data/secrets/spend), P1 (Demo
  rubric damage: crash, >5 min, wrong number), P2 (polish). Fixes go to owner lanes as new scoped tasks.
- S22i re-runs only broken flows on the approved candidate; a fixed flow still needs a fresh 3-in-a-row streak.
- S22j: PASS only with 3 consecutive <5:00 fresh runs + guest pass on the judging URL; else library-only fallback
  with upload limits. Cross-vendor review required.

## 7. Evidence capture format (S22b-i)

Path: `evidence/qa/browser/<RID>/`. One `run.json` per flow plus referenced files.

```json
{
  "rid": "S22c-orchNN", "step": "S22c", "flow": "fresh-account-1",
  "environment": "dev|judging", "url": "https://...", "deployed_sha": "<from health or S23 record>",
  "candidate_approval_receipt": "<path or null>", "account_approval_receipt": "<path or null>",
  "account_kind": "fresh|owner-demo-reset|guest", "browser": "ChatGPT in-app", "viewport": "1280x800|375x812",
  "clip_id": "<clips.csv id>", "started_utc": "...", "ended_utc": "...", "duration_s": 0,
  "steps": [{"id": "3.3", "result": "PASS|FAIL|BLOCKED", "blocked_by": null, "note": "", "evidence": ["shots/3.3.png", "har/flow.har"]}],
  "console_errors": 0, "secrets_observed": false, "outcome": "PASS|FAIL|BLOCKED"
}
```

Rules: UTC timestamps; durations measured, not estimated; HAR/console logs redacted of cookies/tokens before
commit; no private teammate/personal data; failed runs kept. Dev runs set `environment: "dev"` and never count
toward Gate D of record.

## 8. Not covered / limits

Only a read-only HTTP probe of dev ran (S22a-dev-guest-probe.md): /library serves but **"No demos are published yet"**
-> 2.2 FAIL, 2.3/2.4 additionally BLOCKED-BY published library scenes (S18 library demos + viewer connection).
Not browser-rendered; deployed SHA on dev unverified; Clerk sign-in on dev reported unavailable (STATE), not re-tested.

