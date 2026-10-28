# S05b authorized RM02 probe preflight — 2026-10-28 UTC

Standing permission: canonical `evidence/owner/S05/GPU-AUTHORIZATION.md` and latest
DISPATCH supersede the older pending-Q8/no-GPU/no-private-transfer statements.
Input: the retained four RM02 Pexels PNGs; input.json hashes verified before RPC.
No personal files, other footage, public endpoint or source checkout upload.

## Live headroom / no-paid-overage execution guard

Authenticated Chrome Usage & billing, observed ~04:54 UTC:
`https://modal.com/settings/koushiksadhakjeet/usage` shows Starter, $130 credits,
total spend $0.00, billing cycle Oct1–31, $0 credits used/$0 charges, gross limit
$155, and `Set spend limit` (NO explicit net-spend cap configured). The old
$42.50 gross-limit receipt is superseded. No billing settings changed.

Existing Modal credentials are present by KEY NAME only. CLI initially lacked
environment credentials; native `uv run --env-file .env` supplies existing auth
to the client without displaying/persisting values or sending them to the job.
Authenticated `modal app list --json` returned `[]`; no concurrent app spend
observed. No coding quota check. Fresh $130 applicable headroom and remaining
owner-authorized $30 exceed the first-job conservative reservation **$0.95**.
This is a bounded-job credit-coverage guard, NOT a claim of an account-wide
zero-spend setting. Unrelated future jobs are not covered by this receipt.

## Resource and cost bounds

One ephemeral Modal Function, L4 x1; CPU request1/max2 physical cores; memory
request8192/max16384 MiB. max_containers1/min0/buffer0; single-use container;
retries0; startup90s/execution900s; scaledown2s; no schedules/endpoints/Volumes.
Dependency setup occurs INSIDE execution timeout (pip subprocess also480s),
not in an uncapped custom image build. Platform Debian/Python base only.
No auto-retry/additional job if it fails. Parent process/app stop verified after.

[Official pricing](https://modal.com/pricing): L4 $0.000222/s,
CPU $0.0000131/core/s, RAM $0.00000222/GiB/s. Conservative provisioned maximum
for startup+execution+idle: `(900+90+2)*(0.000222+2*0.0000131+16*0.00000222)`
= **$0.28145024**. Reserve $0.95 includes $0.66854976 contingency for platform
setup, CPU/base image handling and small result transfer. No persistent storage;
ephemeral model cache disappears with container. Invoice/billed time may lag;
measured function time is not billed time. Do not claim exact cost from this cap.

[Timeout semantics](https://modal.com/docs/guide/timeouts),
[CPU/RAM limits](https://modal.com/docs/guide/resources),
[ephemeral app lifecycle](https://modal.com/docs/guide/apps),
[billing latency](https://modal.com/docs/guide/billing) checked against installed
Modal1.6.3 public method signatures. No undocumented permission or retry flags.

## Runtime scope

MapAnything code3d10cf7, Apache weights00f9c24; explicit Apache model ID, no NC
default/SAM/optional external-model extras. Torch2.8.0/torchvision0.23.0 and
timm1.0.20; upstream required dependencies, no full reproducible dependency lock
or exhaustive licence audit claimed. DINOv2 backbone code can be torch-hub
resolved by upstream (not a separately approved NC checkpoint). Preserve limits.
Output is raw upstream arrays/schema/hashes, NOT converted scene contract,
metric calibration, planes, physical timebase or Gate R evidence.

Client corrections before GPU allocation: first appap-igwD6KCstyIBfyJztkbaK2
failed on cp1252 Rich Unicode output; explicit stop confirmed tasks0/stopped.
Second appap-EYAIngJi9igJVdZvVOt3JR rejected serialized Python3.11 vs image3.12
before Function creation; stopped/tasks0 verified. Client output set UTF-8 and
image aligned to Python3.11 (upstream supports>=3.10). These were client/setup
failures, not failed paid inference jobs; no automatic retry was configured.
Single actual remote-call app: ap-FivSp5aI1fHQKSGQQVYpde, created05:00:20Z.

## Outcome / reservation reconciliation

Remote setup failed before weights/inference: `numpy<2` conflicts with upstream
rerun-sdk0.24.1 requiringnumpy>=2. All3 apps stopped/tasks0, no containers remain
(`apps-stopped.json`, `containers-stopped.json`). No extra paid attempt.
Corrected NumPy2.2.6 and compiled96 Linux/Python3.11 dependency versions locally
in13.49s; corrected runner/lock NOT runtime-tested. GPU hardware query moved
before setup for future failure evidence; initial attempt did not measure VRAM.
Final UI05:05UTC shows $130 credits and rounded total/ephemeral spend$0.00.
Exact charged/billedGPU time unknown; reserve$0.95 until billing catches up.
App lifetime131s is NOT billed GPU time; do not report a zero charge as fact.
