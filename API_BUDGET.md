# Real2Simulation — API and compute budget

## Meta Model API usage — Nov 1 2026 (controller)
N01 hosted SAM 3.1 test: 4 calls x 90 video frames = 360 frames at $0.20/1k = ~$0.07 (usage.video_frames_processed;
price from Meta docs). 2 file uploads (no listed fee). Evidence: evidence/N01/SAM31-HOSTED-TEST.md.
Wave 1 (Nov 1 11:00-11:30Z): N02 sam-3.1 2 x 543 frames $0.2172; N05 muse-spark-1.3(+contributor) + voice ~$0.029;
N04 one Modal A10G warm-up ~$0.36 est (cost_log rates, not yet billed). Running Meta total today ~$0.32; Modal ~$0.36.
Wave 2 (11:45-12:00Z): N07 sam-3.1 543 frames $0.1086; N08 one Modal A10G reconstruct ~$0.35 est; N12 Muse Spark 12 turns + 1 muse-image ~$0.92 est.
Running today ~ Meta $1.35 est, Modal ~$0.71 est (not billed yet).
Wave 3 (12:30Z): N14 one Modal reconstruct ~$0.35 est + 2 sam-3.1 images $0.005. Running today ~ Meta $1.36, Modal ~$1.06 (est).
Product guard (owner Nov 1): global paid-call cap $10/day, $20/day Thu Nov 5 to Sun Nov 8; ledger every call.

## CURRENT — successor accepts unpaid evidence; no new paid reservation

S07b custody d58c7c9 and S05b diagnostic6 8fca36f accepted by scoped verified FF.
Fresh controller local custody/hash/tests only; no service/GPU/job/download.
Retain2.85 historical reservations under unchanged30 authority; exact charges
unknown. New S05b recovery7 guard and S07b recovery4 identity/readiness contracts
are LOCAL/READ-ONLY, NO paid work or model bytes. A local guard test is not
confirmed remote stop or renewed paid readiness. Existing safeguards unchanged.

## CURRENT — recovery5 stopped, CPU proof accepted — Oct28 12:56UTC

Accepted scoped evidence9b25fcc after fresh rebased spike7/scene11 PASS. Real CPU
imports PASS; subsequent single GPU RPC stayed pending with no observed allocation,
container, device/VRAM/runtime/output. Manually stopped12:51:08Z before remaining
session could fit full992s bound. Both apps stopped/tasks0; final containers[].
Cause UNKNOWN, not proven model or capacity failure; app588s lifetime NOT billed
GPU time. Function/startup limits do not bound queue wait; total queue+execution
needs an explicit manual/wall-clock guard for any future scoped continuation.

Retain full **$2.85** ($1.90 historical + $.95 new), exact billing unknown, no
reserve release or second paid attempt. Existing **$30** authority unchanged;
at most$27.15 before other debits. Reuse actual CPU receipt; no reinstall/retry
without changed prerequisite. GateR NOT_RUN/S05c locked. S07b recovery2 readiness
is accepted PARTIAL; recovery3 is local approved-input prefix custody only:
**no paid service/GPU jobs/spend**, no SAM downloads/terms or metric approval.
Older active/import-pending sections below are historical, superseded here.

## CURRENT — recovery5 CPU pass, ONE bounded GPU active — Oct28 12:42UTC

Current worker ledger reserves **new$0.95 all-in**, plus historical$1.90 pending,
**$2.85 total retained**; at most$27.15 of existing$30 before other debits. Exact
charges/billed seconds unknown, no reserve released. Authority is NOT the$130
dashboard balance. Parent authenticated credit receipt12:34 remains on disk.
Worker preflight observed apps/containers empty, verified all4 approved RM02
raw-frame hashes, and bounds one CPU then at most one L4 GPU, retries0, no custom
image build/persistent storage/endpoint/schedule. Pip/setup is inside hard limits;
compute bound$0.31737128 plus <=$.01 egress and$0.62262872 contingency within$.95.

