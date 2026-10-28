# S07b — real tracking adapter, explicit verification limits

Fresh CODEX-1 gpt-6.1-sol/medium <=30m, no new work after25m. Current S07a
implementation is merged/accepted; read canonical controls and acceptance receipt.
S07r removes only administrative three-input implementation block. No physical
gate/approval relaxation. S07c is independent mathematical fitter on frozen input.

Use isolated managed worktree, branch run/S07b. Owns ONLY:
Build/measurement/tracking.py; Build/measurement/TRACKING.md;
tests/measurement/test_tracking.py; evidence/S07/S07b/; Run-System/Runs/S07b/.
Read frozen inputs.py/README, do not edit them or any shared dependency/control
file. Questions/dependency changes via REPORT for controller; do not stop useful
independent work. Controller serializes controls/merges; leave commits UNMERGED.

Implement actual SAM3.1 adapter against current official documented interface,
not a dummy backend claimed to be SAM. Verify exact model/API/licence assumptions
from primary sources before choosing calls. Keep heavy model/provider execution
lazy/explicit; don't download weights/install huge models on low-memory PC.
Sanitize observed output into source-pixel frame/index/PTS and provenance using
S07a contract, preserve unknown physical scale/clock and immutable held-out split.
Handle missing detections, invalid/multiple outputs, time/frame mapping, malformed
or nonfinite/out-of-range values without fabricating tracks. Reuse project patterns.
Transport/model response fixtures can verify boundary behavior, NOT live SAM.
No fake implementation or fixture promoted to real tracking success. Record exact
unverified provider/runtime limits honestly; model integration may remain PARTIAL.

No private/clip upload, real model/API/GPU execution or new media processing in
this run. Owner receipt currently grants local scene/tracking, not blanket remote
or metric use. No secrets, accounts/terms/publication/purchases/deployment/provider
changes. Existing GPU permission not relevant here. Gate M NOT RUN/S12 locked.

Read/APPLY Ponytail full; applicable Superpowers TDD/debugging/verification and
task-relevant docs tools, no plugin name-dropping. Real red/green behavior tests,
fresh S07a regressions, strict scope/diff check. Existing inputs/code are NOT an
approval authority; preserve scientific eligibility checks. Report concrete skills,
checks/changes/limits and exact next action on disk. No quota polling or optional
chatter; one final status/absolute REPORT pointer. No subagents for this bounded task.
