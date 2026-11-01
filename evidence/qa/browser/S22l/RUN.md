# S22l Gate D retest on the fixed DEV build

Run S22l-orch248 (anthropic/claude-sonnet-5-5/medium, CODEX-2 lane), 2026-11-01 09:12Z to 09:26Z. Target https://web-dev-cd80.up.railway.app. Route: Playwright bundled Chromium, HEADED (headless is blocked by the Clerk bot challenge), fresh browser context and fresh Clerk test account per flow (alias s22l-<flow>-***, +clerk_test, code 424242, addresses not recorded). OWN05 uploaded with owner video elements hidden by CSS injected before the upload; stills contain no owner frames and no emails. Machine-readable record: [run.json](run.json). Script: [run.mjs](run.mjs) (stills named <flow>-*.png).

## Build observed
- API /version (https://api-dev-6091.up.railway.app/api/version): service api, revision e0213a0cdfe22c6939464df4aef0de1d28d96b5f = S15bf commit, an ancestor of main 7cd9481d (commits after it, incl. S15bg 36b73c0d, are not in that API revision; S15bg is a web change).
- Web build: no version endpoint on web (/api/version and /api/health return 404; HTML has no buildId). The controller states web af881dce; this run could NOT verify it. S15bg behaviour is verified by observation only (table below).
- Same-origin /api/workspace/version is 404 and /api/version is 404 on web.

## Verdict: Gate D streak on DEV: 3/3 PASS (3.1 to 3.8, 3.6 N/A), negative check PASS with one UX note, guest PASS, S15bg PASS. Not a judging-env result (S23 pending); scripted timings exclude human reading and typing.

## Per-flow record (UTC start/end from Date.toISOString, ms from a monotonic clock, home to Report body)
| Flow | Account | Job id | Start UTC | End UTC | Total | home | signup page | signed up | workspace | upload | interview ready | fit shown | report |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| f1 | s22l-f1-*** | job_273488660a53eb7693e9ea126bc13320 | 2026-11-01T09:23:06.665Z | 2026-11-01T09:23:27.679Z | 21.0 s | 2420 ms | 3470 ms | 9721 ms | 11730 ms | 12261 ms | 15311 ms | 17989 ms | 20795 ms |
| f2 | s22l-f2-*** | job_71fab684022fc18a861c0549af5b5150 | 2026-11-01T09:23:37.362Z | 2026-11-01T09:23:58.552Z | 21.2 s | 2789 ms | 3612 ms | 9781 ms | 11823 ms | 12243 ms | 15345 ms | 18120 ms | 21030 ms |
| f3 | s22l-f3-*** | job_0c7936ad6cbb04ca0e6754108f64b02c | 2026-11-01T09:24:05.546Z | 2026-11-01T09:24:26.772Z | 21.2 s | 2727 ms | 3559 ms | 9972 ms | 11988 ms | 12471 ms | 15662 ms | 18289 ms | 21060 ms |

## Protocol items per flow (PASS/FAIL derived from observed data, see run.json)
| Item | f1 | f2 | f3 | Evidence |
|---|---|---|---|---|
| 3.1 | PASS | PASS | PASS | sign-up with email + code 424242 reached, URL left /sign-up (step signed_up) |
| 3.2 | PASS | PASS | PASS | /workspace/<id> private workspace, empty state, header "Private workspace" ([f1-workspace.png](f1-workspace.png)) |
| 3.3 | PASS | PASS | PASS | upload POST/PUT/complete all 200; interview ready (no_textarea false) |
| 3.4 | PASS | PASS | PASS | chips shown (3 + Other) with free text, answer 20.28 cm, POST .../spec 200 with setup_validated false and label "user-declared, not verified" ([f1-question.png](f1-question.png)) |
| 3.5 | PASS | PASS | PASS | g = 8.62 ± 1.29 m/s² from fitter on RECORDED track ([f1-result.png](f1-result.png)) |
| 3.6 | N/A (not in signed-in UI) | N/A (not in signed-in UI) | N/A (not in signed-in UI) | not in signed-in UI (as S22j) |
| 3.7 | PASS | PASS | PASS | Report body contains the g line and caveats ([f1-report.png](f1-report.png), f1-report.txt) |
| 3.8 | PASS | PASS | PASS | total < 300 s (21.0 s, 21.2 s, 21.2 s scripted) |
| S15bg | PASS | PASS | PASS | role=alert empty before, after the probe and on Report; document.title "Real2Simulation" throughout; only aria-live polite regions with scene/upload placeholders |

## Per-flow details

### f1
- Result text: g = 8.62 ± 1.29 m/s²
- Chips: 1 the length recorded with this clip (owner-declared) ; 2 A four paper, short edge ; 3 Bank card, long edge
- Spec response: {"ok":true,"owner_clip":true,"spec":{"kind":"owner_clip_scale","object":"book cover horizontal edge 20.28 cm","length_m":0.2028,"unit":"m","label":"user-declared, not verified"},"setup_validated":false,"label":"scale user-declared, not verified; not setup-vali
- [role=alert] before/after/report: {"before":[],"after":[],"report":[]}; [aria-live] after: ["polite: ","polite: No scene yet. The viewport appears when an upload produces a scene."]
- document.title before/after/report: {"before":"Real2Simulation","after":"Real2Simulation","report":"Real2Simulation"}
- Console errors (redacted, 2): ["Failed to load resource: the server responded with a status of 404 ()","Failed to load resource: the server responded with a status of 404 ()"]
- Failed network requests (status, path only; 20): failed / x3; failed /lab x2; failed /ins_*/... x10; failed /sign-in x2; failed /library x2; failed /workspace x1

### f2
- Result text: g = 8.62 ± 1.29 m/s²
- Chips: 1 the length recorded with this clip (owner-declared) ; 2 A four paper, short edge ; 3 Bank card, long edge
- Spec response: {"ok":true,"owner_clip":true,"spec":{"kind":"owner_clip_scale","object":"book cover horizontal edge 20.28 cm","length_m":0.2028,"unit":"m","label":"user-declared, not verified"},"setup_validated":false,"label":"scale user-declared, not verified; not setup-vali
- [role=alert] before/after/report: {"before":[],"after":[],"report":[]}; [aria-live] after: ["polite: ","polite: No scene yet. The viewport appears when an upload produces a scene."]
- document.title before/after/report: {"before":"Real2Simulation","after":"Real2Simulation","report":"Real2Simulation"}
- Console errors (redacted, 2): ["Failed to load resource: the server responded with a status of 404 ()","Failed to load resource: the server responded with a status of 404 ()"]
- Failed network requests (status, path only; 20): failed /lab x2; failed /library x2; failed /sign-in x3; failed /ins_*/... x10; failed / x2; failed /workspace x1

### f3
- Result text: g = 8.62 ± 1.29 m/s²
- Chips: 1 the length recorded with this clip (owner-declared) ; 2 A four paper, short edge ; 3 Bank card, long edge
- Spec response: {"ok":true,"owner_clip":true,"spec":{"kind":"owner_clip_scale","object":"book cover horizontal edge 20.28 cm","length_m":0.2028,"unit":"m","label":"user-declared, not verified"},"setup_validated":false,"label":"scale user-declared, not verified; not setup-vali
- [role=alert] before/after/report: {"before":[],"after":[],"report":[]}; [aria-live] after: ["polite: ","polite: No scene yet. The viewport appears when an upload produces a scene."]
- document.title before/after/report: {"before":"Real2Simulation","after":"Real2Simulation","report":"Real2Simulation"}
- Console errors (redacted, 2): ["Failed to load resource: the server responded with a status of 404 ()","Failed to load resource: the server responded with a status of 404 ()"]
- Failed network requests (status, path only; 20): failed /library x5; failed /lab x3; failed / x2; failed /ins_*/... x7; failed /sign-up x1; failed /workspace x1; failed /workspace/dev-fixture-87625ea x1

Failed requests are client aborts (navigation prefetch of /, /library, /lab, /sign-in, /sign-up) plus third-party Clerk/Cloudflare probe URLs (paths shortened); no 4xx/5xx from /api/workspace in any streak flow. Console errors are Clerk CSP data: URL noise and styled-log fragments, none from app code.

## Negative check (neg flow, job job_a84a9f788b822b2676d86ff27e490653, 2026-11-01T09:22:14.776Z to 2026-11-01T09:22:42.891Z)
- Typed "0 cm": POST .../spec returned 422; alert text: "INVALID_INPUT: spec did not validate: known_size: length must be above 0 and at most 10 m" (plain, but prefixed with the code INVALID_INPUT:). PASS ([neg-after-invalid.png](neg-after-invalid.png)).
- The question panel then showed "All questions answered." with Back, and the card showed Retry; the textarea was NOT reopened automatically. Clicking Back reopened the textarea (result: Back -> textarea 1); re-answering "book cover horizontal edge 20.28 cm" without restarting gave 200 and g = 8.62 ± 1.29 m/s². PASS for S15bf (no restart), with UX note U1 below ([neg-reopened.png](neg-reopened.png)).

## Guest check (2026-11-01T09:12:42.622Z)
- /library: 18 cards, 2 playable, simulated-projectile-baseline-short opened inline; label "SIMULATED projectile: baseline-short (display-only)" and "Credit: SIMULATED · project-authored, no external footage."; Play button pressed; SVG frames differ across 1.5 s samples (frames_differ true). PASS ([guest-before.png](guest-before.png), [guest-playing.png](guest-playing.png)). Replay is a simulated side-view trace, not a 3D scene (scoped deviation per S22k F2).

## Conditions from S22k
- (1) S15bf chips + validated owner spec: chips shown, spec response validated server-side (setup_validated false by design, user-declared label). Observed MET.
- (2) S15bg announcer: no [role=alert] "Private development fixture" in any of 3 flows or the negative flow; MET by observation (web build SHA unverified).
- (3) S22l streak + guest + receipts: MET here (per-flow UTC, aliases, job ids, redacted console/network, API revision; web build not observable).
- (4) S23 judging approval: not part of this run; still open.

## Proposed fix rows (no product code changed)
- U1 (P3): after an invalid known-size answer the panel says "All questions answered." with no input; the user must find Back (or Retry). Proposed: reopen the textarea with the error beside it and keep Finish enabled.
- U2 (P3): validation alert is code-prefixed ("INVALID_INPUT: spec did not validate: known_size: ..."). Proposed: show the plain sentence, keep the code small.
- V1 (P3): expose the web build SHA (e.g. /api/version on web) so Gate D receipts can record it.
- Unchanged limits: headed Playwright route (not the in-app browser), Clerk test accounts only, OWN05 only, private clip stays private (stills hide frames).
