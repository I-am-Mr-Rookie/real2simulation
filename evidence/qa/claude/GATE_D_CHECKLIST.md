# Gate D QA checklist — current product (S22a-orch127)

Written 2026-10-30 from main `67e299a` by S22a-orch127 (CLAUDE, Opus 5.5 medium assigned). Read-only source/receipt review;
**no check below was executed by this run.** Gate D is **NOT met / not assessed**. Supersedes the per-surface dependency
table of [GATE_D_PROTOCOL.md](GATE_D_PROTOCOL.md); that file's authority, fresh-account x3 (<5:00) rule and JSON evidence
format still apply.

## 0. Rules (apply to every check)

- **Written candidate-deploy approval from Koushik is still required before any judging traffic.** None is on record
  (STATE/QUEUE at 67e299a). Until it exists, run checks ONLY on Railway **dev** (owner-approved Oct27):
  web `https://web-dev-cd80.up.railway.app` (=WEB), api `https://api-dev-6091.up.railway.app` (=API). Dev results are
  **rehearsal evidence, never Gate D of record**. S22 deploys nothing; S23 deploys only after written go-ahead.
- Fresh accounts / terms acceptance need Koushik's written approval per account; otherwise mark the step `BLOCKED-BY owner-approval`.
  Never use a personal account or reuse one account as "fresh".
- Browser: signed-in ChatGPT in-app browser, not Chrome. Viewports 1280px and 375px. Secrets: key-name presence only;
  never capture env values, auth headers/cookies or provider dashboards.
- First record deployed SHA per service. If deployed SHA != main SHA under test, every result is tagged `STALE-DEPLOY`
  (rehearsal only); local-main facts below do not transfer to dev automatically.
- Evidence per check: JSON record (format in GATE_D_PROTOCOL.md) + screenshot(s) + HTTP status/content-type, under
  `evidence/qa/browser/<check-id>/` (S22b-i Owns). UTC timestamps.
- Pass/fail is binary per check. A missing required honesty label = **FAIL** even if the function works.
  Any number on screen not traceable to fitter/simulator output = **FAIL (P1)**.
- QA makes no new GPU/Meta/Baseten/Fireworks calls and no key/config edits unless the controller authorizes it.

## 1. Guest library (S18e-k) — Gate D (b)

Current-main facts: web `/library` (`Build/web/src/app/(public)/library/page.jsx`) still renders the static
"No demos are published yet" / "Viewer not connected" state. Guest data is served by the **Python API**
(`Build/library/guest.py`): `GET /api/library/manifest`, `GET /api/library/artifacts/<sha>`. S18k routed playable traces for
**projectile baseline** and **short small-angle pendulum** only; free-fall baseline withheld (shares Mystery-g answer record);
RM02/RM04 PLY, Apollo, bounce, RM05 and nine other cases **UNAVAILABLE**. S18g: all entries `canMount: false`.
**Expect L1/L4 to FAIL Gate D (b) until a web row wires /library to the guest API and a viewer can mount a trace.**

| ID | URL / steps | Expected | Evidence | Pass rule | Labels that must be visible |
|---|---|---|---|---|---|
| L1 | Logged out (fresh profile, no Clerk cookie): open WEB`/library` | 200, no sign-in redirect; lists published demos | screenshots 1280+375, status | PASS only if >=1 demo listed AND openable without login; static empty state = FAIL (b) | "Public · no account needed"; per item SIMULATED / SYNTHETIC (or measured class) |
| L2 | Logged out: `curl -i API/api/library/manifest` | 200 application/json; entries with sha256/bytes/href | body + status | 200, JSON parses, every playable href under `/api/library/artifacts/`; 404 = `NOT-DEPLOYED` FAIL | SIMULATED/SYNTHETIC, SCALE_UNVERIFIED where applicable |
| L3 | GET each manifest artifact href; sha256 the body | bytes and sha == declared | hash table | all match; any mismatch = FAIL P1 | — |
| L4 | Run projectile, then pendulum demo logged out (in /library viewer once wired) | trace plays; no GPU/model call | recording <=20s each + network log | plays AND zero calls to Modal/Meta/Baseten/Fireworks | "Simulated" trace label; no "measured"/"real-scene" wording |
| L5 | View UNAVAILABLE items (RM02, RM04, RM05, Apollo, bounce, free-fall baseline) | UNAVAILABLE with reason, or omitted | screenshot | no invented geometry/trace/viewer for any | "UNAVAILABLE" + reason |
| L6 | Mystery-g: page source, manifest, artifacts, network | metadata/challenge only | search result for answer field/value | answer absent from every guest response = PASS; present anywhere = FAIL P0 | "simulated challenge"; no answer |
| L7 | GET API`/api/library/artifacts/deadbeef` and a traversal id (`..%2Fmanifest.json`) | 404 `{"error":"artifact_not_found"}` | bodies | 404 both, no file contents/stack trace | — |