Actual CPU imports PASS: Torch2.8.0+cu128/vision0.23.0+cu128/audio2.8.0+cu128,
NumPy2.2.6/MapAnything1.1.4; elapsed115.620071692s is NOT billed time. CPU app
ap-r3ct5JcmICM3MYJmqfsnPt stopped/tasks0, containers[]. Single GPU app
ap-7TvkSZJ4Wk6Ym0t0yZ3lsM now active; inference result/stop not yet accepted.
Follow worker evidence/S05/S05b/recovery5/{RUNTIME-PREFLIGHT.md,job-ledger.json};
controller will independently reconcile final report/stops before acceptance.
No account-wide cap, no-overage setting change or physical GateR success claimed.
Earlier stop/surface/import statements below are historical, superseded here.

## Latest S05b actual CPU attempt and stop — Oct28 ~08:25UTC

ONE bounded CPU preparation app ap-HXf8zry5uWtJx63efPpSdA ran08:20:46–08:20:58Z,
then explicit stop/tasks0 and containers[] verified. No GPU/model/media transfer.
pip failed before imports due worker-added wheel-only option excluding locked
source-only antlr4 runtime. Flag removed locally + regression; corrected remote
imports NOT retested. No paid retry. This supersedes browser-only launch blocker.

Old$0.95 PLUS new$0.95 reserves retained = **$1.90 pending**, leaving at most
**$28.10** of existing$30 before any other debits. Exact charge/billed time unknown;
12s app lifetime is NOT billed duration. Fresh active$100 grant supported bounded
coverage, NOT an account-wide cap. Full reservation/stop/cost assumptions:
evidence/S05/S05b/recovery3/job-ledger.json and RUNTIME-PREFLIGHT.md.
Controller accepted code/evidence by verified FF89e744c, fresh guard4/4+scene11/11
PASS. No actual installed runtime/inference/GateR. Owner requested STOP after
current batch: no further CPU/GPU job scheduled by this controller.

## Fresh controller credit receipt — Oct28 ~08:16UTC

Supported reconnected parent Chrome4 actually read authenticated usage AND
Credits: Active hackathon grant$100 remaining, expiryOct31,2027; total display
$130/monthly$30 separate; rounded spend$0/gross limit$155/Set spend limit.
No account cap/settings change. Fresh receipt: Runs/ORCH-20261028-HANDOFF/
MODAL-PREFLIGHT.md. Child lacks Chrome; trusted fresh controller evidence is
usable without redundant child-connector/consent gate. SAME recovery3 worker
continues remaining original timebox. Old$0.95 retained; no new job assumed.
Existing$30/new<=1 ALL-IN/resource/no-overage/stop safeguards unchanged.

## S05b recovery2 — Oct28 current controller receipt

Supported parent Chrome briefly reached authenticated billing: credits$130,
rounded spend$0, monthly$30, usage limit$155, no established net-spend cap.
Isolated worker browser operations then timed out; parent debugger detached.
No CPU/GPU/inference/model/media upload or new reservation. Retain historical
$0.95 until precise reconciliation; $29.05 before other debits is only budget
arithmetic, not live balance. Runtime/actual headroom/no-overage/stop-state not
proved by UI title or rounded zero. Q9 requests browser-control restoration,
NOT permission or credit redemption. No repeated identical worker dispatch.
Worker evidence: evidence/S05/S05b/recovery2/job-ledger.json and REPORT.

## Latest S05b continuation — 2026-10-28 05:23 UTC

Official torch2.8/vision0.23/audio2.8 pins corrected, resolver/config tests only.
Current billing verification failed browser-URL policy safety guard; native/browser
work stopped, no bypass. New CPU/GPU/Meta/inference jobs0, new reservation0; old
$0.95 retained pending exact reconciliation. Historical$130/stopped-app receipts
not refreshed. Installed imports/CUDA/HF, headroom and actual cost unverified.
No permission/credit redemption question; standing GPU scope unchanged. See
evidence/S05/S05b/dependency-continuation.json and latest S05b REPORT.

