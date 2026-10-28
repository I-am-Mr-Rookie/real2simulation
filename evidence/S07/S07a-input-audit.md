# S07a — input readiness, not a Gate M result

**PARTIAL. Literal acceptance remains unmet:** "Three Earth fall candidates
selected; scale and timebase uncertainty documented." The approved local set
contains **one** Earth-fall candidate (ST03), not three. None has a verified
independent metric scale AND capture timebase, and metric processing is not
approved. No g, residual, physical uncertainty interval or Gate M result exists.

Source snapshot / hashes: [S07a-candidates.json](S07a-candidates.json), generated
from canonical clips.csv and existing S02 audit, with local-path existence checks
only. No new footage acquisition, decoding or model processing. Scene approvals
were transcribed from `evidence/owner/S02/APPROVAL.md`, not stale CSV broad-use
flags; original CSV/audit/approval remain unchanged.

| Candidate | Existing/local evidence | Selection/uncertainty blocker |
|---|---|---|
| FF01 | Earth fall; local, 25/1 presentation FPS; same capture group as FF02 | NOT in ten-ID approval. Independent reference size absent; capture rate/edits unknown. Possible overlap with FF02, not two independent trials. No processing/selection for this run. |
| FF02 | Earth fall; local, 25/1 presentation FPS; same capture group as FF01 | NOT approved. Source height is inferred from fall time: circular scale, rejected. Uploader's corrected capture-rate statement remains unverified. No processing/selection. |
| FF03 | Manifest metadata only; no accepted local path | Rejected existing copy, time reversal/edit risk; no documented ball size or verified capture clock; NOT approved. Not revived from TEMP. |
| FF04 | Manifest metadata only; no accepted local path | Rejected existing copy, low resolution, cup dimensions unknown, slow-motion factor unknown; NOT approved. Not revived. |
| ST03 | Approved **local scene/tracking only**; local; pre-existing continuous fall review f58–76; 30000/1001 presentation FPS | Sole scoped tracking candidate. Apple width is assumed, not a known-size reference; repeated frames and capture/slow-motion factor unresolved. Metric use abstains. Existing review is not fresh tracking/scale verification. |

Raw local nominal Earth-fall files:3 (FF01, FF02, ST03). Scoped local Earth-fall
candidates:1 (ST03). Metric-selected/qualified trials:0. FF01/FF02 share a capture
group; independence unresolved. Do not conflate files, approvals, independent
trials or calibrated clips. Other ten-ID approvals cover rooms, projectile,
bounce and pendulum; RM05 is ISS. NASA swing/drop/impact N1–N3, projectile PJ03,
bounce BN01, pendulums, AP15 NOT_TRACKABLE and excluded ST05 cannot fill this gap.

## Input and uncertainty disposition

[Contract](../../Build/measurement/README.md) and validator require explicit
source hash, receipt references, scoped approval, coordinates/PTS, immutable
prefix/suffix split and non-circular scale/capture mapping. Unknown scale or
capture clock stays null and produces abstention. No arbitrary standard object
size, assumed g, delivered FPS or guessed slow-motion factor is substituted.
Uncertainty magnitudes remain **unknown**, not zero or invented percentages.
S07d owns propagation; current validator only checks declared prerequisites.

For ST03, a future authorized S07b may produce scene-only pixel tracks on the
reviewed segment with true frame PTS and explicit repeated-frame disposition.
Select and seal the prefix/suffix before fitting or calibration. No actual
split/track is generated here because the calibration/capture inputs are absent
and no tracking task was requested. ST03 cannot enter a metric fit under current
approval even if synthetic contract tests pass.

## Acceptance check (deliberately fails)

From this run worktree, after verifying receipt source hashes against canonical:

```powershell
python -c "import json,sys; d=json.load(open('evidence/S07/S07a-candidates.json')); n=len(d['scoped_local_fall_ids']); print(f'approved local Earth-fall candidates: {n}/3'); sys.exit(0 if n>=3 else 1)"
```

Expected/observed exit1,1/3. This is a snapshot check, not automatic future
approval discovery. Rebuild/review the snapshot against authoritative evidence
on any resumption. Exact three-candidate requirement is retained; no waiver,
fallback gate decision or parent completion is inferred.

## Next

Controller: retain PARTIAL and unmerged run/S07a under manual failed-acceptance
protocol. Existing contract/tests can be reviewed on that branch; do not mark
S07a DONE or silently unlock S07b/S07e. Any further acquisition/approval or
calibration work needs a separately authorized run. No new owner decision is
necessary merely to restate the existing shortage; Q8 remains untouched. Gate M
is NOT RUN (not a measured failure); table-plane fallback is not activated here.
