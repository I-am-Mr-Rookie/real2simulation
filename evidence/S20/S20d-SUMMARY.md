# S20d — PASS: scoped SIMULATED cap regression

**No live provider/GPU/AWS calls, no spend, no measured prices or costs.**
Machine evidence: `S20d-regression.json`. Replay:
`python -B evidence/S20/simulated_cap_regression.py`.
Fresh guardrails suite: **93 tests OK** (91 existing + 2 new); replayed JSON bytes
match SHA256 `c800b8fc672a3020f80539659b3fd0f5f987be58c5d2a3e09c7d2a267dc619b2`.

- 35 deterministic events, including 20 expected nonretryable `SPEND_PAUSED`
  refusals; per-event SIMULATED bounds/final bills and projected liabilities logged.
  Event dollar fields are **not additive spend**.
- Global Meta: three scenes across fresh ledgers, two stages and synthetic linked
  worktree metadata reach $119.99999999. Candidates reaching/exceeding $120 refuse;
  $30.00000001 of the $150 envelope remains, preserving the $30 demo reserve.
- Modal: exact $5 monthly/credit floor admits; one quantum below refuses. $30 and
  above also refuse: the floor makes **$25 the effective monthly routine ceiling**.
  Global two-job/$1 envelope is shared by standalone and pipeline reservations;
  $1 exact admits, $1.00000001 refuses before a second job is accepted.
- Parent/child handoff consumes once without another row; replay refuses.
  Hash-bound SIMULATED settlement replaces $.50 liability with $.10 while keeping
  history; another $.40 scene can reuse the slot. Tampering and settlement replay
  refuse without journal mutation.
- All five real Modal local-entrypoint launch tails refuse before remote code
  while paused. No Modal import/remote execution was needed.
- `R2S_ENABLE_AWS` unset throughout; provider stays Modal with `launched=False`.
  Cap/floor/pause failures never activate AWS. Network/process/AWS-activation
  tripwires observed zero attempted calls.
- Existing public library DTO + synthetic manifest remain readable under cap,
  explicit pause and missing receipt (3 checks). This is **not HTTP/UI/playback**.

## Scope and residuals

This completes the controller's **S20d offline simulated-cap child contract**, not
live/account-wide enforcement or full runtime Gate C. ADMISSION.md still records
no upload HTTP route and no durable daily-user-quota integration; exhausted quota
is not claimed tested. Existing guardrails tests cover their offline upload-store
harness and library exemption. Controller must not erase these parent limitations.

R-C recheck2's four P3 residuals remain unchanged: operator-trusted settlement,
bearer reservation IDs, entrypoint-only guards (including two CPU launchers/direct
Modal CLI bypass), and fail-closed missing-worktree evidence. No policy expansion
or production fix was needed or made.