## Owner-validated GPU window — Oct28 scheduling authority

**Oct29 owner update (supersedes conflicting lines below):** monthly Modal $30 is
use-it-or-lose-it at month-end; front-load useful GPU jobs and size them from measured
probe cost to use remaining monthly credit by Oct31 (exact reset unverified). $100
grant persists. AWS quota owner-reported APPROVED; agents still need owner-created $50
EC2 alert plus agent AWS access before any launch. No overage/idle burn; ledger jobs.

Koushik confirms the current planning figures: **approximately20 GPU-hours
needed, approximately15 hours available in his current Modal allocation, and
reset on or after November1,2026**. These are owner-validated estimates, not
unverified guesses; use them as the planning baseline. Runtime can differ.

- Prioritize useful dependency-ready Modal GPU work **Oct28–31**, rather than
  deferring all GPU work until after November1. Plan to use up to the available
  current15h on justified jobs and roughly5h after the actual reset if needed.
  Do not idle/burn compute to hit20h or treat20h as a measured requirement.
- Start prerequisite/account/runtime preparation now. S06p is a bounded,
  read-only readiness run independent of footage approval; actual product jobs
  retain S02e input approval, model/weight licences, memory and job dependencies.
- Before live jobs, verify the existing account's allocation units/GPU class,
  remaining operational allowance, reset timestamp/timezone if exposed and
  projected job cost against existing authorised credit/spend limits. This is
  execution bookkeeping, not a demand to re-prove Koushik's planning estimate.
  Reconcile the older $30 authorised spend ceiling with the now-visible $130
  credit balance (receipt below); credited balance alone is not a spending increase. No paid overage,
  purchases, new accounts, terms acceptance or billing changes are authorised.
- Do not assume a reset at November1 midnight. Record actual refresh evidence;
  if later, use the remaining window before Nov4 18:00 Asia/Dhaka. Checkpoint
  useful completed outputs so the reset is not a reason to rerun paid work.
- Ledger every job: GPU type/count, UTC start/end, GPU-seconds/hours including
  multiplicity and billed runtime, remaining allocation, output/revision and
  actual/estimated cost. Shut down idle resources. AWS approval gates unchanged.

### S06p readiness receipt — Oct28

**Later Chrome inspection supersedes the signed-out limitation below.**
Authenticated pre-redemption snapshot: Starter$30/month, remaining$30,
spent$0, Oct1–31 billing cycle, gross usage limit$42.50, no explicit net spend
limit shown (`Set spend limit`). GPU concurrency10/current0 is not an hours
allowance. Exact reset timezone/GPU-class availability not established.
No settings changed; Chrome closed normally and closure verified.
[Sanitized controller receipt](Run-System/Runs/ORCH-MODAL-CHECK/REPORT.md).
**Post-redemption evidence supplied by Koushik (Oct28):** the submitted form
shows processing confirmation; the separate Modal Credits dashboard screenshot
confirms **$130 total credit**, $30/month included and **$100 additional credit
remaining across one Active grant**, note `Meta Global AI Developer Hackathon`.
Grant activated **Oct27,2026**, expires **Oct31,2027**. Redemption is no longer
pending. Evidence basis: owner-provided dashboard screenshot, not a new live
browser check; no screenshot/code/email copied into Git. Current usage limits,
spend guards and GPU class were not rechecked by these images.

Distinguish the monthly allocation/reset from this long-lived grant: the
$100 grant does NOT expire at the coming Nov1 reset. Preserve Koushik's useful
pre-reset GPU priority and owner-validated20h/15h baseline; do not convert the
dollars to GPU-hours or burn credit from an assumed grant expiry. Existing
authorised spend ceiling/no-overage and input/runtime/licence gates remain.