## 2. Private workspace (S04i) — owner only

Facts: `/workspace` and `/workspace/[sceneId]` mount S15 workspace only after Clerk session + owner policy; guests,
non-owners, malformed/unknown IDs and missing config deny uniformly with 404. S04i is local-only DONE; signed-in real-key
HTTP verification moved to S15k (not done). STATE records dev sign-in "unavailable".

| ID | URL / steps | Expected | Evidence | Pass rule | Labels |
|---|---|---|---|---|---|
| W1 | Logged out: WEB`/workspace`, `/workspace/<fixture-id>`, `/workspace/zzz` | identical 404 (no 401/403, no redirect) | status + body sha256 each | all identical = PASS; any difference = FAIL P1 (existence leak) | — |
| W2 | Signed in as approved non-owner test account | same 404 as W1 | as W1 | identical to W1; else FAIL P0 | `BLOCKED-BY owner-approval` if no account |
| W3 | Signed in as owner (Koushik runs or approves) | workspace renders fixture scene | screenshots 1280+375 | renders AND fixture labelled | "development fixture" / SYNTHETIC; never "your upload" |
| W4 | Fresh account upload -> report, 3 consecutive runs | each < 5:00 wall clock | stopwatch log + screenshots | GATE_D_PROTOCOL fresh-account rule; now `BLOCKED-BY S15k, owner-approval` | report labels per §4 |

## 3. Interview / Gate A (S14h)

Facts: `evidence/S14/GATE_A.json` verdict **MET_AMENDED_Q16**, label **"scale unverified, not setup-validated"**;
numeric 10/10, setup-validator 0/10; fallback is tool-only/templated.

| ID | Steps | Expected | Evidence | Pass rule | Labels |
|---|---|---|---|---|---|
| I1 | Wherever Gate A / interview status appears (UI, report, README, video script) | MET_AMENDED_Q16 with label | screenshot/quote | plain "MET", "validated" or "calibrated" anywhere = FAIL P1 | "scale unverified, not setup-validated" verbatim |
| I2 | Interview with model unavailable (owner/dev-config only; QA edits no keys) | tool-backed templated reply, non-empty | screenshot | no blank turn, no invented number | fallback / tool-only indicator |

## 4. Reports (S17f)

Facts: `Build/reports/checkpoint.py` renders checkpoint HTML and refuses labels other than MET_AMENDED_Q16; real scenes have
no fitter result (physics NOT_RUN), so RM02 is the "Fallback: input missing" page. Print path = browser "Save as PDF" from
HTML; **that PDF is untagged** (no accessibility structure) and must not be called accessible.

| ID | Steps | Expected | Evidence | Pass rule | Labels |
|---|---|---|---|---|---|
| R1 | Open checkpoint/report HTML (in-app link, or `evidence/S17/checkpoint/RM02-checkpoint.html` locally) | landmarks, skip link, scoped table headers | screenshot + keyboard pass notes | renders; keyboard reaches all regions | Gate A label verbatim; "Fallback: input missing" where no fitter result |
| R2 | Print -> Save as PDF | PDF saved; table headers repeat | PDF sha256 | opens; content matches HTML | any "accessible/tagged PDF" claim = FAIL; PDF described as untagged |
| R3 | Compare every report number to fitter/simulator JSON (`python -m tests.reports.run_diff`) | identical | diff output | 0 mismatches | measured vs simulated class per value |

