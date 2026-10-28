# S05b-recovery10 — local F3 repair

Owner directly requests this chat be the sole serial worker until22:30 BDT.
No new session/delegation, provider change, remote operation or paid probe.
Requested lane CODEX-1 Sol/medium; actual runtime/effort not independently exposed.
Parent project/root inherited from this existing project chat; no launcher binding invented.

Issued2026-10-28T15:56:13Z; deadline16:26:13Z=22:26:13BDT;
minute25 implementation cutoff16:21:13Z. Overall owner stop16:30:00Z.
Use available time for unfinished criteria; no early incomplete terminal except
owner/safety stop. Verified complete child may end early; parent stays PARTIAL.

Objective: eliminate relative child-clock restart and preserve received payload
atomically BEFORE potentially blocking cleanup, without treating saved bytes as success.
Owns: Build/reconstruction/spike/{rm02_deadline.py,rm02_watchdog.py,modal_rm02.py,
test_rm02_deadline.py,test_rm02_watchdog.py,test_modal_rm02.py,README.md}; minimal new local
result helper/test in same directory if necessary; evidence/S05/S05b/recovery10/;
Run-System/Runs/S05b-recovery10/. Canonical control updates serialized by this chat.

Acceptance:
1. Parent passes absolute monotonic deadline; child startup/preflight consumes it;
   output margin reserved; expired/invalid deadline never starts remote setup.
2. Received bytes + pending receipt persisted atomically before cleanup; late/hung
   cleanup retains artifacts but fails closed. Persistence errors still trigger stop.
3. Fresh offline tests on available3.14 and3.11, bounded subprocesses; source audit,
   timing receipt, local report/commit and verified FF; no remote readiness claim.

Ponytail full: reuse existing atomic_json, fake APIs, deadline/CLI seams, stdlib.
No dependency addition, generic framework, provider imports or paid work.