Readiness DONE, not GPU/account verification. [Evidence and schedule](evidence/S06/pre-reset/READINESS.md), [report](evidence/S06/pre-reset/REPORT.md). Supported browser reaches signed-out Modal login; current allowance units/class/credits, gross usage cap, net spend limit and reset/timezone are not exposed. Owner baseline ~20h/~15h/reset on-or-afterNov1 remains authoritative. Q5 in STATE requests sanitized execution bookkeeping only. No credentials retrieved, GPU jobs/uploads/inference or billing changes.

Keep older$30 authorized Modal ceiling until reconciled;15h does not authorize any GPU class or paid overage. Gross usage and net out-of-pocket limits differ; public pricing is not credited balance. Future jobs need worst-case cost reservation including non-GPU charges within verified applicable credits AND usage headroom AND existing unspent authorization, plus no-paid-overage assurance. Below$5 pause new uploads while AWS pending. No automatic cap increase at reset. Useful eligible S05→S06→S13 work takes priority Oct28–31; remainder only after observed refresh, reusing completed outputs. S02e/licence/runtime/AWS gates remain. Coding quota: OpenCodex-managed; not polled; task tokens/dollars unknown; service job spend$0.

## Meta credit policy

**Owner update Oct29 ~19:10 Dhaka:** dev.meta.ai billing shows "Free credits in use",
balance **$149.92**; no top-up. Owner: the 4-call S14b event is not a problem; ~$150 is
enough if the process is frugal. Live Meta calls are UNBLOCKED for dependency-ready
runs under frugal limits: per-run cap set in the contract, ledger every call, and the
existing $120 routine hard stop + $30 demo reserve remain. Balance is owner-reported.

**Oct29 controller breach (recorded):** S14b-orch16 made 4 live muse-wonder-1.0 calls
(+1 free GET /v1/models) 11:3x-11:4xZ under a controller contract cap <=$1, while this
policy still required known billing. Est $0.114 (list $4/$20 per Mtok x1.5), billed
unknown. Per-call JSONL ledger: evidence/S14/ (S14b-orch16). Live Meta calls stay blocked
until Koushik supplies sanitized balance/usage.

| Item | Value / evidence |
|---|---|
| Promotional allocation | $150; owner reports billing complete, actual balance not independently verified |
| Routine cumulative hard stop | $120, including historical usage, in-flight reservations and conservative unbilled estimates |
| Final-demo reserve | $30; unavailable to routine work; demo use must be explicitly identified and authorized |
| Confirmed spend during preflight/S03 | $0 — no Meta/service inference or GPU calls made; coding-subscription CLI smoke is separate |
| Historical spend | Unknown; owner reports prior successful 44-token Meta test, exact price/billed amount not supplied |
| Verified available balance | Unknown; never infer $150 remaining from allocation |
| Routine headroom | Unknown until historical/billing reconciliation; no live dispatch today |
| Enforcement today | Written control policy only; no runtime cap exists because product implementation is forbidden |

Before any future LIVE_SMOKE, obtain sanitized balance/usage evidence, reconcile historical spend, estimate worst-case request cost and reserve it atomically in the ledger. Do not launch if cumulative spend + pending reservations + projected request cost reaches/exceeds $120, if billing is unknown, or if credit is insufficient. Pause routine requests at the threshold; never let a billing alert substitute for code enforcement. No top-ups, purchases or automatic overage approval. Gate C later proves runtime enforcement; NOT implemented in S03.

Log every provider call with UTC, task/RID, provider, exact model, protocol, input/output/reasoning tokens, GPU seconds where relevant, price source/date, estimated cost, billed cost, reservation, cumulative spend and evidence. Unknown prices/costs remain unknown and block budget-dependent requests; do not copy the legacy Merge Gateway rates or $8/$2 caps.