## 5. Sidebar tools (S16)

Facts: Baseten `meta-models/muse-spark-open-1026`: **one** live HTTP 200 call (S16e; 1,176 provider-counted tokens; dollar cost UNKNOWN).
Fireworks: explicit-config fallback, **offline tests only**, no automatic switch. Meta Spark explicit config = refusal, not an adapter.

| ID | Steps | Expected | Evidence | Pass rule | Labels |
|---|---|---|---|---|---|
| T1 | Read all UI/README/demo text about sidebar search / open weights | matches facts above | screenshot/quote | "Fireworks live", known cost, multiple live calls or bonus claim = FAIL P1 | results SIMULATED / SCALE_UNVERIFIED; provider named |
| T2 | Sidebar search with provider unavailable (dev config, no QA key edits) | readable error naming selected provider; no automatic switch | screenshot | readable, no stack trace, no silent switch | — |
| T3 | Rerun `python -B -m unittest discover -s tests/sidebar-tools -t tests/sidebar-tools` (~52 s per S16h) | all OK, offline | log | all pass, zero network | — |

## 6. Spend guardrails (S20d)

Facts: 35 **simulated** events incl. 20 SPEND_PAUSED refusals; 93 guardrail tests; not full runtime Gate C (durable
daily-user quota/upload HTTP integration gap).

| ID | Steps | Expected | Evidence | Pass rule | Labels |
|---|---|---|---|---|---|
| G1 | `python -B -m unittest discover -s tests/guardrails -t tests/guardrails` on main under test | OK | log | all pass | — |
| G2 | Any UI spend/cap message | SPEND_PAUSED readable, nonretryable | screenshot | readable; no fake balance | "simulated cap"; never "live-verified" |
| G3 | Guest library session | zero spend events | network log | zero GPU/model calls | — |

## 7. PWA (S19)

Facts: manifest + service worker (scope `/`, cache `r2s-static-v1`) wired locally (S19d-wire); InstallGuidance not mounted;
manifest theme_color #155a92 vs layout #f3eee3; no real install prompt/device test; APK deferred; S19d PARTIAL.

| ID | Steps | Expected | Evidence | Pass rule | Labels |
|---|---|---|---|---|---|
| P1 | GET manifest link target and WEB`/pwa/sw.js` | 200; manifest+json; `Service-Worker-Allowed: /` | status + non-secret headers | both 200 with header | — |
| P2 | DevTools > Application: SW state, cache keys | static assets only | cache key list | any `/workspace`, `/api`, upload or authenticated URL cached = FAIL P0 | — |
| P3 | 375px: `/`, `/library`, `/lab`, `/workspace` (owner) | no horizontal scroll; usable tap targets | screenshots | no overflow | — |
| P4 | Install guidance / install claims | truthful Android/iOS steps; no orientation-lock claim | screenshot | truthful | "installable" only if a browser prompt was observed |

## 8. Decision record (S22f/j)

Gate D (a) needs W4 PASS x3; (b) needs L1+L2+L4 PASS logged out. Dev runs = rehearsal. Gate-of-record run needs Koushik's
written candidate-deploy approval + S23 deploy. If unmet at freeze: demo video uses the library path; uploads limited.

## Known blockers at 67e299a (expected FAILs, not checklist defects)

1. /library web page not wired to the guest API -> L1/L4 FAIL. 2. S15k signed-in dev verification not done -> W2-W4 blocked.
3. No owner candidate-deploy or fresh-account approval. 4. Dev deployed SHA unknown -> STALE-DEPLOY risk.
5. S19d PARTIAL; S20 runtime Gate C gap.
