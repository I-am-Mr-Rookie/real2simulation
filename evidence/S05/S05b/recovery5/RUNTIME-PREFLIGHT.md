# Recovery5 preflight / reservation BEFORE paid action

2026-10-28 12:38 UTC. Trusted authenticated controller receipt at
Run-System/Runs/ORCH-20261028-SOL/MODAL-PREFLIGHT-1234.md (12:32–12:34 UTC)
shows total $130 and active grant $100 remaining. Rounded spend $0.00 is NOT
an exact invoice. Existing authority stays $30; historical $1.90 reserved.
Fresh own normal authenticated Modal1.6.3 app/container lists both [] (retained).
No concurrent resource work observed, no other new debit reported by controls.

NEW all-in reservation $0.95 recorded in job-ledger.json BEFORE CPU execution.
Total retained $2.85; $27.15 authority before other debits. Even disregarding
monthly credits, $100 grant minus $2.85 is $97.15 conservative coverage.
This is bounded-job/no-paid-overage credit coverage, NOT account-wide cap proof.
No billing/account/terms/policy changes. No child browser/consent loop.

Fresh official https://modal.com/pricing confirms L4 .000222/s,
CPU .0000131/core/s, memory .00000222/GiB/s and egress .04/GiB.
https://modal.com/docs/guide/timeouts separates startup/execution timeouts;
https://modal.com/docs/guide/resources documents requested limits.
CPU max2 cores/16GiB, 60+520+2=582s: $0.03592104.
GPU max1 L4/2cores/16GiB, 90+900+2=992s: $0.28145024.
Both compute bounds total $0.31737128; capped <=256MiB GPU return egress <=$.01.
Remaining $.62262872 contingency covers standard base-image/CPU setup and tiny
control/CPU-result transfer. No custom image build, persistent storage, Volume,
snapshot, endpoint, schedule, extra disk or unbounded background service.
Pip/setup is INSIDE hard execution bounds; CPU pip450s/import60s; GPU pip480s.
Exactly one CPU attempt, then at most one GPU only AFTER actual imports PASS.
Retries0, min0/max1/buffer0, single-use, scaledown2, stages serialized.
Explicit app.stop() finally and fresh resource check mandatory on every outcome.
Timebox stop13:04Z; do not start GPU unless bounded completion fits.

Read-only installed cached uv/Python3.11 route reused. Long --env-file path hit
known wrapper argv splitting, then backslashes were stripped; no authentication
attempt/job resulted. Standard Windows short-path resolution + forward slashes
lets uv read canonical existing .env normally without agent reading/copying values.
No credential/provider change, injection into job, UI fallback or bypass.
Four original approved RM02 PNGs individually hash/size verified BEFORE copy,
recovered ONLY into recovery5/local/, reverified4/4; directory ignored explicitly.
Manifest/lock unchanged. No other footage, personal/archive files or public upload.

12:41UTC: real CPU imports PASS: Torch2.8.0+cu128, vision0.23.0+cu128,
audio2.8.0+cu128, NumPy2.2.6, MapAnything1.1.4. Actual function115.620071692s,
NOT billed time. CPU app ap-r3ct5JcmICM3MYJmqfsnPt stopped/tasks0, containers[].
No concurrency/debit outside own reserved job observed. Existing .95 all-in
reservation covers next SINGLE GPU attempt, not a second reservation/consent.
992s bound fits deadline13:04 with >6m closeout margin at12:41.

Final12:51UTC: app remained ephemeral/tasks0, containers[] on multiple fresh
checks, with no allocated_gpu/startup/pip/inference log. Queue/wait time is outside
the startup/execution bound; the remaining session ceased to fit the full992s
bound. Manual stop initiated12:50:23Z, confirmed stopped12:51:08Z/tasks0,
containers[]; original runner's finally-stop also completed. One plain CLI stop
aborted at its normal confirmation (no state change); inspected supported help,
then used documented --yes for this explicitly required own-app stop (exit0).
No second job, GPU/lane change or retry. Client exited1 with RemoteError after
the external stop; no provider capacity/compatibility diagnosis is established.
No GPU model/VRAM/runtime/output obtained. Keep full$.95 plus old$1.90 pending
exact billing; app lifetime588s is NOT GPU/billed time or proof of zero charge.