| UTC | Task/RID | Provider/model | Usage | Estimated USD | Billed USD | Evidence/status |
|---|---|---|---|---:|---:|---|
| 2026-10-27 (earlier, owner-reported) | pre-existing test | Meta muse-spark-1.3 | 44 tokens reported; split unknown | unknown | unknown | Owner reports HTTP200/pong; not independently repeated |
| 2026-10-27 | preflight/S03 | none | no Meta/service model or GPU calls | 0 | 0 | Local file reads, Git and quota inspection; harmless coding-subscription smoke tracked separately below |

## Other resources (not Meta balance)

| Resource | Planning baseline only | Permission / operational rule |
|---|---|---|
| Modal | Owner dashboard screenshot confirms $130 total: monthly$30 plus Active hackathon grant$100, expires Oct31,2027 | Existing$30 authorised spend ceiling unchanged by balance evidence; GPU/inference and no-overage guard unverified; reserve job costs against applicable credits, headroom and authorization; pause new uploads below $5 while AWS pending |
| Baseten | Guide offers $100; credited balance unverified | Spark Open primary, exact model ID meta-models/muse-spark-open-1026; verify at S16 |
| Fireworks | Plan says $80; guide offer $25 does not establish account balance | Fallback only; prior model listing is auth evidence, not inference |
| AWS | $176.27 remaining reported in earlier notes, not current verified balance | Spot only (8 vCPU verified Oct29; on-demand 0 pending); $50 EC2 budget alert verified; us-east-2 only; spot batch, stop after session |
| Kaggle | Plan baseline 30h/week, actual quota unverified | No account/terms acceptance; check memory/licences before spikes |
| Railway | Existing Pro account reported | Dev deploys approved for future steps; judging/other environments separately gated |

## Day-1 coding quota calibration (not API-credit spend)

Koushik's Oct28 correction: OpenCodex manages coding-subscription usage/allowance. Do not poll quota before/after, require reset snapshots or pause at percentages; record `OpenCodex-managed; not polled`. Historical snapshots below are receipts only, not current dispatch gates. Keep one row/task/lane with planned versus observable actual model/effort, tokens, elapsed minutes, dollar estimate and evidence; unavailable is not zero. Subscription use is not Meta API spend; API/AWS limits remain unchanged. On Oct29 compare observable task cost with plan L31; >2x difference triggers a logged routing proposal, not automatic cross-lane reassignment. Sol xhigh escalations and any approved Astra use are separately counted.

| Task | Planned lane/model | Actual model | Tokens | Codex 5h / weekly snapshot | Claude quota | Cost attribution |
|---|---|---|---|---|---|---|
| S03a/S03b | CODEX-1 / Sol medium | Current chat; exact runtime model not exposed by tools | unavailable | Before final verification: used37% /44%; remaining63% /56%, shared account, not lane-specific | unavailable | Per-task delta/dollars unavailable; no inference spend |
| S05a | CODEX-1 / Sol medium | Manual Codex chat; exact runtime model/effort unavailable | unavailable | Before/after used67% /49%; remaining33% /51%; shared-account snapshot, no per-task attribution; primary reset1793132283 | unavailable | Subscription task cost unknown; $0 Meta/service inference and GPU spend; public licence metadata/text reads only |
| S08a | CODEX-1 / Sol medium | Manual Codex chat; exact runtime model/effort unavailable | unavailable | Before/after used67% /49%; remaining33% /51%; shared-account snapshot, no per-task attribution; primary reset1793132283 | unavailable | Subscription task dollars unknown; $0 Meta/service/GPU spend; offline schema work only |
| S02a | CODEX-2 / Terra high | Manual Codex chat; exact runtime model/effort unavailable | unavailable | Before/after used67% /49%; remaining33% /51%; shared-account snapshot, no per-task attribution; primary reset1793132283 | unavailable | Subscription task dollars unknown; $0 Meta/service inference/GPU spend; public source reads/browser previews only |
| S08b | CODEX-1 / Sol medium | Manual Codex chat; exact runtime model/effort unavailable | unavailable | Before/after used67% /49%; remaining33% /51%; shared-account snapshot, no per-task attribution; primary reset1793132283 | unavailable | Subscription task dollars unknown; $0 Meta/service/GPU spend; offline validator only |
| S08c | CODEX-1 / Sol medium | Delegated fresh Codex session; exact runtime model/effort unavailable | unavailable | Initial numeric receipt unavailable; observed used70% /50%, remaining30% /50%; shared account, not task attribution; primary reset1793132283 | unavailable | Subscription task dollars unknown; $0 Meta/service/GPU spend; offline geometry/stability preflight |

| S08d | CODEX-1 / Sol medium | Delegated fresh Codex session; exact runtime model/effort unavailable | unavailable | Before/after used70% /50%, remaining30% /50%; shared account, not task attribution; primary reset1793132283 | unavailable | Subscription task dollars unknown; $0 Meta/service/GPU spend; offline template/oracle |

After each future run update this table and STATE. Never change account models, providers, credentials or permission settings merely to match a plan label.

## S03 CLI smoke calibration (coding subscription, not Meta credit)

| Probe | Requested actual CLI route | Observed input / cached / output tokens | Outcome |
|---|---|---|---|
| Initial write-marker smoke | gpt-6.1-sol / medium | 33108 /23680 /149 | Exit0 but marker absent; not accepted; existing read-only policy found |
| Read-only smoke | gpt-6.1-sol / medium | 31949 /23040 /57 | Marker-read sentinel verified; DONE in24.316s |
| Consolidation/short-prompt tests | offline Python fixtures | no coding-model calls |16 deterministic tests pass; real product dispatch disabled |

Earlier receipts are retained under ignored Run-System/Runs; paths in chronological receipts name the location at run time, not an active checkout. Current operational root is the event folder and worktrees are .worktrees/. Shared Codex snapshot after the prior smoke: used52%/5h and47%/weekly, versus37%/44% at preflight. This includes other shared activity and is not a per-task cost attribution. Claude quota/dollars remain unavailable; no Claude inference was performed. No additional Meta, Modal, AWS, Baseten or Fireworks call was made by S03.

## S04a coding quota receipt

| Task | Planned route | Actual route/effort | Tokens / task USD | Before / after shared Codex used | Meta/service/GPU |
|---|---|---|---|---|---|
| S04a | CODEX-2 GPT-6.1 Sol medium | Delegated fresh Codex session; exact runtime identity/effort unavailable | unavailable / unknown | 70%5h,50%weekly /70%5h,50%weekly; reset1793132283; not task attribution | $0 new calls; historical Meta balance still unknown |

## S08e coding quota receipt

| Task | Planned route | Actual route/effort | Tokens / task USD | Before / after shared Codex used | Meta/service/GPU |
|---|---|---|---|---|---|
| S08e | CODEX-1 GPT-6.1 Sol medium | Delegated Codex session; exact runtime identity/effort unavailable | unavailable / unknown | 70%5h,50%weekly /70%5h,50%weekly; reset1793132283; not task attribution | $0 new calls; historical Meta balance still unknown |

## S02c coding quota receipt

| Task | Planned route | Actual route/effort | Tokens / task USD | Before / after shared Codex used | Meta/service/GPU |
|---|---|---|---|---|---|
| S02c | CODEX-2 GPT-6.1 Terra high | Delegated Codex session; exact runtime identity/effort unavailable | unavailable / unknown | 70%5h,50%weekly /70%5h,50%weekly; reset1793132283; not task attribution | $0 new calls; historical Meta balance still unknown |

## S08f coding quota receipt

| Task | Planned route | Actual route/effort | Tokens / task USD | Before / after shared Codex used | Meta/service/GPU |
|---|---|---|---|---|---|
| S08f | CODEX-1 GPT-6.1 Sol medium | Delegated Codex session; exact runtime identity/effort unavailable | unavailable / unknown | 70%5h,50%weekly /70%5h,50%weekly; reset1793132283; not task attribution | $0 new calls; historical Meta balance still unknown |

## S08g coding quota receipt

| Task | Planned route | Actual route/effort | Tokens / task USD | Before / after shared Codex used | Meta/service/GPU |
|---|---|---|---|---|---|
| S08g | CODEX-1 GPT-6.1 Sol medium | Delegated Codex session; exact runtime identity/effort unavailable | unavailable / unknown | 70%5h,50%weekly /70%5h,50%weekly; reset1793132283; not task attribution | $0 new calls; historical Meta balance still unknown |

## S08h coding quota receipt

| Task | Planned route | Actual route/effort | Tokens / task USD | Before / after shared Codex used | Meta/service/GPU |
|---|---|---|---|---|---|
| S08h | CODEX-1 GPT-6.1 Sol medium | Delegated Codex session; exact runtime identity/effort unavailable | unavailable / unknown | 70%5h,50%weekly /70%5h,50%weekly; reset1793132283; not task attribution | $0 new calls; historical Meta balance still unknown |

## S04d coding quota receipt

- Requested CODEX-2 GPT-6.1 Sol medium; actual delegated Codex, exact runtime
  model/effort unavailable. Tokens/coding cost unknown.
- Shared quota before70%5h/50%weekly; after snapshot19:28UTC83%5h/52%weekly,
  reset1793132283. Not attributable solely to this run; no reset or purchase.
- Meta/service-inference/GPU$0; synthetic Clerk SDK diagnostics only, no real
  sign-in/session. Historical Meta spend/balance remains unknown.

## S04e coding allowance / cost receipt

- Requested CODEX-2 GPT-6.1 Sol medium; actual delegated Codex session, exact model/effort unavailable. Tokens/coding cost unknown; approximately5.4 minutes.
- **OpenCodex-managed; not polled**. No quota snapshots, resets, purchases or policy/routing changes.
- Meta/service-inference/GPU $0 new calls. Local FastAPI/Uvicorn HTTP and regression tests only; historical Meta spend/balance still unknown. Evidence: Run-System/Runs/S04e/REPORT.md.

## S04f coding allowance / resource receipt

- Requested CODEX-2 GPT-6.1 Sol medium; actual delegated Codex identity/effort,
  observable tokens and coding dollars unavailable. OpenCodex-managed; not polled.
- Meta/service-inference/GPU $0 new calls; historical balance remains unknown.
- Railway dev Postgres/Redis and private bucket provisioned under existing dev
  approval; normal ongoing resource charges/balance unmeasured and unknown, NOT
  $0. No purchases, upgrades, accounts, terms or alternate environments.
- Pinned health-only dependencies installed in disposable isolated venv; no
  global Python/runtime/model/provider/credential changes. Receipt S04f/REPORT.md.

## S04g deployment checkpoint — Oct28 Dhaka

- Dev-only Docker builds and live read-only dependency checks; Meta/service-inference/GPU0 new calls. Historical balances unknown. Railway build/runtime/storage charges ongoing, unmeasured and not zero. No purchases/upgrades.
- Requested CODEX-2 Sol medium; actual delegated Codex exact model/effort/tokens/task dollars unavailable. OpenCodex-managed; not polled. Isolated pinned health runtime, no global runtime changes. Evidence Run-System/Runs/S04g/REPORT.md.

## F-CODEX-1-1 review receipt — Oct28 Dhaka

- Requested CODEX-1 GPT-6.1 Sol medium; actual delegated Codex exact model/effort/tokens/task dollars unavailable. OpenCodex-managed; not polled.
- Local read-only owned-module analysis and synthetic checks only; new Meta/service-inference/GPU calls0. Historical spend/balance and ongoing infrastructure charges not reverified. No purchase/deployment/settings/approval changes.
- Evidence: evidence/fillers/CODEX-1/1/REPORT.md; no simulator/gate success claimed.

## S05b local-preparation receipt — Oct28 Dhaka

- Requested CODEX-1 GPT-6.1 Sol/medium; actual delegated Codex identity/effort,
  tokens and coding dollars unobservable. OpenCodex-managed; not polled.
- Meta/service/GPU calls0, new job spend0. Only local frame decode and public
  pinned package/model metadata reads; no weights, installs, uploads or GPU.
- $130 owner credit receipt and existing $30 ceiling/no-overage unchanged;
  historical balances/ongoing infrastructure charges not freshly verified.
  Q8 recommended A is APPROVED. Owner then clarified pre-reset direction already
  authorized useful dependency-ready Modal jobs within existing$30 budget;
  no redundant per-job approval. First RM02 probe <=$1 conservative all-in reserve;
  verify headroom/no-paid-overage and stop resources. No launch yet claimed.

## Standing GPU execution authorization — owner correction Oct28

**Latest parent receipt12:34UTC:** controller supported authenticated Usage/Credits restored:
130 total/Active100 grant plus monthly30, rounded0.00 spend, no configured cap
asserted. Historical1.90 retained pending exact billing; authority stays30 and new
reserve<=1 all-in. Recovery5 checks current resources/bounds/raw input/imports
before any GPU. Current recovery5 jobs/reservation are recorded at the top;
this parent receipt predates them. Supersedes disabled-surface note.

**Latest recovery4:** supported local browser use disabled in Work settings;
no new CPU/GPU/build/inference/upload job or reservation. Historical$1.90 retained
pending exact billing; current global resources/headroom not refreshed. Corrected
installed imports untested. Q10 concerns execution visibility, NOT GPU/credit
approval. No identical retry until genuinely changed state.

Run useful ready Modal GPU work before the monthly$30 allocation resets Nov1;
do not defer everything or ask per-job permission within existing$30 authority,
approved licensed inputs and established safeguards. Prior Q8 approval waiting
was redundant. $100 grant/$130 balance already confirmed; grant expires2027,
not this coming monthly reset. Do not treat credited balance as spend expansion.
First RM02 probe reserve <=$1 including setup/CPU/storage; all jobs require
conservative reservations, current applicable headroom, bounded resources,
no-paid-overage safeguards and verified stop. No waste merely to consume credits.
No purchases/accounts/terms/billing changes/AWS/public uploads or calibrated-gate
claims. Read evidence/owner/S05/GPU-AUTHORIZATION.md; actual blocked safeguards
may stop launch, but do not re-ask answered GPU permission or credit redemption.
- S05b latest supported-browser recovery: `Browser is not available: chrome`; no verified current headroom, CPU/GPU launch or new reservation. Historical$0.95 retained (at most$29.05 of existing$30 before other debits); exact charge unknown. No account cap or fresh resource-stop receipt asserted. Restore provider availability before redispatch; no alternate route/retry/permission question. See evidence/S05/S05b/BROWSER-RECOVERY-20261028.md.
- S05b Oct28 authorized attempt: one private remote RM02 setup invocation; dependency resolver failed before weights/inference. All3 initialization/attempt apps stopped/tasks0; containers[]. **$0.95 reservation retained** pending billing reconciliation; exact charge/billedGPU-seconds unknown (final UI rounds spend$0.00, not proof of zero cost). Preflight$130 credits/$0 spent, no configured net-spend cap; bounded-job coverage guard, NOT an account-wide cap. Corrected NumPy2.2.6/Linux-Python3.11 lock resolves locally, not runtime-tested. No extra paid retry. Ledger: evidence/S05/S05b/job-ledger.json; report Run-System/Runs/S05b/REPORT.md. Standing useful-job permission remains answered; no re-redemption or per-job approval.
